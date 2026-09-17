"""
python/scripts/plot_early_prediction.py

Plot how predictive accuracy (R²) accumulates as more of the B&B search
trajectory is observed. Uses bb_snapshots.csv where snapshot_fraction ∈
{0.01, 0.05, 0.10, 0.25, 0.50, 1.00}.

Output: results/revision-2/early-prediction/early_prediction_curves.png
        results/revision-2/early-prediction/early_prediction_data.csv
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modeling.config import GROUP_A_INSTANCE_CHARACTERISTICS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "data" / "instrumentation"
RESULTS_DIR = BASE_DIR.parent / "results" / "revision-2" / "early-prediction"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Execution metric columns in bb_snapshots.csv (exclude structural columns)
EXEC_COLS = [
    "nodes_generated", "nodes_explored", "leaf_nodes", "internal_nodes",
    "max_depth", "mean_depth", "median_depth", "max_queue_size",
    "mean_queue_size", "final_queue_size", "mean_bound", "bound_variance",
    "mean_bound_gap", "bound_gap_variance", "pruned_by_bound",
    "left_branches", "right_branches", "explored_children",
    "improvement_count", "sum_improvement_amount", "mean_improvement_amount",
    "first_improvement_node", "explored_generated_ratio",
    "pruned_generated_ratio", "avg_branching_factor",
]

TARGET_COL = "log_nodes_explored"


def compute_r2_at_fraction(snap_df: pd.DataFrame, inst_df: pd.DataFrame,
                            fraction: float, static_features: list[str]) -> dict:
    """Fit Ridge regression on static + exec cols at given fraction, 5-fold CV R²."""
    sub = snap_df[snap_df["snapshot_fraction"] == fraction].copy()
    # merge with full target (log_nodes_explored at fraction=1.0)
    full = snap_df[snap_df["snapshot_fraction"] == 1.0][["instance_id", "capacity_mode", "nodes_explored"]].copy()
    full = full.rename(columns={"nodes_explored": "total_nodes"})
    sub = sub.merge(full, on=["instance_id", "capacity_mode"])
    sub["log_nodes_explored"] = np.log1p(sub["total_nodes"])

    # merge static features
    sub = sub.merge(inst_df[["instance_id", "capacity_mode"] + static_features], on=["instance_id", "capacity_mode"], how="left")

    avail_exec = [c for c in EXEC_COLS if c in sub.columns]
    avail_static = [c for c in static_features if c in sub.columns]

    X_static = sub[avail_static].fillna(0).values
    X_exec = sub[avail_exec].fillna(0).values
    X_combined = np.hstack([X_static, X_exec])
    y = sub["log_nodes_explored"].values

    from sklearn.model_selection import cross_val_score
    from sklearn.ensemble import RandomForestRegressor

    rf = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    
    r2_m1 = np.mean(cross_val_score(rf, X_static, y, cv=5, scoring="r2"))
    r2_m2 = np.mean(cross_val_score(rf, X_combined, y, cv=5, scoring="r2"))

    return {"fraction": fraction, "r2_m1": r2_m1, "r2_m2": r2_m2, "delta_r2": r2_m2 - r2_m1}


def main():
    print("=" * 60)
    print("Phase 3: Early Prediction Curve")
    print("=" * 60)

    snap_path = DATA_DIR / "bb_snapshots_clean.csv"
    inst_path = DATA_DIR / "instances.csv"

    if not snap_path.exists():
        print(f"Snapshots file not found: {snap_path}")
        return
    if not inst_path.exists():
        print(f"Instances file not found: {inst_path}")
        return

    snap_df = pd.read_csv(snap_path)
    inst_df = pd.read_csv(inst_path)

    print(f"Loaded {len(snap_df)} snapshot rows across "
          f"{snap_df['snapshot_fraction'].nunique()} fractions, "
          f"{snap_df['instance_id'].nunique()} instances.")

    static_features = [f for f in GROUP_A_INSTANCE_CHARACTERISTICS if f in inst_df.columns]
    print(f"Using {len(static_features)} static features.")

    fractions = sorted(snap_df["snapshot_fraction"].unique())
    records = []
    for frac in fractions:
        print(f"  Computing R² at fraction={frac:.2f}...", end="", flush=True)
        result = compute_r2_at_fraction(snap_df, inst_df, frac, static_features)
        records.append(result)
        print(f"  M1={result['r2_m1']:.4f}  M2={result['r2_m2']:.4f}  ΔR²={result['delta_r2']:.4f}")

    results_df = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "early_prediction_data.csv"
    results_df.to_csv(out_csv, index=False)
    print(f"\nSaved data to {out_csv}")

    # ---- Plot ----
    fig, ax = plt.subplots(figsize=(8, 5))
    pct_labels = [f"{int(f*100)}%" for f in results_df["fraction"]]
    x = np.arange(len(pct_labels))
    width = 0.35

    bars1 = ax.bar(x - width/2, results_df["r2_m1"], width, label="M1 (Static only)", color="#4C72B0", alpha=0.85)
    bars2 = ax.bar(x + width/2, results_df["r2_m2"], width, label="M2 (Static + Execution)", color="#DD8452", alpha=0.85)

    ax.plot(x + width/2, results_df["r2_m2"], "o-", color="#DD8452", linewidth=1.5, markersize=5)
    ax.axhline(results_df["r2_m1"].iloc[-1], linestyle="--", color="#4C72B0", linewidth=1,
               label="M1 asymptote (static only)")

    ax.set_xlabel("Fraction of B&B Search Observed", fontsize=12)
    ax.set_ylabel("5-Fold CV $R^2$ (log nodes explored)", fontsize=12)
    ax.set_title("Online Prediction: How Quickly Does Predictive\nAccuracy Accumulate During B&B Search?", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(pct_labels, fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_ylim(bottom=min(0, results_df[["r2_m1", "r2_m2"]].min().min() - 0.05))

    plt.tight_layout()
    out_fig = RESULTS_DIR / "early_prediction_curves.png"
    plt.savefig(str(out_fig), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved figure to {out_fig}")


if __name__ == "__main__":
    main()
