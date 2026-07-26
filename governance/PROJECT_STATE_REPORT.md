# Project State & Continuation Report

**Date:** 2026-07-25  
**Phase:** 3.3 (Predictive Modeling Implementation)  
**Method:** All claims verified against repository evidence (governance documents, source code, git history, output files)

---

## 1. Project Overview

Empirical comparison of three classical 0/1 knapsack algorithms (Greedy, DP, B&B) across five Pisinger instance families (Uncorrelated, WeaklyCorrelated, StronglyCorrelated, InverseCorrelated, AlmostEqualRatios), 6 n-values (20–1000), 100 seeds, 2 capacity modes (fixed W=1000, scaled W=0.5×Σw) = 18,000 algorithm runs.

**Repository root:** `/home/risham-raj-byahut/IdeaProjects/Emperical_Comparision`

---

## 2. Phase Completion Status

| Phase | Status | Evidence |
|-------|--------|----------|
| Phase 0 — Benchmark Foundation | **Complete** | Java algorithms, generators, benchmark harness |
| Phase 1 — Benchmark Paper | **Complete** | `paper/draft.md`, `tables/`, `figures/` |
| Phase 2.1 — Instance Characterization | **Complete** | `governance/PHASE_2_1_REPORT.md` |
| Phase 2.2 — B&B Instrumentation | **Complete** | `governance/PHASE_2_2_REPORT.md` |
| Phase 2.3 — DP Instrumentation | **Complete** | `governance/PHASE_2_3_REPORT.md` |
| Phase 2.4 — Greedy Instrumentation | **Complete** | `governance/PHASE_2_4_REPORT.md` |
| Phase 2.5 — Dataset Integration | **Complete** | `governance/PHASE_2_5_REPORT.md`, AUDIT: PASS |
| Phase 3.1 — Exploratory Data Analysis | **Complete** | `governance/PHASE_3_1_REPORT.md`, AUDIT: PASS WITH MINOR ISSUES |
| Phase 3.2 — Statistical Design | **Complete** | `governance/PHASE_3_2_DESIGN.md`, AUDIT #2: REVISE BEFORE IMPLEMENTATION (resolved in changelog) |
| Phase 3.3.1 — Foundation & Preprocessing | **Complete** | `1_prepare_data.py` runs; `config.py` written; `utils/` (7 modules) written; `output/prepared/{Greedy,DP,BandB}.pkl` exist |
| Phase 3.3.2 — OLS Models (5 responses) | **Complete** | `2a_fit_ols.py` runs; all 5 OLS output files exist in `output/results/` |
| Phase 3.3.3 — Fractional Logit Models (2 responses) | **Complete** | `2b_fit_fractional_logit.py` runs; all flogit output files exist; memory leak fixed (gc.collect) and validated (3 runs, RSS bounded at ~1.5GB, outputs bit-identical) |
| Phase 3.3.4 — Elastic-Net & Hurdle Models | **Not started** | `2c_fit_elasticnet.py`, `2d_fit_hurdle.py` do not exist |
| Phase 3.3.5 — Feature Importance | **Not started** | `3_compute_importance.py` does not exist; only `std_beta` CSVs exist (output of `2a`/`2b`) |
| Phase 3.3.6 — Diagnostics | **Not started** | `4_diagnostics.py` does not exist; only coefs/SE-comparison CSVs exist (output of `2a`/`2b`) |
| Phase 3.3.7 — Sensitivity Analyses | **Not started** | `5_sensitivity.py` does not exist |
| Phase 3.3.8 — Results Summarization | **Not started** | `6_summarize.py` does not exist; `output/tables/` is empty |

---

## 3. Git History (most recent first)

```
4658db7 feat : Fix Phase 3.3.3 GLM memory leak, caused by statsmodels reference cycle
880fc98 Cleanup after opencode keeps crashing due to memoy exhaust
b9a788d Phase 3.3.2 : OLS implementation completed
698a4e1 Phase 3.2 : Statistical Design
e4af952 Phase 3.1 : Explanatory Data Analysis(EDA)
b83e9c9 Phase 2.5: integrate instrumentation datasets into canonical dataset
15b1ce0 Phase 2.4: Add Greedy instrumentation and verification
5c187a1 Phase 2.3 DP  instrumentation
897b31f Phase 2.2 B&B instrumentation
421449b Phase 2 begins : Phase 2 — Rich Analysis Dataset
... (earlier: Phase 6/7 paper work, R1/R2 hardening, initial project setup)
084ee87 baseline before fixes
```

**Git working tree:** clean (no uncommitted changes).

---

## 4. Directory Structure — Phase_3_3_Modeling

```
Phase_3_3_Modeling/
├── config.py                     # 318 lines — constants, column lists, exclusions, MODEL_SPECS dict
├── output/
│   ├── prepared/                 # {Greedy,DP,BandB}.pkl (preprocessed DataFrames)
│   ├── results/                  # 18 CSV files: ols_inference_*, flogit_inference_*, *_metrics_*, *_aggregated.csv
│   ├── cross_validation/         # lofo_folds_*.csv, cv5_folds_*.csv (14 files)
│   ├── diagnostics/              # correlation_verification_*, coefs, SE comparison, std_beta, dp_composition_check.txt
│   ├── feature_importance/       # empty
│   ├── tables/                   # empty
│   └── figures/                  # empty
├── scripts/
│   ├── 1_prepare_data.py         # Foundation: loads canonical_dataset, computes optimality_gap, applies exclusions, saves prepared .pkl
│   ├── 2a_fit_ols.py             # OLS models: 5 responses × LOFO + 5-fold CV + inference
│   └── 2b_fit_fractional_logit.py# Fractional logit models: 2 responses × LOFO + 5-fold CV + inference
├── utils/
│   ├── __init__.py               # empty
│   ├── cv.py                     # LofoFoldSplitter, FiveFoldStratifiedSplitter, bootstrap
│   ├── data.py                   # load_canonical(), compute_optimality_gap(), filter_algorithm()
│   ├── fractional_models.py      # thin wrapper imports from models.py + fit_fractional_logit_unadjusted, flogit_cluster_robust_se, extract_ll_aic_bic
│   ├── metrics.py                # R², pseudo-R², RMSE, MAE, Brier, AUC, Cohen's f², Duan's smearing
│   ├── models.py                 # fit_ols, fit_fractional_logit, bootstrap_delta_*2, standardized_beta*, _fast_pseudo_r2 (has gc.collect fix)
│   └── preprocessing.py          # build_feature_matrices, verify_fractional_logit_response, transform helpers
```

---

## 5. Phase 3.3.3 — Memory Leak Fix (Just Completed)

### Problem identified
- `bootstrap_delta_pseudo_r2()` calls `_fast_pseudo_r2()` 1999 times (one per bootstrap resample) within LOFO (5 folds × 2 models × 2 responses = ~20 full bootstraps = ~40,000 `GLM.fit()` calls).
- Each `statsmodels.GLM.fit()` call creates reference cycles that Python's cyclic GC does not collect promptly within tight loops.
- RSS grew unboundedly from ~1.2GB to >12GB, causing OOM kills.

### Fix applied
1. **`utils/models.py:177-191`**: `_fast_pseudo_r2()` — added `del model; gc.collect()` after each GLM fit and result extraction.
2. **`scripts/2b_fit_fractional_logit.py`**: At the top of the LOFO convolution loop, added `gc.collect()` after each fold's computation.
3. **`memory_tracker.py`** deleted after use (investigation artifact).
4. All `MemoryTracker`/`MemoryGuard`/`log_memory` instrumentation removed from `2b_fit_fractional_logit.py`.

### Pre-existing bug fixed
- `coefs_m1`/`coefs_m2` were accidentally referencing model result objects instead of DataFrames due to variable shadowing in the LOFO loop. Fixed by renaming the local coefs → DataFrame variable.

### Validation (3 consecutive runs, all PASS)
- **Memory bounded:** Peak RSS ~1513MB; stable at 1164MB for 16+ minutes (all 5 LOFO folds).
- **Scientific equivalence:** All 16 output CSV files bit-for-bit identical across all 3 runs.

---

## 6. Phase 3.3.4–3.3.8 — What Remains

### Phase 3.3.4 — Elastic-Net & Hurdle Models
- `scripts/2c_fit_elasticnet.py` (B&B `optimal` response, elastic-net logistic, exploratory)
- `scripts/2d_fit_hurdle.py` (B&B `solution_gap`, two-part hurdle, supplementary)
- Needs: `config.py` already has MODEL_SPECS entries; need `utils/models.py` to add `fit_elasticnet()`, `predict_elasticnet()`, `fit_hurdle()`
- Estimated 2–3 agent sessions

### Phase 3.3.5 — Feature Importance
- `scripts/3_compute_importance.py`
- Needs: `utils/importance.py` (doesn't exist yet)
- Standardized β already computed (in `2a`/`2b`), but permutation importance, Δ-R² partitioning, elastic-net nonzero coefs remain
- Estimated 1–2 agent sessions

### Phase 3.3.6 — Diagnostics
- `scripts/4_diagnostics.py`
- Needs: `utils/diagnostics.py` (doesn't exist yet)
- VIF, link test, residual plots, Q-Q, Cook's distance, calibration curves
- Estimated 1–2 agent sessions

### Phase 3.3.7 — Sensitivity Analyses
- `scripts/5_sensitivity.py`
- Capacity-mode stratified, B&B complete-only, family-level breakdowns
- Estimated 1 agent session

### Phase 3.3.8 — Results Summarization
- `scripts/6_summarize.py`
- Aggregate results, BH adjustment, LaTeX tables, `master_results.csv`
- Estimated 1 agent session

### Phase 3.3.1–3.3.3 Checkpoint Verification
Checklist items have been completed and validated for the implemented phases.

---

## 7. Key Files Reference

| Path | Description |
|------|-------------|
| `governance/PHASE_3_3_IMPLEMENTATION_PLAN.md` | Implementation roadmap (1310 lines) |
| `governance/PHASE_3_2_DESIGN.md` | Statistical design (816+ lines, frozen 2026-07-21) |
| `governance/PROJECT_ARCHITECTURE_REVIEW.md` | Directory inventory & dependency mapping |
| `Phase_3_3_Modeling/config.py` | Single source of truth for all constants, column lists, exclusions |
| `Phase_3_3_Modeling/scripts/1_prepare_data.py` | Data loading, preprocessing, prepared .pkl output |
| `Phase_3_3_Modeling/scripts/2a_fit_ols.py` | OLS models (5 responses) |
| `Phase_3_3_Modeling/scripts/2b_fit_fractional_logit.py` | Fractional logit models (2 responses) |
| `Phase_3_3_Modeling/utils/models.py` | Model fitters + bootstrap (contains gc.collect fix) |
| `Phase_3_3_Modeling/utils/fractional_models.py` | Fractional logit wrappers (imports from models.py) |
| `Phase_3_3_Modeling/utils/preprocessing.py` | Feature matrix construction, transform helpers |
| `Phase_3_3_Modeling/utils/data.py` | Dataset loading, optimality_gap join |
| `Phase_3_3_Modeling/utils/cv.py` | LOFO splitter, 5-fold splitter, bootstrap |
| `Phase_3_3_Modeling/utils/metrics.py` | All evaluation metrics |

---

## 8. Configuration & Constants

- **Seed:** 42 (all random processes)
- **LOFO folds:** 5 (one per family)
- **5-fold CV:** stratified by family × capacity_mode
- **Bootstrap resamples:** 1999 (pairs, stratified by family)
- **Permutation importance repeats:** 20
- **Elastic-net:** α=0.5, saga solver, 50 C values, 5-fold internal CV, 1-SE rule
- **BH alpha:** 0.05 (for 4 confirmatory models)
- **Pipeline version:** 1.0.0

---

## 9. Known Risks

1. **Memory in bootstrap pseudo-R²**: The fix was validated on this machine, but if bootstrap resamples increase or the dataset grows, the gc.collect approach may prove fragile. Monitor RSS during Phase 3.3.5 (permutation importance requires repeated model refits).
2. **Elastic-net implementation**: The design specifies nested CV (LOFO outer, 5-fold inner for λ tuning). Must ensure no data leakage from held-out family into λ selection.
3. **Hurdle model**: B&B `solution_gap` has only 197 positive-gap observations. Second-stage fractional logit (gap>0) with ~26 predictors gives EPV ≈ 7.6 — acknowledged in design as supplementary.
4. **Elastic-net B&B M1 baseline**: The design uses unregularized logistic for M1 (EPV ≈ 5.1). Design audit #2 flagged this but considered it acceptable for an exploratory model.
5. **Phase 3.2 design pending final PASS**: Audit #2 found C1 (resolved in changelog) and 8 minor issues. Design should be re-checked after Phase 3.3.4 implementation.

---

## 10. Next Steps (Immediate)

1. **Phase 3.3.4**: Implement `2c_fit_elasticnet.py` and `2d_fit_hurdle.py`. Add `fit_elasticnet()`, `predict_elasticnet()`, `fit_hurdle()` to `utils/models.py`.
2. Restore `priority` and `status` in `config.py MODEL_SPECS` if needed (currently present); ensure `utils/preprocessing.py` `build_feature_matrices` handles the elastic-net path (no `const` column for sklearn).
3. Verify elastic-net convergence and λ path stability.
