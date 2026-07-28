# Architecture Conformance Report — Phase 1 Audit (Revised)

**Audit Date:** 2026-07-28
**Scope:** Full repository — all phases (0 through 3.3.6)
**Method:** Every claim verified against repository evidence (source code, design docs, output files, governance docs)
**Revision Note:** This is the VERIFIED edition. Each finding was independently re-examined with adversarial scrutiny.

---

## 1. Architecture Summary

The project implements an empirical comparison of three classical 0/1 knapsack algorithms (Greedy, Dynamic Programming, Branch & Bound) across five Pisinger instance families. The architecture spans two languages and multiple phases:

### Phase 0 — Benchmark Foundation (Java)
```
src/main/java/
  algorithms/     Algorithm.java, Greedy.java, DynamicProgramming.java,
                  BranchAndBound.java, AlgorithmFactory.java
                  +Instrumentation: BbInstrumentation.java, DpInstrumentation.java,
                  GreedyInstrumentation.java
  dataset/        DatasetGenerator.java, InstanceGenerator.java + 5 Pisinger generators
  benchmark/      BenchmarkRunner.java, ResultsExporter.java, DatasetIntegrationRunner.java
                  +InstrumentationRunners: BbInstrumentationRunner, DpInstrumentationRunner,
                  GreedyInstrumentationRunner
  model/          Item.java, KnapsackInstance.java, Result.java
  Main.java       Entry point
```

### Phase 1 — Analysis & Paper (Python)
```
Root-level Python: analyze.py, figures.py, plot_utils.py, extract_features.py, update_draft.py
  tables/*.tex, figures/{fixed,scaled}/*, paper/draft.md
```

### Phase 2 — Instrumentation & Dataset Assembly (Java)
```
results/bb_instrumentation.csv, results/dp_instrumentation.csv,
  results/greedy_instrumentation.csv
  → DatasetIntegrationRunner → out/results/canonical_dataset.csv
```

### Phase 3 — Statistical Modeling (Python)
```
Phase_3_3_Modeling/
  config.py             318 lines — single source of truth
  utils/                __init__.py, cv.py, data.py, diagnostics.py,
                        fractional_models.py, importance.py, metrics.py,
                        models.py, preprocessing.py
  scripts/              1_prepare_data.py, 2a_fit_ols.py, 2b_fit_fractional_logit.py,
                        2c_fit_elasticnet.py, 2d_fit_hurdle.py, 3_compute_importance.py,
                        4_diagnostics.py
  output/               prepared/, results/ (20 files), cross_validation/ (16 files),
                        diagnostics/ (77 files), feature_importance/ (26 files),
                        figures/ (empty), tables/ (empty)
```

### Intended Data Flow
```
DatasetGenerator → BenchmarkRunner → full_experiment.csv
                                          ↓
extract_features.py → instances.csv      │
       ↓                                ↓
   Instance features         DatasetIntegrationRunner
       ↓                                ↓
   canonical_dataset.csv (18,000 × 110)
       ↓
   Phase_3_3_Modeling/1_prepare_data.py → prepared/{Greedy,DP,BandB}.pkl
       ↓
   2a_fit_ols.py, 2b_fit_fractional_logit.py,
   2c_fit_elasticnet.py, 2d_fit_hurdle.py
       ↓
   3_compute_importance.py, 4_diagnostics.py
       ↓
   [5_sensitivity.py — future phase 3.3.7]
   [6_summarize.py — future phase 3.3.8]
```

---

## 2. Implementation Summary

### Fully Implemented and Verified
| Component | Evidence |
|-----------|----------|
| 3 algorithms (Greedy, DP, B&B) | `src/main/java/algorithms/` — complete with `Algorithm` interface |
| 5 Pisinger instance generators | `src/main/java/dataset/` — Uncorrelated, WeaklyCorrelated, StronglyCorrelated, InverseCorrelated, AlmostEqualRatios |
| Benchmark harness with timeout/warmup | `BenchmarkRunner.java` — 30s timeout, JIT warmup, per-instance warmup |
| Algorithm instrumentation (B&B, DP, Greedy) | `BbInstrumentation.java` (45 metrics), `DpInstrumentation.java` (15 metrics), `GreedyInstrumentation.java` (6 metrics) |
| Dataset integration | `DatasetIntegrationRunner.java` — merges instances.csv + full_experiment.csv + instrumentation CSVs |
| Phase 1 analysis pipeline | `analyze.py`, `figures.py`, `plot_utils.py` → `tables/*.tex`, `figures/*` |
| Phase 3.3.1 Foundation | `config.py`, `utils/data.py`, `utils/preprocessing.py`, `utils/cv.py`, `utils/metrics.py`, `scripts/1_prepare_data.py` |
| Phase 3.3.2 OLS Models | `utils/models.py`, `scripts/2a_fit_ols.py` — LOFO CV, 5-fold CV, full-sample inference, all 5 OLS responses |
| Phase 3.3.3 Fractional Logit | `utils/fractional_models.py`, `utils/models.py`, `scripts/2b_fit_fractional_logit.py` — LOFO CV, full-sample fit, SE comparison, 2 responses |
| Phase 3.3.4 Elastic-Net & Hurdle | `utils/models.py`, `scripts/2c_fit_elasticnet.py`, `scripts/2d_fit_hurdle.py` — B&B optimal + solution_gap |
| Phase 3.3.5 Feature Importance | `utils/importance.py`, `scripts/3_compute_importance.py` — permutation importance, delta-R² partitioning, elastic-net nonzero coefs, standardized β |
| Phase 3.3.6 Diagnostics | `utils/diagnostics.py`, `scripts/4_diagnostics.py` — VIF, Q-Q, BP test, Cook's distance, calibration curves, smearing factors, assumption summaries |

### All 9 Model Specifications are Fully Implemented
| Model | Config | Script | Outputs |
|-------|--------|--------|---------|
| Greedy log_time_millis (OLS, Confirmatory) | ✅ | 2a_fit_ols.py | ✅ metrics, inference, CV folds, std_beta |
| Greedy optimality_gap (FLogit, Confirmatory) | ✅ | 2b_fit_fractional_logit.py | ✅ metrics, inference, CV folds, std_beta |
| DP log_time_millis (OLS, Confirmatory) | ✅ | 2a_fit_ols.py | ✅ metrics, inference, CV folds, std_beta |
| DP log_memory_mb (OLS, Exploratory) | ✅ | 2a_fit_ols.py | ✅ metrics, inference, CV folds, std_beta |
| DP fill_rate (FLogit, Supplementary) | ✅ | 2b_fit_fractional_logit.py | ✅ metrics, inference, CV folds, std_beta |
| B&B log_time_millis (OLS, Confirmatory) | ✅ | 2a_fit_ols.py | ✅ metrics, inference, CV folds, std_beta |
| B&B optimal (Elastic-Net, Exploratory) | ✅ | 2c_fit_elasticnet.py | ✅ metrics, LOFO folds |
| B&B log_nodes_explored (OLS, Supplementary) | ✅ | 2a_fit_ols.py | ✅ metrics, inference, CV folds, std_beta |
| B&B solution_gap (Hurdle, Supplementary) | ✅ | 2d_fit_hurdle.py | ✅ hurdle_metrics.csv, LOFO folds |

---

## 3. Mapping Table — Design Decisions to Implementation

| # | Architectural Decision | Source | Status | Evidence |
|---|---|---|---|---|
| 1 | Config-driven model specification in `config.py` | Plan §1.3 | ✅ FULLY | `config.py:196-260` — all 9 models in MODEL_SPECS dict |
| 2 | Per-algorithm subsetting (no cross-algo pooling) | Plan §1.4 | ✅ FULLY | `data.py:filter_algorithm()`, all scripts filter per algorithm |
| 3 | LOFO CV by family | Design §8.1 | ✅ FULLY | `cv.py:LofoFoldSplitter` — 5 families, one held out per fold |
| 4 | 5-fold CV (secondary) | Design §8.2 | ✅ FULLY | `cv.py:FiveFoldStratifiedSplitter` — stratified by family×cap_mode |
| 5 | Cluster-robust SEs by instance_id | Design §11.1 | ✅ FULLY | `models.py:cluster_robust_se()` — using `get_robustcov_results(cov_type='cluster')` |
| 6 | Bootstrap ΔR² (1999 resamples, stratified by family) | Plan §2.2 | ✅ FULLY | `models.py:bootstrap_delta_r2()` — 1999 resamples, family-stratified |
| 7 | Bootstrap Δ pseudo-R² | Plan §2.3 | ✅ FULLY | `models.py:bootstrap_delta_pseudo_r2()` — 1999 resamples, family-stratified |
| 8 | Standardised β pipeline | Plan §2.2 step 2f | ✅ FULLY | `models.py:standardized_beta()` — refits OLS on scaled X and y. Mathematically equivalent to formula β = coef × SD_x/SD_y for OLS. See revision note D9. |
| 9 | Fractional logit with HC3 robust SEs | Design §7.4 | ✅ FULLY | `models.py:fit_fractional_logit()` — `cov_type='HC3'` |
| 10 | Elastic-net with nested CV, α=0.5, saga solver | Design §7.5 | ✅ FULLY | `models.py:fit_elasticnet()` — LogisticRegressionCV with saga, α=0.5, 1-SE rule, nested within LOFO |
| 11 | Hurdle model: logistic + fractional logit | Design §2.2 | ✅ FULLY | `models.py:fit_hurdle()` — part1: unregularized logistic, part2: GLM Binomial |
| 12 | VIF post-fit diagnostic, iterative removal | Design §6.2 | ✅ FULLY | `diagnostics.py:perform_vif_thinning()` — implemented in 4_diagnostics.py |
| 13 | Per-algorithm correlation verification | Design §3.3 | ⚠️ PARTIAL | `preprocessing.py:compute_per_algorithm_correlation()` — computes per-algo correlations but does NOT compare to Phase 3.1 baseline (no Δ\|r\| > 0.10 report) |
| 14 | DP compositional check | Design §3.4 | ✅ FULLY | `preprocessing.py:check_dp_composition()` — verified: include+exclude+tie = total_evaluations exactly |
| 15 | Back-transformed RMSE with Duan's smearing | Design §9.1 | ✅ FULLY | `metrics.py:duan_smearing()`, `metrics.py:backtransformed_rmse()` — pooled and family-specific φ |
| 16 | Greedy optimality_gap via DP join | Design §2.2 | ✅ FULLY | `data.py:compute_optimality_gap()` — joins on (instance_id, capacity_mode) |
| 17 | B&B solution_gap via DP join | Plan §4.1 step 3 | ✅ FULLY | `data.py:compute_solution_gap()` — same join pattern |
| 18 | Seed reproducibility (numpy rng(42)) | Plan §1.4 | ✅ FULLY | `config.py:RANDOM_SEED=42` — used consistently across all scripts |
| 19 | Model-specific exclusions (near-circularity) | Design §4.6 | ✅ FULLY | `config.py:MODEL_SPECIFIC_EXCLUSIONS` — DP memory, DP fill_rate, B&B log_nodes, B&B bound metrics all excluded correctly |
| 20 | Correlation-block pre-filter (§6.3) | Design §6.3 | ✅ FULLY | `preprocessing.py:apply_block_filter()` — drops Block 1-3 variables; Block 4 handled per-model in MODEL_SPECIFIC_EXCLUSIONS |
| 21 | Arctanh transform for correlation predictors | Design §5.2 | ✅ FULLY | `preprocessing.py:arctanh_transform()` — clips to ±0.9999, then arctanh |
| 22 | Family one-hot encoding (reference=Uncorrelated) | Design §5.3 | ✅ FULLY | `preprocessing.py:encode_family()` — 5→4 dummies, Uncorrelated dropped |
| 23 | Include both n and log(n) by default | Design §5.3 | ✅ FULLY | `preprocessing.py:add_log_n()` — both retained in feature matrices |
| 24 | Capacity_mode binary encoding | Design §5.3 | ✅ FULLY | `preprocessing.py:encode_capacity_mode()` — 0=fixed, 1=scaled |
| 25 | String histograms excluded globally | Design §3.2, §5.4 | ✅ FULLY | `config.py:STRING_HISTOGRAM_COLUMNS` — depth_histogram, queue_histogram, improvement_depths, improvement_nodes |
| 26 | Zero-event family handling for B&B optimal | Design §8.3 | ✅ FULLY | `2c_fit_elasticnet.py` — Brier score for zero-event families, AUC + Brier for families with events |
| 27 | 1-SE rule for elastic-net λ selection | Design §8.4 | ✅ FULLY | `models.py:fit_elasticnet()` — mean_deviance + SE threshold, selects simplest model within 1 SE |
| 28 | Permutation importance (20 repeats) | Design §10.2 | ✅ FULLY | `importance.py:permutation_importance_lofo()` — 20 repeats per predictor, LOFO test sets |
| 29 | Delta-R² partitioning for top-10 metrics | Design §10.4 | ✅ FULLY | `importance.py:delta_r2_partitioning()` — restricts to top-k predictors |
| 30 | `utils/` modules are reusable, scripts are independent | Plan §1.2 | ✅ FULLY | Verified: no circular imports, scripts only import from utils, each script independently runnable |

---

## 4. Missing Components (Future Phases)

These components are **intentionally deferred future work**, explicitly documented as "Not started" in PROJECT_STATE_REPORT.md §3.3.7 and §3.3.8. They are listed here for completeness but are NOT defects.

| # | Component | Intended Phase | Status per Governance |
|---|---|---|---|
| M1 | `scripts/5_sensitivity.py` | 3.3.7 | Not started — planned future phase |
| M2 | `scripts/6_summarize.py` | 3.3.8 | Not started — planned future phase |
| M3 | `utils/reporting.py` | 3.3.8 | Not started — planned future phase |
| M4 | `master_results.csv` | 3.3.8 | Not started — will be created by 6_summarize.py |
| M5 | LaTeX output tables | 3.3.8 | Not started — will be created by 6_summarize.py |
| M6 | `output/figures/` diagnostic plots | 3.3.6 | Diagnostic plots exist in `output/diagnostics/` (77 files); figures/ empty. Plan §5.1 maps figures/ to diagnostic content — minor directory variance |
| M7 | BH multiplicity-adjusted p-values | 3.3.8 | Not started — will be implemented in 6_summarize.py |
| M8 | LOFO per-family R² matrix | 3.3.8 | Not started — will be implemented in 6_summarize.py |

> **Note on output/figures/:** The Implementation Plan §5.1 specifies `output/figures/` for diagnostic plots. The implementation stores them in `output/diagnostics/` instead. All plots exist and are complete; this is a directory-naming variance, not a missing feature.

---

## 5. Unexpected Components

| # | Component | Location | Classification | Detail |
|---|---|---|---|---|
| U1 | `utils/fractional_models.py` | `Phase_3_3_Modeling/utils/` | **Engineering Improvement** | **NOT dead code.** 8 functions total: 3 unique functions actively used by `2b_fit_fractional_logit.py`, 5 re-exports from `models.py` as convenience wrappers. The unique functions (`fit_fractional_logit_unadjusted`, `flogit_cluster_robust_se`, `extract_ll_aic_bic`) are called in `run_full_sample()`. The file is ACTIVELY IMPORTED. It creates unnecessary indirection but is functional. |
| U2 | Root `.class` files | Repository root | **Confirmed Repository Defect** (LOW) | Build artifacts checked into version control: CompareBound.class, TestBound.class, TestFloat.class, TestIsolate.class, TestNodeCount.class, TestPQ.class, TestRandom.class |
| U3 | CV metric aggregation duplicated | `2a_fit_ols.py:49-80` and `2b_fit_fractional_logit.py:54-83` | **Engineering Improvement** (LOW) | Near-identical `_compute_cv_metrics()` and `_aggregate_cv_metrics()` in both scripts. Compute different metrics (R² vs pseudo-R²) but structure is duplicated. |
| U4 | `CORRELATION_BLOCK_PRE_FILTER_DROPS` in preprocessing.py | `preprocessing.py:114-118` | **Engineering Improvement** (LOW) | Configuration scattered outside `config.py` — minor violation of "single source of truth" |
| U5 | Sklearn import inside function body | `models.py:236-240` | **Engineering Improvement** (LOW) | `from sklearn.linear_model import LinearRegression` inside `_fast_r2()` |

---

## 6. Deviations (Revised)

| # | Design Requirement | Implementation | Deviation | Classification |
|---|---|---|---|---|
| D1 | Fractional logit functions should be in `utils/models.py` only (Plan §1.2, §2.3 step 1) | `utils/fractional_models.py` exists as a wrapper with 3 unique utility functions | **Architectural drift.** The file is NOT dead code (verified: all functions are used). However, it creates an unnecessary abstraction layer. The 3 unique functions should live in `models.py` or as a separate utility module. | **Engineering Improvement** (was: CRITICAL) |
| D2 | Standardised β = coef × (SD_x / SD_y) OR refit on scaled data (Plan §2.2 step 2f, Design §10.1) | `models.py:standardized_beta()` refits OLS on scaled X AND scaled y | **Mathematically equivalent for OLS.** β_s = (X_s' X_s)^(-1) X_s' y_s = β_j × SD_xj / SD_y exactly. For fractional logit, scaling y to z-scores is theoretically questionable (breaks [0,1] support for Binomial GLM), but design allows it as "descriptive only". | **False Positive** (OLS) + **Engineering Improvement** (FLogit) |
| D3 | Per-algorithm correlation comparison to Phase 3.1 (Δ\|r\| > 0.10) (Design §3.3) | `compute_per_algorithm_correlation()` dumps correlations but does NOT compare to Phase 3.1 baseline | **Missing comparative step.** Cannot verify block structure preservation. | **Requires Further Evidence** — need to check if Phase 3.1 block structure is available in comparable format |
| D4 | `utils/reporting.py` should contain BH adjustment (Plan §1.2) | `utils/reporting.py` does not exist | **Intentionally deferred.** Part of Phase 3.3.8 which is documented as "Not started" in PROJECT_STATE_REPORT.md. | **Intentional Design Evolution** |
| D5 | `scripts/5_sensitivity.py` for capacity-mode, complete-only, family-level analyses (Plan §2.7) | File does not exist | **Intentionally deferred.** Part of Phase 3.3.7 which is documented as "Not started". | **Intentional Design Evolution** |
| D6 | `scripts/6_summarize.py` for aggregation, BH adjustment, LaTeX tables (Plan §2.8) | File does not exist | **Intentionally deferred.** Part of Phase 3.3.8 which is documented as "Not started". | **Intentional Design Evolution** |
| D7 | Model specs use `'m2_predictors'` key (Plan §1.3) | `config.py:MODEL_SPECS` uses `'m2_predictor_label'` (singular) | **Naming difference only.** No functional impact. | **Documentation Mismatch** |
| D8 | Plan §4.1 step 11: Block 4 variables handled as structural exclusions per-model | `CORRELATION_BLOCK_PRE_FILTER_DROPS` does NOT include Block 4; applied per-model via MODEL_SPECIFIC_EXCLUSIONS | Conforms to design. | **Confirmed Architectural Conformance** |

---

## 7. Detailed Verification Notes

### D1 / U1 — `utils/fractional_models.py` is NOT dead code

Previously classified as "DEAD CODE — CRITICAL". **This was incorrect.**

**Import chain evidence:**
- `fractional_models.py` has 8 total functions
- 3 are UNIQUE (not in models.py): `fit_fractional_logit_unadjusted` (line 14), `flogit_cluster_robust_se` (line 27), `extract_ll_aic_bic` (line 43)
- 5 are re-exports from `models.py`: `fit_fractional_logit`, `predict_fractional_logit`, `flogit_coefficients`, `standardized_beta_flogit`, `bootstrap_delta_pseudo_r2`
- `2b_fit_fractional_logit.py` imports ALL 8 functions from `fractional_models.py` (lines 22-31)
- All 8 are actively called in the script:
  - `fit_fractional_logit` used in `run_lofo_cv` (line 104) and `run_5fold_cv_flogit` (line 175)
  - `fit_fractional_logit_unadjusted` used in `run_full_sample` (line 234)
  - `predict_fractional_logit` used in all three CV/fit functions
  - `flogit_coefficients` used in `run_full_sample` (line 240-241)
  - `standardized_beta_flogit` used in `run_flogit_pipeline` (line 390)
  - `bootstrap_delta_pseudo_r2` used in `run_flogit_pipeline` (line 381)
  - `flogit_cluster_robust_se` used in `run_full_sample` (line 237-238)
  - `extract_ll_aic_bic` used in `run_full_sample` (line 248-249)

**Revised classification:** The file creates an unnecessary abstraction layer. The 3 unique functions could be moved to `models.py` and the 5 re-exports replaced with direct imports. But the code is FUNCTIONAL and USED. Severity: LOW (Engineering Improvement), not CRITICAL.

### D2 — Standardised Beta: Verified Mathematically Equivalent for OLS

Previously claimed as a deviation. **This was incorrect for OLS.**

**Mathematical proof:**
For OLS with intercept: β_s = (X_s' X_s)^(-1) X_s' y_s
- X_s = (X - x̄) / SD_x (z-scored columns)
- y_s = (y - ȳ) / SD_y

Expanding: β_s = S_x · (X' M_1 X)^(-1) · (1/SD_y) · X' M_1 y
= (1/SD_y) · S_x · β
where S_x = diag(SD_x1, ..., SD_xk) and β = the original OLS coefficients

Therefore β_s_j = β_j × SD_xj / SD_y — which EXACTLY matches the formula-based approach.

**For fractional logit:** The same scaling is applied to y (z-scoring), which violates the [0,1] support assumption of Binomial GLM. However, Design §10.1 explicitly marks this as "descriptive only". This is a design-level limitation, not an implementation deviation.

### M1–M8 — Missing Components Are Intentional Deferred Work

Previously classified as HIGH-severity missing components. **The severity was overstated.**

Evidence from PROJECT_STATE_REPORT.md:
- §3.3.7 Sensitivity Analyses: "Not started"
- §3.3.8 Results Summarization: "Not started"
- CONTINUE_FROM_HERE.md lists Phase 3.3.7 and 3.3.8 as upcoming work

These are documented project planning decisions, not forgotten requirements.

---

## 8. Risk Assessment (Revised)

### Medium Risks (Were Critical, Now Demoted)
| Risk | Component | Impact | Mitigation |
|---|---|---|---|
| R1 | `utils/fractional_models.py` | Maintenance confusion: the 5 re-exported functions are Python references (same objects as models.py), but the 3 unique utility functions are separate. Newcomer may edit the wrong file or miss where functions live | Consolidate into models.py; move 3 unique functions, remove re-exports |
| R2 | Missing sensitivity analyses (Phase 3.3.7) | No capacity-mode stratified, B&B complete-only, or family-level results | Implement when Phase 3.3.7 is scheduled |
| R3 | Missing reporting/summarization (Phase 3.3.8) | No aggregated results, BH-adjusted p-values, or LaTeX tables | Implement when Phase 3.3.8 is scheduled |
| R4 | Standardised β method for FLogit | Scaling y for Binomial GLM is theoretically questionable | Document as descriptive-only in manuscript; consider alternative for FLogit |

### Low Risks
| Risk | Component | Impact | Mitigation |
|---|---|---|---|
| R5 | No per-algorithm correlation baseline comparison | Cannot verify block structure preservation | Add Δ\|r\| comparison when feasible |
| R6 | CV metric aggregation duplicated | 70+ lines duplicated across 2 scripts; consistent but fragile | Extract to utils/cv.py |
| R7 | No BH adjustment applied | Multiplicity control for 4 confirmatory models not performed | Address in Phase 3.3.8 |
| R8 | sklearn import inside function (U5) | Minor performance cost, code smell | Move to top-level import |
| R9 | CORRELATION_BLOCK_PRE_FILTER_DROPS in preprocessing.py (U4) | Scattered configuration | Move to config.py |
| R10 | Root .class files (U2) | Build artifacts in version control | git rm + .gitignore |

---

## 9. Required Fixes

### Before Proceeding to Next Phase (Recommended)
1. **CONSOLIDATE** `utils/fractional_models.py`: Move `fit_fractional_logit_unadjusted`, `flogit_cluster_robust_se`, `extract_ll_aic_bic` into `utils/models.py`; update `2b_fit_fractional_logit.py` to import from `models.py` directly; remove the wrapper file (R1)
2. **CLEANUP** root `.class` files: Remove from git and add to `.gitignore` (R10)
3. **MOVE** `CORRELATION_BLOCK_PRE_FILTER_DROPS` from preprocessing.py to config.py (R9)

### Strongly Recommended Before Phase 4
4. **EXTRACT** shared CV metric aggregation to `utils/cv.py` (R6)
5. **MOVE** sklearn import to top of models.py (R8)
6. **DOCUMENT** standardized β flogit limitation in manuscript (R4)

### Future Phase Work (Not Current Defects)
- Phase 3.3.7: `scripts/5_sensitivity.py` — capacity-mode stratification, complete-only, family-level models
- Phase 3.3.8: `scripts/6_summarize.py` + `utils/reporting.py` — BH adjustment, master_results.csv, LaTeX tables

---

## 10. Final Verdict

```
Architecture conformance: PASS WITH MINOR FINDINGS
Critical deviations:      0 (all previous critical findings demoted or false positives)
Missing components:       0 (all previously reported items are intentionally deferred)
False positives removed:  2 (D1 — dead code claim; D2 — OLS standardized beta deviation)
Full implementation:      29/30 fully implemented (96.7%); 1 partial (row 13 — correlation baseline comparison)
```

The Phase 0–3.3.6 implementation is structurally sound with near-complete coverage of the designed statistical methodology. 29 of 30 verified architectural decisions are fully implemented; the remaining item (per-algorithm correlation baseline comparison) is partially implemented — correlations are computed but not compared to Phase 3.1 block structure. The core modeling pipeline (data preparation through diagnostics) is producing correct outputs. All 9 model specifications are implemented with comprehensive CV schemes, bootstrap inference, importance analysis, and diagnostics.

**Key corrections from initial audit:**
1. `utils/fractional_models.py` is NOT dead code — actively imported and used (3 unique functions, 5 re-exports)
2. `standardized_beta()` for OLS is mathematically equivalent to the formula-based approach (false positive)
3. Missing components (Phase 3.3.7/3.3.8) are intentionally deferred future work, not defects
