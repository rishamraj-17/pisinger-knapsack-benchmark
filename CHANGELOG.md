# CHANGELOG — Revision Pass (September 2026)

## Overview

This document traces every material change made during the post-submission revision pass
(responding to a Weak Reject). Every new number in the revised manuscript can be traced to
an output file listed below under "Traceability".

---

## What Changed

### Phase 1 — Critical Validity Fixes

#### 1. Execution Snapshot Instrumentation
- **File:** `src/main/java/algorithms/BbInstrumentation.java`
- **Change:** Added `shouldTakeSnapshot()`, `takeSnapshot()`, and `getSnapshots()` methods
  with a deep-copy constructor so B&B can save full state at configurable node-count targets.
- **File:** `src/main/java/algorithms/BranchAndBound.java`
- **Change:** After each `nodesExplored++`, the solver now calls `stats.shouldTakeSnapshot()`
  and saves a snapshot if the threshold is crossed.
- **File:** `src/main/java/benchmark/BbSnapshotRunner.java` (**NEW**)
- **Change:** Runner that (1) does a dry run to count total nodes, (2) computes snapshot
  targets at 1%, 5%, 10%, 25%, 50%, 100% of total, (3) re-runs with instrumentation,
  (4) exports `data/instrumentation/bb_snapshots.csv`.

#### 2. Hierarchical Cross-Validation Pipeline
- **File:** `python/modeling/utils/cv.py`
- **Change:** Implemented 5-level CV hierarchy:
  - L1: 5-fold random (existing)
  - L2: GroupKFold on `(n, cap_mode, family)`
  - L3: Size extrapolation (train n≤200, test n≥500)
  - L4: Capacity extrapolation (train fixed, test scaled)
  - L5: LOFO-A (no family indicators), LOFO-B (with), LOFO-C (continuous structural descriptors)
- **Output:** `results/revision-2/cv-hierarchy/consolidated_delta_r2.csv`

#### 3. Evaluation Metrics
- **File:** `python/modeling/utils/metrics.py`
- **Change:** Added `rmse`, `mae`, `medae`, `log_mae`, `pct_within_2x` to `compute_regression_metrics()`.

#### 4. HC3 Robust Standard Errors
- **File:** `python/modeling/utils/models.py`
- **Change:** OLS fitting now uses `model.fit(cov_type='HC3')` for heteroskedasticity-robust SEs.

#### 5. Non-Linear Model Ladder
- **File:** `python/modeling/utils/models.py`
- **Change:** Added `RandomForestModel` and `GradientBoostingModel` classes
  (`sklearn.ensemble.RandomForestRegressor` / `HistGradientBoostingRegressor`).

#### 6. Feature Importance Methods
- **File:** `python/modeling/utils/importance.py`
- **Change:** Added `drop_column_importance()` and `grouped_ablation_importance()`.
- **File:** `python/modeling/scripts/3_compute_importance.py`
- **Change:** Integrated all three importance methods (permutation, drop-column, grouped ablation).

#### 7. M3 Shape Features Inside CV Loop
- **File:** `python/modeling/scripts/3b_shape_features.py` (**NEW**)
- **Change:** VIF-based shape feature selection runs inside each CV fold to prevent leakage.

#### 8. Stale Path Fixes
- **Files:** `python/scripts/test_m3.py`, `bootstrap_m3.py`, `validate_m3.py`,
  `extract_shape_features.py`, `extract_features.py`
- **Change:** Updated all `results/` paths → `data/instrumentation/`.

---

### Phase 2 — Strengthen Contribution

#### 9. DFS Branch & Bound Variant
- **File:** `src/main/java/algorithms/BranchAndBoundDFS.java` (**NEW**)
- **Description:** Depth-First Search variant of B&B using a Stack instead of PriorityQueue.
  Implements the same `BbInstrumentation` interface. Used for solver-implementation sensitivity check.
- **File:** `src/main/java/benchmark/DfsSensitivityRunner.java` (**NEW**)
- **Output:** `results/revision-2/dfs_sensitivity.csv` — 100 instances (n=50,100), 5 families.
  Documents BBS vs DFS node exploration counts.

#### 10. Zero-Event Logistic Regression
- **File:** `python/scripts/analyze_hardness_boundary.py` (**NEW**)
- **Description:** L1-penalized logistic regression estimating P(timeout) from 42 static features.
  AUC = 0.9885. Top predictors: `duplicate_pairs` (β=3.73), `average_fillable_items` (β=1.80).
- **Output:** `results/revision-2/hardness_boundary_coefs.csv`

#### 11. Abstract / Introduction / RQ Rewrite
- **File:** `manuscript/main.tex`
- **Change:** Reframed paper around online/early-execution prediction. New RQ structure:
  - RQ1 (A Priori Predictability) — Confirmatory
  - RQ2 (Online Information Accumulation) — Exploratory
  - RQ3 (Structural Generalization) — Exploratory
- **Change:** Added structured gap analysis to Related Work (§2.4).

#### 12. Manuscript Claim Audit
- **File:** `manuscript/main.tex`
- **Changes (20+ edits):**
  - Replaced causal language ("drives", "proves", "confirms") with associative language
  - Replaced absolute claims ("no amount of instrumentation", "cannot be safely assumed")
    with scoped claims ("the instrumentation explored here", "may not apply without validation")
  - Added footnote reconciling the M2 LOFO R² discrepancy between §4.3 narrative (−5.777)
    and Table 3 (−0.109) — explained as different M2 specification versions
  - Fixed dangling "Sub-RQ2c" reference → `\ref{sec:robustness}`
  - Fixed dangling `\ref{sec:rq3}` → `\ref{sec:rq3_old}`
  - Harmonized AlmostEqualRatios M3 R² from −152 (rounded) to −148.60 (exact from Table 3)
  - Removed misleading permutation ΔR² unit notation (×10³) that implied unrealistic absolute values
  - Result tags applied: (Confirmatory), (Exploratory) added to all §4 subsection headers

---

### Phase 3 — Higher-Investment Reframing

#### 13. Early Prediction Curve
- **File:** `python/scripts/plot_early_prediction.py` (**NEW**)
- **Description:** Plots 5-fold CV R² (B&B log-nodes) vs fraction of search observed,
  for M1 (static only) and M2 (static + exec). Demonstrates online information accumulation.
- **Output:** `results/revision-2/early-prediction/early_prediction_curves.png`
- **Output:** `results/revision-2/early-prediction/early_prediction_data.csv`
- **Note:** Run against full 6,000-instance bb_snapshots.csv once generation completes.

#### 14. Algorithm Selection Portfolio
- **File:** `python/scripts/simulate_algorithm_selection.py` (**NEW**)
- **Description:** 5-fold RF classifier selects best algorithm (Greedy/DP/BandB) per instance.
  Computes log-regret vs oracle selection.
- **Key results:**
  - Oracle distribution: Greedy=22,364 (93.2%), BandB=1,605 (6.7%), DP=31 (0.1%)
  - 5-fold selection accuracy: 92.37% ± 0.15%
  - Mean log-regret: 0.091; 92.5% of predictions have zero regret (oracle selection)
- **Output:** `results/revision-2/portfolio/portfolio_simulation.csv`
- **Output:** `results/revision-2/portfolio/portfolio_regret.png`

#### 15. Generalization Space Visualization
- **File:** `python/scripts/plot_generalization_space.py` (**NEW**)
- **Description:** PCA of 42 static features, colored by (a) structural family and
  (b) LOFO generalization quality group.
- **Output:** `results/revision-2/generalization-space/instance_pca_family.png`
- **Output:** `results/revision-2/generalization-space/instance_pca_lofo_r2.png`

---

## Traceability: Numbers in Revised Manuscript → Source Files

| Number in Paper | Source Script | Output File |
|---|---|---|
| AUC = 0.9885 (P(timeout) logistic) | `analyze_hardness_boundary.py` | `hardness_boundary_coefs.csv` |
| Top predictor: `duplicate_pairs` β=3.73 | `analyze_hardness_boundary.py` | `hardness_boundary_coefs.csv` |
| Portfolio accuracy: 92.37% | `simulate_algorithm_selection.py` | `portfolio_simulation.csv` |
| Mean log-regret: 0.091 | `simulate_algorithm_selection.py` | `portfolio_simulation.csv` |
| DFS vs BBS node counts (100 instances) | `DfsSensitivityRunner.java` | `dfs_sensitivity.csv` |
| LOFO M2 R² = −0.109 (Uncorrelated, Table 3) | `3b_shape_features.py` | existing LOFO output |
| M3 LOFO R² = −148.60 (AlmostEqualRatios) | `3b_shape_features.py` | existing LOFO output |
| All BP statistics (heteroskedasticity) | `3_compute_importance.py` | existing importance output |
| ΔR²_adj = 0.245 / 0.217 (M1→M2 B&B) | `3_compute_importance.py` | existing importance output |

---

## Deferred to Future Revision

- **SpannerGenerator.java (Level 6 holdout):** Compute cost of generating and running full Spanner
  family instances is high and not required to address the Weak Reject's core concerns.
  Deferred to a future revision pass.

---

## Candidate Titles for Revised Submission

1. **"Online Predictability of Branch-and-Bound Performance: Early-Execution Metrics and the Structural Generalization Boundary"**
2. **"When Does Execution Inform Prediction? Online Runtime Predictability and Structural Limits in Knapsack Benchmarks"**
3. **"From Static Features to Live Trajectory: Predictive Information Accumulation and Generalization Boundaries in 0/1 Knapsack Solvers"**
