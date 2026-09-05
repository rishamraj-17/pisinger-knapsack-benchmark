# Project Architecture Review

**Review Date:** 2026-07-25
**Reviewer:** Automated architecture analysis
**Scope:** Full repository walkthrough, dependency graph, phase mapping, code health, design conformity
**Phase gates:** All phases from Phase 0 through Phase 3.3.2 (frozen)

---

## 1. Repository Overview

### 1.1 Project Identity

- **Project:** Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics
- **Language:** Java 17 (experiment engine) + Python 3.11+ (analysis pipeline)
- **Version:** 2.0.0
- **Total tracked files:** ~180 (excluding build artifacts, virtual envs, caches)
- **Repository structure age:** Evolved over Phases 0–3.3.2

### 1.2 Directory Inventory

| Directory | Phase | Status | Size | Purpose |
|-----------|-------|--------|------|---------|
| `src/main/java/` | Phase 0 | Active | 23 `.java` files | Core experiment: algorithms, generators, benchmark, harness |
| `lib/` | Phase 0 | Active | 1 JAR | External dependency (commons-csv) |
| `out/` | Phase 0 | Mixed | 2 CSV + ~40 `.class` | Experiment output (CSV Active, `.class` temp build artifacts) |
| `tables/` | Phase 1 | Active | 14 files (12 `.tex` + 2 `.csv`) | Canonical paper tables |
| `figures/` | Phase 1 | Active | 36 image files | Publication figures (6 types × 2 modes × 3 formats) |
| `paper/` | Phase 2 | Active | 1 file | `draft.md` — manuscript |
| `docs/` | Phase 2.1 | Active | 1 file | `INSTANCE_FEATURES.md` — canonical dataset schema |
| `results/` | Phase 2.1 | Legacy | 4 CSV | Pre-canonical feature extraction (superseded by canonical_dataset.csv) |
| `eda_output/` | Phase 3.1 | Active | ~139 files | EDA diagnostics (summary stats, boxplots, histograms) |
| `Phase_3_3_Modeling/` | Phase 3.3 | Active/Dev | ~50+ files | Statistical modeling pipeline (current development phase) |
| `governance/` | Phase 2 | Active | 18 `.md` files | Phase reports, audits, design docs, roadmap |
| Root-level | Mixed | Mixed | ~25 files | Scripts, config, tests, patches |
| `venv/`, `Phase_3_3_Modeling/.venv/` | Mixed | Temporary | 2 dirs | Python virtual environments |
| `target/` | Phase 0 | Empty | — | Maven build output (empty) |

### 1.3 Phase Status Summary

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 (Benchmark) | ✅ Complete | Algorithms, generators, harness, CSV output |
| Phase 1 (Paper) | ✅ Complete | Analysis, figures, tables, manuscript |
| Phase 2.1 (Instance Characterization) | ✅ Complete | Feature extraction, `instances.csv` |
| Phase 2.2 (B&B Instrumentation) | ✅ Complete | Instrumented B&B in Java |
| Phase 2.3 (DP Instrumentation) | ✅ Complete | Instrumented DP in Java |
| Phase 2.4 (Greedy Instrumentation) | ✅ Complete | Instrumented Greedy in Java |
| Phase 2.5 (Dataset Assembly) | ✅ Complete | Canonical dataset CSV |
| Phase 2.6 (Dataset Validation) | ❓ Status unclear | No dedicated report/audit found |
| Phase 3.1 (EDA) | ✅ Complete | EDA report, audit passed |
| Phase 3.2 (Statistical Design) | ✅ Complete | Design doc frozen, audited |
| Phase 3.3.1 (Foundation) | ✅ Complete | Config, utils, data prep pipeline |
| Phase 3.3.2 (OLS Models) | ✅ Complete | 5 OLS models, audited, committed |
| Phase 3.3.3 (Fractional Logit) | 🔄 Implemented | Script exists, output not yet audited |
| Phases 3.3.4–3.3.8 | ❌ Not started | Elastic-net, hurdle, importance, diagnostics, sensitivity, reporting |
| Phase 4 (Research Questions) | ❌ Not started | — |
| Phase 5 (Novel Paper) | ❌ Not started | — |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       Phase 0  (Java)                           │
│  src/main/java/                                                 │
│  ├── algorithms/*.java     (Greedy, DP, BB + instrumented)      │
│  ├── dataset/*.java        (Generators, DatasetGenerator)       │
│  ├── benchmark/*.java      (Runners, ResultsExporter)           │
│  ├── model/*.java          (Item, KnapsackInstance, Result)     │
│  ├── Main.java             (Entry point)                        │
│  └── TimeoutValidation.java                                     │
└──────────────┬──────────────────────────────────────────────────┘
               │  build_and_run.sh / reproduce.sh
               ▼
┌─────────────────────────────────────────────────────────────────┐
│              out/results/ (CSV output)                           │
│  full_experiment.csv → canonical_dataset.csv                    │
└──────────────┬──────────────────────────────────────────────────┘
               │  input
               ▼
┌─────────────────────────────────────────────────────────────────┐
│               Phase 1 + 2  (Python analysis)                    │
│                                                                  │
│  analyze.py ────→ tables/*.tex, figures/*                       │
│  figures.py ────→ figures/fixed/*, figures/scaled/*             │
│  plot_utils.py ←── shared utilities for above                   │
│  extract_features.py ──→ results/instances.csv (legacy)         │
│  eda_phase3_1.py ──→ eda_output/                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│          Phase 3.3  (current development)                        │
│  Phase_3_3_Modeling/                                             │
│                                                                  │
│  config.py  ←─── single source of truth                         │
│      │                                                           │
│      ├──→ utils/data.py  (loading, filtering, gap computation)  │
│      ├──→ utils/preprocessing.py (transforms, encoding,         │
│      │                           correlation, block filter)     │
│      ├──→ utils/cv.py  (LOFO, 5-fold, bootstrap splitters)     │
│      ├──→ utils/metrics.py  (R², RMSE, MAE, AUC, smearing)     │
│      ├──→ utils/models.py  (OLS + FRACTIONAL LOGIT + bootstrap) │
│      ├──→ utils/fractional_logit.py  ⚠ DUPLICATE                │
│      ├──→ [utils/importance.py]  ❌ not yet created              │
│      ├──→ [utils/diagnostics.py]  ❌ not yet created             │
│      └──→ [utils/reporting.py]    ❌ not yet created             │
│                                                                  │
│  scripts/                                                        │
│  ├── 1_prepare_data.py          [Phase 3.3.1]  ✅               │
│  ├── 2a_fit_ols.py              [Phase 3.3.2]  ✅               │
│  ├── 2b_fit_fractional_logit.py [Phase 3.3.3]  🔄               │
│  ├── [2c_fit_elasticnet.py]     [Phase 3.3.4]  ❌               │
│  ├── [2d_fit_hurdle.py]         [Phase 3.3.4]  ❌               │
│  ├── [3_compute_importance.py]  [Phase 3.3.5]  ❌               │
│  ├── [4_diagnostics.py]         [Phase 3.3.6]  ❌               │
│  ├── [5_sensitivity.py]         [Phase 3.3.7]  ❌               │
│  └── [6_summarize.py]           [Phase 3.3.8]  ❌               │
│                                                                  │
│  output/                                                         │
│  ├── prepared/     {Greedy,DP,BandB}.pkl   [3.3.1]              │
│  ├── results/      12 CSV files            [3.3.2]              │
│  ├── cross_validation/  10 CSV files       [3.3.2]              │
│  ├── diagnostics/  19 CSV + 1 TXT          [3.3.1+3.3.2]        │
│  ├── feature_importance/  (empty)          [future]              │
│  ├── figures/            (empty)           [future]              │
│  └── tables/             (empty)           [future]              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Phase-to-File Mapping

### 3.1 Phase 3.3.1 — Foundation and Preprocessing Pipeline

| File | Role | Implementation Plan Reference |
|------|------|-----------------------------|
| `Phase_3_3_Modeling/config.py` | Constants, column lists, model specs | §1.1 (Config), §1.3 (Model Specs) |
| `Phase_3_3_Modeling/utils/data.py` | load_canonical, filter_algorithm, compute_optimality_gap, compute_solution_gap | §1.2 Table row 2 |
| `Phase_3_3_Modeling/utils/preprocessing.py` | Transforms, encoding, exclusions, block filter, feature matrix building | §1.2 Table row 3, §4.1 Pipeline |
| `Phase_3_3_Modeling/utils/cv.py` | LofoFoldSplitter, FiveFoldStratifiedSplitter, stratified_bootstrap | §1.2 Table row 4, §8 |
| `Phase_3_3_Modeling/utils/metrics.py` | R², RMSE, MAE, Cohen's f², Duan smearing, AUC, Brier | §1.2 Table row 5, §9 |
| `Phase_3_3_Modeling/scripts/1_prepare_data.py` | Orchestrates 12-step pipeline | §2.1 Steps |

Also produces:
- `output/prepared/{Greedy,DP,BandB}.pkl`
- `output/diagnostics/correlation_verification_{algo}.csv`
- `output/diagnostics/dp_composition_check.txt`

### 3.2 Phase 3.3.2 — OLS Models

| File | Role | Implementation Plan Reference |
|------|------|-----------------------------|
| `Phase_3_3_Modeling/utils/models.py` | fit_ols, predict_ols, ols_coefficients, cluster_robust_se, incremental_f_test, standardized_beta, bootstrap_delta_r2, bootstrap_delta_pseudo_r2 | §2.2 Steps 1 |
| `Phase_3_3_Modeling/scripts/2a_fit_ols.py` | LOFO CV, 5-fold CV, full-sample fit, bootstrap ΔR², back-transformed RMSE | §2.2 Steps 2 |

Produces:
- `output/results/ols_metrics_{algo}_{response}.csv` (5 per-model + 1 aggregated)
- `output/results/ols_inference_{algo}_{response}.csv` (5 per-model + 1 aggregated)
- `output/cross_validation/lofo_folds_{algo}_{response}.csv` (5)
- `output/cross_validation/cv5_folds_{algo}_{response}.csv` (5)
- `output/diagnostics/full_sample_coefs_{algo}_{response}_{M1,M2}.csv` (10)
- `output/diagnostics/std_beta_{algo}_{response}_M2.csv` (5)

### 3.3 Phase 3.3.3 — Fractional Logit Models

| File | Role | Implementation Plan Reference |
|------|------|-----------------------------|
| `Phase_3_3_Modeling/utils/models.py` | fit_fractional_logit, predict_fractional_logit, flogit_coefficients, standardized_beta_flogit, bootstrap_delta_pseudo_r2 | §2.3 Step 1 |
| `Phase_3_3_Modeling/utils/preprocessing.py` | verify_fractional_logit_response | §2.3 Step 2 |
| `Phase_3_3_Modeling/scripts/2b_fit_fractional_logit.py` | LOFO CV, full-sample fit, bootstrap Δ pseudo-R², SE comparison | §2.3 Step 3 |
| `Phase_3_3_Modeling/utils/fractional_logit.py` | ⚠ DUPLICATE of functions in models.py | Not part of plan |

### 3.4 Phases 3.3.4–3.3.8

| Phase | Script | Utility Module | Status |
|-------|--------|----------------|--------|
| 3.3.4 (Elastic-Net) | `scripts/2c_fit_elasticnet.py` | `utils/models.py` (extend) | ❌ Not created |
| 3.3.4 (Hurdle) | `scripts/2d_fit_hurdle.py` | `utils/models.py` (extend) | ❌ Not created |
| 3.3.5 (Feature Importance) | `scripts/3_compute_importance.py` | `utils/importance.py` | ❌ Not created |
| 3.3.6 (Diagnostics) | `scripts/4_diagnostics.py` | `utils/diagnostics.py` | ❌ Not created |
| 3.3.7 (Sensitivity) | `scripts/5_sensitivity.py` | Reuses existing utils | ❌ Not created |
| 3.3.8 (Reporting) | `scripts/6_summarize.py` | `utils/reporting.py` | ❌ Not created |

---

## 4. Dependency Graph

### 4.1 Module Import Dependencies

```
scripts/1_prepare_data.py
  ├── config.py
  ├── utils/data.py ──→ config.py
  └── utils/preprocessing.py ──→ config.py

scripts/2a_fit_ols.py
  ├── config.py
  ├── utils/models.py ──→ (statsmodels, scipy, sklearn)
  ├── utils/preprocessing.py ──→ config.py
  ├── utils/cv.py ──→ config.py, sklearn
  └── utils/metrics.py ──→ sklearn

scripts/2b_fit_fractional_logit.py
  ├── config.py
  ├── utils/models.py ──→ (statsmodels, scipy)
  ├── utils/preprocessing.py ──→ config.py
  ├── utils/cv.py ──→ config.py
  └── utils/metrics.py ──→ sklearn
```

### 4.2 Dependency Rules (verified)

- **No circular dependencies** detected. All imports flow from scripts → utils → config.
- **config.py has zero imports** from utils or scripts — it is a pure constant module.
- **No coupling between utility modules** — utils/data.py does not import utils/models.py, etc.
- **Scripts never import each other** — each script is independently runnable.
- **External packages:** statsmodels, scikit-learn, scipy, pandas, numpy, matplotlib (not yet imported but needed for diagnostics/figures).

### 4.3 Hidden Dependency

`utils/models.py` imports `sklearn.linear_model.LinearRegression` inside a private function (`_fast_r2`) rather than at module top level. This is a minor code smell — sklearn is already an explicit dependency in the design, so it should be a top-level import.

---

## 5. Code Health Review

### 5.1 Duplicated Code (Critical)

**5.1.1 `utils/models.py` vs `utils/fractional_logit.py`**

Five functions are duplicated across these two files:

| Function | models.py lines | fractional_logit.py lines |
|----------|-----------------|--------------------------|
| `fit_fractional_logit` | 101-107 | 31-36 |
| `predict_fractional_logit` | 109-113 | 38-42 |
| `flogit_coefficients` | 115-134 | 44-62 |
| `standardized_beta_flogit` | 73-84 | 129-141 |
| `bootstrap_delta_pseudo_r2` | 148-177 | 104-127 |

Additionally:
- `_fast_pseudo_r2` is duplicated (models.py:136-146, fractional_logit.py:100-108)
- `cluster_robust_se_flogit` exists only in `fractional_logit.py` (64-72) — not used by anything

**Impact:** If bug fixes are applied to one copy but not the other, results will silently diverge. The `2b_fit_fractional_logit.py` script imports from `utils.models` (not `fractional_logit.py`), so `fractional_logit.py` is dead code.

**Severity:** HIGH. The unused file `fractional_logit.py` must be removed (or consolidated) before Phase 3.3.4.

**5.1.2 CV logic duplication across scripts**

The `_compute_cv_metrics` and `_aggregate_cv_metrics` helper functions are independently defined in both `2a_fit_ols.py` and `2b_fit_fractional_logit.py` with near-identical structure. These should be in a shared utility module.

**Severity:** MEDIUM. Duplicated but stable logic; low risk of divergence.

### 5.2 Dead Code

| File | Issue | Severity |
|------|-------|----------|
| `utils/fractional_logit.py` | Entire file is dead code (157 lines, 10 functions) — not imported by any script | HIGH |
| `CompareBound.java` (root) | Stub/test file, appears unfinished | LOW |
| `bb_diff.patch` (root) | Git patch, should not be in working tree | LOW |
| Root `.class` files | Build artifacts checked into version control | MEDIUM |

### 5.3 Empty Placeholder Directories

Three output subdirectories exist with no content:
- `Phase_3_3_Modeling/output/feature_importance/`
- `Phase_3_3_Modeling/output/figures/`
- `Phase_3_3_Modeling/output/tables/`

These are intentional placeholders for future phases. No action needed.

### 5.4 Naming Inconsistencies

| Location | Name Used | Design Document Name | Issue |
|----------|-----------|---------------------|-------|
| `config.py:ALGO_BB` | `"BranchAndBound"` | `"B&B"` | OK for code, but prepared file is `BandB.pkl` |
| `config.py:ALGORITHM_LABEL_MAP` | `"BandB"` for BB | `"B&B"` | `BandB` is a compromise for filesystem safety but inconsistent with `"Greedy"` and `"DP"` patterns |
| Prepared filenames | `BandB.pkl` | `B&B.pkl` would be file-error | Acceptable compromise |
| `utils/preprocessing.py:CORRELATION_BLOCK_PRE_FILTER_DROPS` | Module-level list | Should be in `config.py` | Functionality drift — config defines `CORRELATION_BLOCK_DROPS` but the actual drops are also hardcoded in preprocessing.py |
| `config.py:MODEL_SPECS` keys | `(ALGO_BB, "log_time_millis")` etc. | Uses canonical names | Consistent ✅ |

### 5.5 Oversized Modules

| Module | Lines | Assessment |
|--------|-------|------------|
| `scripts/2a_fit_ols.py` | 555 | Large but cohesive — a single pipeline script |
| `config.py` | 318 | Appropriate for single-source-of-truth configuration |
| `utils/preprocessing.py` | 315 | Contains `build_feature_matrices` which is arguably a modeling concern |
| `utils/models.py` | 273 | Contains both OLS and fractional logit functions — will grow further with elastic-net and hurdle (Phase 3.3.4). Consider splitting by model family. |

### 5.6 Responsibility Drift

`build_feature_matrices` in `utils/preprocessing.py`:
- This function builds model-specific feature matrices, processes model specs, resolves M2 labels, and applies exclusions.
- It is called by both `2a_fit_ols.py` and `2b_fit_fractional_logit.py`.
- Despite being in `preprocessing.py`, it serves as a bridge between preprocessing and modeling.
- **Recommendation:** Move to `utils/models.py` or a new `utils/features.py` in the future.

### 5.7 Potential Technical Debt for Later Phases

1. **No error handling for missing packages** — scripts will crash with `ModuleNotFoundError` if statsmodels or sklearn are not installed.
2. **No logging framework** — uses `print()` statements. Fine for now but will become unwieldy with parallelism in bootstrap.
3. **Bootstrap parallelization** — the 1999-resample bootstrap is serial. For Phase 3.3.5 (20 repeats × ~18 models), permutation importance will be slow.
4. **No VIF computation yet** — the design specifies VIF as a post-fit diagnostic (§6.2 step 3), but `utils/diagnostics.py` doesn't exist yet.
5. **Fractional logit in two places** — before Phase 3.3.4 adds elastic-net and hurdle to `models.py`, the duplication must be resolved or it will triple.

---

## 6. Design Conformity Report

Deviations from the frozen Phase 3.2 Design (`PHASE_3_2_DESIGN.md`) and the Phase 3.3 Implementation Plan (`PHASE_3_3_IMPLEMENTATION_PLAN.md`).

### 6.1 Deviations from Implementation Plan (PHASE_3_3_IMPLEMENTATION_PLAN.md)

| # | Design Requirement | Implementation | Deviation | Severity | Type |
|---|---|---|---|---|---|
| D1 | `utils/fractional_logit.py` should NOT exist — fractional logit functions should be in `utils/models.py` (Plan §1.2, §2.3 step 1) | Separate `utils/fractional_logit.py` created with 5 duplicated functions | ⚠ File created contrary to plan. Functions duplicated. | HIGH | Unintentional |
| D2 | `utils/models.py` should contain `fit_elasticnet`, `predict_elasticnet`, `fit_hurdle`, `predict_hurdle` (Plan §2.4 step 1) | Not yet implemented | ✅ Expected for future phase | — | Not yet due |
| D3 | `utils/importance.py` should contain standardized_beta, permutation_importance, delta_r2_partitioning, elasticnet_nonzero_coefs (Plan §2.5 step 1) | Not yet created | ✅ Expected for future phase | — | Not yet due |
| D4 | `utils/diagnostics.py` should contain VIF, residual plots, Q-Q, link test, etc. (Plan §2.6 step 1) | Not yet created | ✅ Expected for future phase | — | Not yet due |
| D5 | `utils/reporting.py` should contain bh_adjust, latex_primary_table, etc. (Plan §2.7 step 1) | Not yet created | ✅ Expected for future phase | — | Not yet due |
| D6 | Correlation verification should compare per-algorithm matrices to pooled Phase 3.1 block structure and report Δ\|r\| > 0.10 (Plan §4.1 step 9) | `compute_per_algorithm_correlation` dumps all pairwise correlations but does not compare to Phase 3.1 baseline | ⚠ Missing comparative step | MEDIUM | Unintentional |
| D7 | Model specs should use `'m2_predictors'` key with labels like `'all_greedy'`, `'bb_minus_bound_exclusions'` (Plan §1.3) | Uses `'m2_predictor_label'` (singular) with same values | ✅ Naming difference only — no functional impact | LOW | Harmless |
| D8 | Plan §3.4: DP `log_memory_mb` model-specific exclusions should list `['cells_allocated', 'nonzero_value_states', 'zero_value_states']` | Implemented identically in `MODEL_SPECIFIC_EXCLUSIONS` | ✅ Conforms | — | — |
| D9 | Plan §2.2 step 2f: Standardised β should be computed as "β = coef × (SD_x / SD_y)" or by refitting on scaled data | `standardized_beta` refits OLS on scaled X and scaled y — produces different β than the formula method | ⚠ Refitting on scaled y gives standardized β for the *scaled* y, not the original y. The formula β = coef × (SD_x / SD_y) using the original model's coefficients would be the standard approach | MEDIUM | Potential future problem |
| D10 | Plan §4.1 step 11: Block 4 variables (`mean_bound`, `max_bound`, `min_bound`) should be handled as structural exclusions per-model, not in correlation-block pre-filter | `CORRELATION_BLOCK_PRE_FILTER_DROPS` does NOT include Block 4 — they are applied per-model in `build_feature_matrices` via exclusions | ✅ Conforms | — | — |

### 6.2 Deviations from Phase 3.2 Design (PHASE_3_2_DESIGN.md)

| # | Design Requirement | Implementation | Deviation | Severity | Type |
|---|---|---|---|---|---|
| D11 | §4.3: `instance_id` should be retained for cluster-robust SE grouping but never enter predictor matrix | Retained in DataFrame, excluded from feature matrices via `_get_m1_base_columns` and `_get_group_a_columns` | ✅ Conforms | — | — |
| D12 | §5.2: `selected_count` (Greedy) should use "None or sqrt" transform | No transform applied to `selected_count` — it is not in `PREDICTOR_LOG_TRANSFORM` | ✅ Acceptable — left untransformed as per "None" option | LOW | Harmless |
| D13 | §6.2 step 2: Per-algorithm correlation Δ\|r\| > 0.10 should be reported | Not implemented (same as D6) | ⚠ Missing | MEDIUM | Unintentional |
| D14 | §7.2: M2 for B&B `log_time_millis` should have "~21 B&B metrics (24 minus 3 bound metrics)" | Implemented as `bb_minus_bounds` label computing BB_METRICS minus `mean_bound/max_bound/min_bound` | ✅ Conforms exactly | — | — |
| D15 | §12: Capacity-mode stratification, B&B complete-only sensitivity, family-level models | Not yet implemented (Phase 3.3.7) | ✅ Expected | — | Not yet due |

### 6.3 Classification Summary

| Category | Count | Items |
|----------|-------|-------|
| **Critical deviations** | 1 | D1: duplicated fractional_logit.py dead code |
| **Medium deviations** | 2 | D6/D13: correlation verification incomplete; D9: standardized β implementation may differ from design |
| **Harmless deviations** | 2 | D7: key name difference; D12: transform choice within spec |
| **Expected not-yet-implemented** | 6 | D2-D5, D15: future phases |

---

## 7. Technical Debt Register

| ID | Item | Location | Impact | Effort to Fix | Recommended Timing |
|----|------|----------|--------|--------------|--------------------|
| TD1 | Dead file `utils/fractional_logit.py` | `Phase_3_3_Modeling/utils/` | Confusion, maintenance burden, potential divergent results | 15 min delete | **Before Phase 3.3.3** |
| TD2 | `CORRELATION_BLOCK_PRE_FILTER_DROPS` defined in preprocessing.py instead of config.py | `preprocessing.py:42-48` | Scattered configuration | 5 min move to config | After Phase 3.3.8 |
| TD3 | CV metric aggregation duplicated across 2 scripts | `2a_fit_ols.py`, `2b_fit_fractional_logit.py` | 70+ lines duplicated | 30 min extract to utils/cv.py | After Phase 3.3.8 |
| TD4 | sklearn imported inside function body | `models.py:_fast_r2` | Code smell, minor performance cost | 2 min move to top | After Phase 3.3.8 |
| TD5 | Root `.class` files tracked in git | Root directory | Build artifacts in version control | 5 min git rm + .gitignore update | Before Phase 3.3.3 |
| TD6 | `bb_diff.patch` in working tree | Root directory | Not a source file | 1 min delete | Before Phase 3.3.3 |
| TD7 | Standardised β method may differ from design formula | `models.py:standardized_beta` | Scientifically different interpretation if design expects formula-based β | 30 min verify | After Phase 3.3.8 (during review) |
| TD8 | No logging framework, all print-based | All scripts | Hard to debug, no log levels, no file output | 1 hour add logging | After Phase 3.3.8 |
| TD9 | Bootstrap is serial | `models.py:bootstrap_delta_r2` | Will be slow for Phase 3.3.5 (~18000 refits) | Several hours parallelize | Before Phase 3.3.5 |
| TD10 | No input validation in config.py | config.py | Type errors caught late | 30 min add type assertions | After Phase 3.3.8 |

---

## 8. Recommendations

### 8.1 Fix Before Phase 3.3.3 (Required)

| # | Recommendation | Reason | Expected Benefit | Difficulty |
|---|---|---|---|---|
| R1 | **Delete `utils/fractional_logit.py`** | Dead code with duplicated functions. `2b_fit_fractional_logit.py` imports from `utils.models`, not this file. | Eliminates maintenance burden and risk of divergence | Trivial |
| R2 | **Remove root `.class` files from git** | Build artifacts pollute version control. All 6 `*.class` files at root are compiled from root-level test stubs. | Cleaner repository, no spurious diffs | Trivial |
| R3 | **Remove `bb_diff.patch` from working tree** | Temporary patch file that should not be in source control | Cleaner repository | Trivial |

### 8.2 Fix Before Phase 3.3.5 (Recommended)

| # | Recommendation | Reason | Expected Benefit | Difficulty |
|---|---|---|---|---|
| R4 | **Parallelize bootstrap** | Phase 3.3.5 needs ~18000 refits for permutation importance. Serial will take ~20+ minutes. | Practical runtime reduction | Medium |
| R5 | **Add logging framework** | Current `print()` statements will be inadequate for debugging Phase 3.3.4 (nested CV elastic-net) | Better debugging, file-based logs | Medium |

### 8.3 Fix After Phase 3.3.8 (Optional)

| # | Recommendation | Reason | Expected Benefit | Difficulty |
|---|---|---|---|---|
| R6 | **Extract `build_feature_matrices` from preprocessing.py to `utils/features.py`** | Responsibility drift — feature matrix building is a modeling concern | Clearer module boundaries | Low |
| R7 | **Move `CORRELATION_BLOCK_PRE_FILTER_DROPS` to config.py** | Configuration scattered across modules | Single source of truth | Trivial |
| R8 | **Extract shared CV metric aggregation** | `_compute_cv_metrics` and `_aggregate_cv_metrics` duplicated in 2 scripts | Reduced duplication | Low |
| R9 | **Verify standardized β formula** | Check if implementation matches design intent (refit on scaled y vs. formula β = coef × SD_x/SD_y) | Scientific correctness | Low |

### 8.4 Organization Observations

1. **The governance/ directory is well-structured** — each phase has audited reports. Continue this pattern.
2. **Script numbering is clear** — `1_`, `2a_`, `2b_`, etc. This makes the execution order obvious. Maintain this.
3. **Output directory structure mirrors the plan** — `results/`, `cross_validation/`, `diagnostics/`, `figures/`, `tables/` is well-organized.
4. **Config-driven model specification** is a good pattern. The `MODEL_SPECS` dict at config.py:238-283 cleanly separates model definitions from fitting logic.

---

## 9. Final Verdict

```
Architecture is clean but has one critical issue that must be resolved
before proceeding to Phase 3.3.3.
```

**Required actions before Phase 3.3.3:**

1. **REMOVE** `Phase_3_3_Modeling/utils/fractional_logit.py` — it is dead code duplicating functions in `utils/models.py`. All 5 fractional logit functions in `models.py` are complete and used by `2b_fit_fractional_logit.py`.

2. **CLEAN** tracked build artifacts (root `.class` files, `bb_diff.patch`).

**Optional but recommended before Phase 3.3.4:**

3. Consolidate histogram/exclusion column lists to eliminate the `sorted(set(...))` redundancy at `config.py:166`.

The architecture is otherwise well-structured for the remaining phases (3.3.3–3.3.8). The planned utility modules (`importance.py`, `diagnostics.py`, `reporting.py`) and scripts (`2c_` through `6_`) have clear specifications in the implementation plan and can be created following the established patterns.
