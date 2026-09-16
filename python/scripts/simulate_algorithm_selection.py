"""
python/scripts/simulate_algorithm_selection.py

Simulate an algorithm selection portfolio using predict-then-run:
  - Train a model to predict which of {Greedy, DP, BandB} will have the
    lowest runtime on a new instance.
  - Compute regret vs. oracle (best algorithm per instance known in hindsight).

Output:
  results/revision-2/portfolio/portfolio_simulation.csv
  results/revision-2/portfolio/portfolio_regret.png
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modeling.config import GROUP_A_INSTANCE_CHARACTERISTICS

BASE_DIR = Path(__file__).resolve().parent.parent
PREPARED_DIR = BASE_DIR / "modeling" / "output" / "prepared"
RESULTS_DIR = BASE_DIR.parent / "results" / "revision-2" / "portfolio"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_all() -> pd.DataFrame:
    """Load Greedy, DP, BandB prepared DataFrames and merge runtimes."""
    dfs = {}
    for alg in ["Greedy", "DP", "BandB"]:
        path = PREPARED_DIR / f"{alg}.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Prepared data not found: {path}")
        df = pd.read_pickle(str(path))
        dfs[alg] = df

    # Use 'instance_id' as join key; keep log_time_millis per algorithm
    greedy = dfs["Greedy"][["instance_id", "log_time_millis"] +
                             [f for f in GROUP_A_INSTANCE_CHARACTERISTICS
                              if f in dfs["Greedy"].columns]].copy()
    greedy = greedy.rename(columns={"log_time_millis": "greedy_log_time"})

    dp = dfs["DP"][["instance_id", "log_time_millis"]].rename(
        columns={"log_time_millis": "dp_log_time"})

    bb = dfs["BandB"][["instance_id", "log_time_millis"]].rename(
        columns={"log_time_millis": "bb_log_time"})

    merged = greedy.merge(dp, on="instance_id").merge(bb, on="instance_id")
    return merged


def main():
    print("=" * 60)
    print("Phase 3: Algorithm Selection Portfolio Simulation")
    print("=" * 60)

    try:
        merged = load_all()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    print(f"Loaded {len(merged)} instances with runtimes for all 3 algorithms.")

    # Oracle: which algorithm is fastest per instance?
    time_cols = ["greedy_log_time", "dp_log_time", "bb_log_time"]
    alg_names = ["Greedy", "DP", "BandB"]
    merged["oracle_alg"] = merged[time_cols].idxmin(axis=1).map({
        "greedy_log_time": "Greedy",
        "dp_log_time": "DP",
        "bb_log_time": "BandB",
    })
    merged["oracle_log_time"] = merged[time_cols].min(axis=1)

    print("\nOracle selection distribution:")
    print(merged["oracle_alg"].value_counts())

    static_features = [f for f in GROUP_A_INSTANCE_CHARACTERISTICS
                       if f in merged.columns]
    X = merged[static_features].fillna(0).values
    y_raw = merged["oracle_alg"].values

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    # 5-fold CV portfolio simulation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scaler = StandardScaler()

    records = []
    fold_accs = []

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        X_tr_s = scaler.fit_transform(X_train)
        X_te_s = scaler.transform(X_test)

        clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
        clf.fit(X_tr_s, y_train)
        y_pred = clf.predict(X_te_s)
        fold_accs.append(accuracy_score(y_test, y_pred))

        # Compute regret: predicted_time - oracle_time
        test_rows = merged.iloc[test_idx].copy()
        pred_alg_names = le.inverse_transform(y_pred)
        test_rows["predicted_alg"] = pred_alg_names
        test_rows["fold"] = fold_idx + 1

        def get_predicted_log_time(row):
            col_map = {"Greedy": "greedy_log_time", "DP": "dp_log_time", "BandB": "bb_log_time"}
            return row[col_map[row["predicted_alg"]]]

        test_rows["predicted_log_time"] = test_rows.apply(get_predicted_log_time, axis=1)
        test_rows["log_regret"] = test_rows["predicted_log_time"] - test_rows["oracle_log_time"]
        records.append(test_rows[["instance_id", "oracle_alg", "predicted_alg",
                                   "oracle_log_time", "predicted_log_time",
                                   "log_regret", "fold"]])

    sim_df = pd.concat(records, ignore_index=True)
    out_csv = RESULTS_DIR / "portfolio_simulation.csv"
    sim_df.to_csv(out_csv, index=False)

    print(f"\n5-Fold CV Selection Accuracy: {np.mean(fold_accs):.4f} ± {np.std(fold_accs):.4f}")
    print(f"\nLog-Regret Statistics (predicted_time - oracle_time, in log-ms):")
    print(f"  Mean:   {sim_df['log_regret'].mean():.4f}")
    print(f"  Median: {sim_df['log_regret'].median():.4f}")
    print(f"  95th %: {sim_df['log_regret'].quantile(0.95):.4f}")
    print(f"  % zero regret (oracle selection): {(sim_df['log_regret'] <= 0.001).mean()*100:.1f}%")

    # Baseline: always pick the globally best algorithm
    global_best = sim_df.groupby("oracle_alg")["oracle_log_time"].count().idxmax()
    # Actually: always pick the single algorithm with the best mean log_time in train
    for baseline_alg in alg_names:
        col = {"Greedy": "greedy_log_time", "DP": "dp_log_time", "BandB": "bb_log_time"}[baseline_alg]
        if col in merged.columns:
            baseline_regret = merged[col] - merged["oracle_log_time"]
            print(f"  Baseline (always {baseline_alg}): mean log-regret = {baseline_regret.mean():.4f}")

    # ---- Plot ----
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Regret distribution
    ax = axes[0]
    ax.hist(sim_df["log_regret"], bins=60, color="#4C72B0", alpha=0.75, edgecolor="white")
    ax.axvline(0, color="black", linestyle="--", linewidth=1.2, label="Zero regret (oracle)")
    ax.axvline(sim_df["log_regret"].mean(), color="#DD8452", linestyle="-",
               linewidth=1.5, label=f"Mean regret = {sim_df['log_regret'].mean():.3f}")
    ax.set_xlabel("Log-scale Regret (predicted − oracle log-ms)", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("Algorithm Portfolio Regret Distribution\n(5-Fold CV, RF Selector)", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Right: Confusion matrix style bar (selection accuracy by true best alg)
    ax = axes[1]
    acc_by_alg = []
    for alg in alg_names:
        subset = sim_df[sim_df["oracle_alg"] == alg]
        if len(subset) > 0:
            acc = (subset["predicted_alg"] == alg).mean()
            acc_by_alg.append((alg, acc, len(subset)))
    if acc_by_alg:
        labels = [a[0] for a in acc_by_alg]
        accs = [a[1] for a in acc_by_alg]
        counts = [a[2] for a in acc_by_alg]
        bars = ax.bar(labels, accs, color=["#4C72B0", "#DD8452", "#55A868"], alpha=0.85)
        for bar, cnt in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f"n={cnt}", ha="center", fontsize=9)
        ax.set_ylim(0, 1.15)
        ax.set_ylabel("Selection Accuracy", fontsize=11)
        ax.set_title("Per-Oracle Algorithm\nSelection Accuracy", fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    out_fig = RESULTS_DIR / "portfolio_regret.png"
    plt.savefig(str(out_fig), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nSaved figure to {out_fig}")
    print(f"Saved simulation data to {out_csv}")


if __name__ == "__main__":
    main()
