"""
scripts/3_compute_importance.py

Phase 3.3.5 — Feature Importance for all models.

Source:
  - PHASE_3_3_IMPLEMENTATION_PLAN.md lines 514–557
  - PHASE_3_2_DESIGN.md §10.1–10.5

Execution order:
  a. Standardized beta  — OLS and fractional logit only (load pre-computed)
  b. Permutation importance — all models, LOFO test sets, 20 repeats
  c. Elastic-net nonzero coefs — B&B optimal only
  d. Delta-R2 partitioning  — top-10 by permutation importance
  e. Importance bar chart figures — top-10 execution metrics

Script filename: 3_compute_importance.py per PHASE_3_3_IMPLEMENTATION_PLAN.md line 514
"""
import gc
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import (
    ALGO_BB,
    ALGO_DP,
    ALGO_GREEDY,
    ALGORITHM_LABEL_MAP,
    GROUP_A_INSTANCE_CHARACTERISTICS,
    MODEL_SPECS,
    N_PERMUTATION_REPEATS,
    RANDOM_SEED,
)
from utils.importance import (
    delta_r2_partitioning,
    format_elasticnet_coefs,
    load_standardized_beta,
    permutation_importance_lofo,
    _r2_full_sample,
)
from utils.preprocessing import build_feature_matrices

RNG = np.random.default_rng(RANDOM_SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PREPARED_DIR = OUTPUT_DIR / "prepared"
RESULTS_DIR = OUTPUT_DIR / "results"
DIAG_DIR = OUTPUT_DIR / "diagnostics"
FIG_DIR = OUTPUT_DIR / "figures"
FI_DIR = OUTPUT_DIR / "feature_importance"

for d in [FI_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Model family mapping — maps MODEL_SPECS "family" to importance utility key
# ---------------------------------------------------------------------------

def _model_family_key(spec_family: str) -> str:
    """Map MODEL_SPECS family string to the key used in importance utilities."""
    mapping = {
        "ols": "ols",
        "fractional_logit": "fractional_logit",
        "elasticnet": "elasticnet",
        "hurdle": "hurdle_part1",   # permutation importance on Part 1 (binary)
    }
    return mapping[spec_family]


# ---------------------------------------------------------------------------
# Figure: horizontal bar chart of top-10 execution metrics by perm importance
# ---------------------------------------------------------------------------

def _plot_importance(
    perm_df: pd.DataFrame,
    algo_label: str,
    response: str,
):
    """
    Horizontal bar chart, top-10 execution metrics by permutation importance.
    Source: PHASE_3_3_IMPLEMENTATION_PLAN.md lines 538–539
    """
    exec_df = perm_df[perm_df["predictor_type"] == "execution_metric"].head(10)
    if exec_df.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    y_pos = np.arange(len(exec_df))
    ax.barh(
        y_pos,
        exec_df["importance_mean"].values,
        xerr=exec_df["importance_sd"].values,
        align="center",
        color="#4C72B0",
        ecolor="gray",
        capsize=3,
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(exec_df["predictor"].values)
    ax.invert_yaxis()
    ax.set_xlabel(f"Permutation importance (Δ{exec_df['metric'].iloc[0]})")
    ax.set_title(f"Top-10 execution metrics\n{algo_label} — {response}")
    plt.tight_layout()
    path = FIG_DIR / f"importance_{algo_label}_{response}.png"
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"    Saved figure: {path.name}")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_importance_pipeline(
    algo: str,
    response: str,
    spec: dict,
):
    algo_label = ALGORITHM_LABEL_MAP[algo]
    spec_family = spec["family"]
    model_family = _model_family_key(spec_family)

    print(f"\n{'='*60}")
    print(f"Phase 3.3.5: {algo_label} — {response}  [{spec_family}]")

    # Load prepared data
    prepared_path = PREPARED_DIR / f"{algo_label}.pkl"
    if not prepared_path.exists():
        print(f"  ERROR: {prepared_path} not found — skipping")
        return

    df = pd.read_pickle(str(prepared_path))
    if "instance_id" not in df.columns:
        df["instance_id"] = range(len(df))

    # Build feature matrices
    X_m1, X_m2, y, _, _ = build_feature_matrices(df, algo, response, MODEL_SPECS, None)
    if y is None or len(y) == 0:
        print(f"  ERROR: empty y — skipping")
        return

    # For binary 'optimal' response, event = not optimal
    if spec_family == "elasticnet":
        if df[response].dtype == bool:
            y = (~df[response]).astype(int).values
        else:
            y = (df[response] == 0).astype(int).values

    # For hurdle Part 1 permutation importance, AUC requires binary labels.
    # y_for_perm is binarized for hurdle; raw continuous y for all others.
    # Source: roc_auc_score requires binary y_true; hurdle Part 1 models P(gap>0).
    if spec_family == "hurdle":
        y_for_perm = (y > 0).astype(int)
    else:
        y_for_perm = y

    p_m2 = X_m2.shape[1]
    print(f"  n={len(y)}, p_M2={p_m2}")

    # ------------------------------------------------------------------
    # Step a: Standardized beta — OLS and fractional logit only
    # Source: PHASE_3_3_IMPLEMENTATION_PLAN.md lines 516–520
    # ------------------------------------------------------------------
    print(f"  [a] Standardized beta...")
    std_beta_df = load_standardized_beta(DIAG_DIR, algo_label, response, spec_family, top_k=20)
    if std_beta_df is not None:
        out_path = FI_DIR / f"standardized_beta_{algo_label}_{response}.csv"
        std_beta_df.to_csv(out_path, index=False)
        print(f"    Saved: {out_path.name} ({len(std_beta_df)} rows)")
    else:
        print(f"    Not applicable for family={spec_family} (§10.1)")

    # ------------------------------------------------------------------
    # Step b: Permutation importance — all models
    # Source: PHASE_3_3_IMPLEMENTATION_PLAN.md lines 521–525
    # ------------------------------------------------------------------
    print(f"  [b] Permutation importance ({N_PERMUTATION_REPEATS} repeats × {p_m2} predictors × 5 LOFO folds)...")
    perm_df = permutation_importance_lofo(
        df=df,
        X_m2=X_m2,
        y=y_for_perm,
        model_family=model_family,
        instance_cols=GROUP_A_INSTANCE_CHARACTERISTICS,
        n_repeats=N_PERMUTATION_REPEATS,
        rng=RNG,
    )
    perm_path = FI_DIR / f"permutation_importance_{algo_label}_{response}.csv"
    perm_df.to_csv(perm_path, index=False)
    print(f"    Saved: {perm_path.name}")
    print(f"    Top-3 predictors: {list(perm_df['predictor'].head(3))}")

    # ------------------------------------------------------------------
    # Step c: Elastic-net nonzero coefs — B&B optimal only
    # Source: PHASE_3_3_IMPLEMENTATION_PLAN.md lines 526–528
    # ------------------------------------------------------------------
    if algo == ALGO_BB and response == "optimal":
        print(f"  [c] Elastic-net nonzero coefficients...")
        en_df = format_elasticnet_coefs(RESULTS_DIR)
        if not en_df.empty:
            en_path = FI_DIR / f"elasticnet_coefs_{algo_label}_{response}.csv"
            en_df.to_csv(en_path, index=False)
            print(f"    Saved: {en_path.name} ({len(en_df)} nonzero coefs)")
    else:
        print(f"  [c] Elastic-net nonzero coefs: not applicable")

    # ------------------------------------------------------------------
    # Step d: Delta-R2 partitioning — top-10 execution metrics by perm importance
    # Source: PHASE_3_3_IMPLEMENTATION_PLAN.md lines 529–532
    # ------------------------------------------------------------------
    print(f"  [d] Delta-R² partitioning (top-10 execution metrics)...")
    exec_perm = perm_df[perm_df["predictor_type"] == "execution_metric"]
    top10 = list(exec_perm["predictor"].head(10))
    top10_in_m2 = [p for p in top10 if p in X_m2.columns]

    if top10_in_m2:
        r2_full = _r2_full_sample(X_m2, y_for_perm, model_family)
        dr2_df = delta_r2_partitioning(
            X_m2=X_m2,
            y=y_for_perm,
            top_k_predictors=top10_in_m2,
            model_family=model_family,
            r2_full=r2_full,
        )
        dr2_path = FI_DIR / f"delta_r2_partitioning_{algo_label}_{response}.csv"
        dr2_df.to_csv(dr2_path, index=False)
        print(f"    Saved: {dr2_path.name}")
        print(f"    Sum of Δ-R²: {dr2_df['delta_r2'].sum():.4f} vs full Δ-R²: {r2_full:.4f}")
    else:
        print(f"    No execution metrics found in M2 — skipping")

    # ------------------------------------------------------------------
    # Step e: Importance figure — top-10 execution metrics
    # Source: PHASE_3_3_IMPLEMENTATION_PLAN.md lines 538–539
    # ------------------------------------------------------------------
    print(f"  [e] Generating importance figure...")
    _plot_importance(perm_df, algo_label, response)

    del df, X_m1, X_m2, y
    gc.collect()


def main():
    print("=" * 60)
    print("Phase 3.3.5 — Feature Importance")
    print("=" * 60)

    # Iterate over all (algo, response) pairs in MODEL_SPECS
    # Order: OLS first (fast), then flogit, then elasticnet, then hurdle
    family_order = ["ols", "fractional_logit", "elasticnet", "hurdle"]

    specs_ordered = sorted(
        MODEL_SPECS.items(),
        key=lambda kv: family_order.index(kv[1]["family"]),
    )

    for (algo, response), spec in specs_ordered:
        run_importance_pipeline(algo, response, spec)

    print("\n" + "=" * 60)
    print("PHASE 3.3.5 COMPLETE")
    print("=" * 60)
    print(f"\nOutputs in: {FI_DIR}")
    print(f"Figures in: {FIG_DIR}")


if __name__ == "__main__":
    main()
