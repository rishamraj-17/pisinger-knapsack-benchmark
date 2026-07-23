# Phase 3.3 — Implementation Plan

**Derived from:** `governance/PHASE_3_2_DESIGN.md` (frozen, 818 lines)
**Frozen design date:** 2026-07-21
**Plan date:** 2026-07-21
**Status:** Planning — no code written yet

This document is the sole implementation roadmap for Phase 3.3. No methodology changes,
redesigns, or optimisations are permitted unless implementation proves something impossible.
Every deviation must be documented and approved against the design.

---

## Table of Contents

1. Overall Architecture
2. Execution Order — Milestones
3. Model Implementation Roadmap
4. Common Preprocessing Pipeline
5. Output Organisation
6. Verification Checkpoints
7. Risk Assessment
8. Final Deliverable

---

## 1. Overall Architecture

### 1.1 Directory Structure

```
Phase_3_3_Modeling/
├── config.py                     # Constants, column lists, exclusion tables,
│                                 #   transform mappings, model specifications
├── utils/
│   ├── __init__.py
│   ├── data.py                   # Data loading, filtering, optimality_gap join
│   ├── preprocessing.py          # Transforms, encoding, exclusion application,
│   │                             #   correlation-block pre-filtering
│   ├── cv.py                     # LOFO splitter, 5-fold splitter, bootstrap
│   │                             #   resampler (stratified by family)
│   ├── metrics.py                # R², pseudo-R², RMSE, MAE, Brier, AUC,
│   │                             #   back-transformed RMSE, Cohen's f²,
│   │                             #   Duan's smearing
│   ├── models.py                 # OLS fitter, fractional logit fitter,
│   │                             #   elastic-net fitter (nested CV),
│   │                             #   hurdle model fitter
│   ├── importance.py             # Standardised β, permutation importance,
│   │                             #   Δ-R² partitioning, elastic-net nonzeros
│   ├── diagnostics.py            # Residual plots, Q-Q, VIF, link test,
│   │                             #   calibration curve, Cook's distance,
│   │                             #   assumption tests
│   └── reporting.py              # LaTeX table generation, BH adjustment,
│                                 #   result aggregation
├── scripts/
│   ├── 1_prepare_data.py         # Foundation, preprocessing, correlation-block filter
│   ├── 2a_fit_ols.py             # OLS models (5 continuous responses)
│   ├── 2b_fit_fractional_logit.py# Fractional logit models (2 responses)
│   ├── 2c_fit_elasticnet.py      # Elastic-net logistic (B&B optimal)
│   ├── 2d_fit_hurdle.py          # Two-part hurdle (B&B solution_gap)
│   ├── 3_compute_importance.py   # All feature importance analyses
│   ├── 4_diagnostics.py          # All diagnostic checks and plots
│   ├── 5_sensitivity.py          # Stratified and sensitivity analyses
│   └── 6_summarize.py            # Aggregate, BH adjust, produce tables
└── output/                       # All generated outputs (see §5)
```

### 1.2 Reusable Utilities

All shared logic lives in `utils/`. Every script imports from these modules rather
than duplicating logic. The utility modules are:

| Module | Key Functions | Purpose |
|--------|--------------|---------|
| `config.py` | — | Single source of truth for all constants: column lists by group, exclusion lists by model, transform mappings, model spec dict (algorithm, response, family, link, status, predictors, exclusions), CV parameters, BH alpha, random seed |
| `data.py` | `load_canonical()`, `filter_algorithm()`, `compute_optimality_gap()`, `merge_optimal_value()` | Loads `canonical_dataset.csv`; filters to one algorithm; performs DP-join to compute Greedy's `optimality_gap` |
| `preprocessing.py` | `apply_global_exclusions()`, `apply_model_exclusions()`, `log_transform()`, `arctanh_transform()`, `encode_family()`, `encode_capacity_mode()`, `apply_block_filter()` | All transformations from §5, exclusion logic from §4, one-hot encoding from §5.3, correlation-block pre-filter (§6.2 step 1) |
| `cv.py` | `lofo_split()`, `five_fold_split()`, `stratified_bootstrap()`, `create_split_scaffold()` | LOFO by family, random 5-fold stratified by family×cap_mode, pairs bootstrap stratified by family |
| `metrics.py` | `r_squared()`, `adj_r_squared()`, `pseudo_r_squared_mcfadden()`, `rmse()`, `mae()`, `brier_score()`, `auc_roc()`, `cohens_f2()`, `backtransformed_rmse()`, `duan_smearing()` | All metrics from §9.1–9.2, including Duan's smearing (§11.4) |
| `models.py` | `fit_ols()`, `fit_fractional_logit()`, `fit_elasticnet()`, `fit_hurdle()`, `predict_ols()`, `predict_fractional_logit()`, `predict_elasticnet()` | Model fitting wrappers that handle the statsmodels/sklearn interface, extract coefficients, compute predictions |
| `importance.py` | `standardized_beta()`, `permutation_importance()`, `delta_r2_partitioning()`, `elasticnet_nonzero_coefs()` | All methods from §10 |
| `diagnostics.py` | `partial_residual_plot()`, `qq_plot()`, `vif()`, `cooks_distance()`, `link_test()`, `calibration_curve()`, `residual_vs_fitted()` | All diagnostics from §11 |
| `reporting.py` | `aggregate_results()`, `bh_adjust()`, `latex_primary_table()`, `latex_importance_table()`, `latex_family_matrix()`, `save_metrics_csv()` | Aggregation, BH adjustment (§9.3), and LaTeX output (§15) |

### 1.3 Configuration-Driven Model Specification

All 9 model definitions live in a single dict inside `config.py`:

```python
MODEL_SPECS = {
    ('Greedy', 'log_time_millis'): {
        'family': 'ols',
        'status': 'confirmatory',
        'response_transform': 'log',
        'm2_predictors': 'all_greedy',      # 6 metrics
        'exclusions': [],
    },
    ('Greedy', 'optimality_gap'): {
        'family': 'fractional_logit',
        'status': 'confirmatory',
        'response_transform': None,
        'm2_predictors': 'all_greedy',
        'exclusions': [],
    },
    ('DP', 'log_time_millis'): {
        'family': 'ols',
        'status': 'confirmatory',
        'response_transform': 'log',
        'm2_predictors': 'all_dp',           # 14 metrics
        'exclusions': [],
    },
    ('DP', 'log_memory_mb'): {
        'family': 'ols',
        'status': 'exploratory',
        'response_transform': 'log',
        'm2_predictors': 'dp_minus_memory_exclusions',  # ~11 metrics
        'exclusions': ['cells_allocated', 'nonzero_value_states', 'zero_value_states'],
    },
    ('DP', 'fill_rate'): {
        'family': 'fractional_logit',
        'status': 'supplementary',
        'response_transform': None,
        'm2_predictors': 'dp_minus_fillrate_exclusions', # ~11 metrics
        'exclusions': ['fill_rate', 'cells_allocated', 'nonzero_value_states'],
    },
    ('B&B', 'log_time_millis'): {
        'family': 'ols',
        'status': 'confirmatory',
        'response_transform': 'log',
        'm2_predictors': 'bb_minus_bound_exclusions',    # ~21 metrics
        'exclusions': ['mean_bound', 'max_bound', 'min_bound'],
    },
    ('B&B', 'optimal'): {
        'family': 'elasticnet',
        'status': 'exploratory',
        'response_transform': None,
        'm2_predictors': 'bb_minus_bound_exclusions',
        'exclusions': ['mean_bound', 'max_bound', 'min_bound'],
    },
    ('B&B', 'log_nodes_explored'): {
        'family': 'ols',
        'status': 'supplementary',
        'response_transform': 'log',
        'm2_predictors': 'bb_minus_nodes_exclusions',    # ~19 metrics
        'exclusions': ['mean_bound', 'max_bound', 'min_bound',
                       'nodes_generated', 'internal_nodes'],
    },
    ('B&B', 'solution_gap'): {
        'family': 'hurdle',
        'status': 'supplementary',
        'response_transform': None,
        'm2_predictors': 'bb_minus_nodes_exclusions',
        'exclusions': ['mean_bound', 'max_bound', 'min_bound',
                       'nodes_generated', 'internal_nodes'],
    },
}
```

### 1.4 Key Design Decisions

- **No cross-algorithm pooling.** Every model is fit per-algorithm. The `algorithm` column is excluded globally (§4.3).
- **Seed reproducibility.** `numpy.random.default_rng(42)` everywhere (CV splits, permutation shuffles, bootstrap resampling, elastic-net internal CV splits).
- **Per-algorithm subsetting.** All models operate on algorithm-specific subsets. The `algorithm` column is dropped after filtering.
- **VIF is a post-fit diagnostic, not a pre-filter.** Per design §6.2: (1) correlation-block filtering happens before fitting (retain the most interpretable variable from each block), (2) models are fit, (3) VIF is checked after fit — any predictor with VIF > 10 triggers iterative removal. No VIF-based removal occurs before model fitting.
- **Cluster-robust SEs are default** for OLS models, by `instance_id` (§11.1). `instance_id` is retained in the working DataFrame for this purpose but is excluded from all predictor matrices.
- **Two-stage hurdle** for `solution_gap`: part 1 is unregularised logistic, part 2 is fractional logit on gap>0 rows only. Both parts use the same M1/M2 predictor sets.

---

## 2. Execution Order — Milestones

### Phase 3.3.1 — Foundation and Preprocessing Pipeline

**Objective:** Build all shared infrastructure; load, clean, and preprocess data; verify
data quality; produce the prepared algorithm-specific dataframes that all model scripts consume.

**Inputs:**
- `out/results/canonical_dataset.csv` (18,000 × 110)
- Column and exclusion definitions from `PHASE_3_2_DESIGN.md` §3, §4

**Steps:**
1. Create directory structure: `Phase_3_3_Modeling/`, `utils/`, `scripts/`, `output/`
2. Write `config.py` with all constants, column lists (Group A, Group B per algorithm,
   exclusion lists per §4.1–4.5 and §4.6), transform mapping (§5.2), model specs (§7.2)
3. Write `utils/data.py`:
   - `load_canonical(path)` → DataFrame (18,000 × 110)
   - `compute_optimality_gap(df)` → joins Greedy rows to DP `solution_value` by
     `(instance_id, capacity_mode)`, computes gap = (DP_val − Greedy_val) / DP_val
   - `filter_algorithm(df, algo)` → subset to one algorithm (6,000 rows each)
4. Write `utils/preprocessing.py`:
   - `apply_global_exclusions(df)` → drops columns from §4.1, §4.2, §4.3
   - `log_transform(df, columns)` → log(y + ε) with ε=1e-9 for log transforms
   - `arctanh_transform(df, columns)` → clip to ±0.9999, then arctanh
   - `encode_family(df)` → one-hot, 5 levels → 4 dummies, reference = Uncorrelated
   - `encode_capacity_mode(df)` → binary dummy: 0=fixed, 1=scaled
    - `apply_block_filter(df)` → drops variables per §6.3: from Block 1 retain `average_fillable_items`; Block 2 retain `capacity_ratio`; Block 3 retain `dp_sum_improvement_amount`; Block 4 drop `mean_bound`, `max_bound`, `min_bound` from all B&B models
5. Write `utils/cv.py`:
   - `LofoFoldSplitter(family_col)` → yields (train_idx, test_idx) per family
   - `FiveFoldStratifiedSplitter(n_splits=5, random_state=42)` → stratified by
     family × capacity_mode
   - `stratified_bootstrap(y, family, n_resamples=1999, rng)` → pairs bootstrap
     stratified by family
6. Write `utils/metrics.py`:
   - All metric functions from §9.1 (continuous) and §9.2 (binary)
   - `duan_smearing(residuals, family_labels=None)` → pooled and family-specific φ
   - `cohens_f2(r2_1, r2_2)` → (R²₂ − R²₁) / (1 − R²₂)
7. Write script `scripts/1_prepare_data.py`:
   - Load `canonical_dataset.csv`
   - Compute `optimality_gap` for Greedy via DP join
   - Apply global exclusions (§4.1–4.5)
   - Apply transforms (§5.2)
   - Encode categoricals (§5.3)
    - Correlation-block pre-filtering (§6.2 step 1, §6.3): retain the most
      interpretable variable from each identified block. Implementation:
      Block 1 → drop `cells_allocated`, `nonzero_value_states`; Block 2 → drop
      `capacity_density`, `solution_density`; Block 3 → drop `cell_value_variance`,
      `include_count`; Block 4 → `mean_bound`, `max_bound`, `min_bound` are already
      handled as structural exclusions per §4.6 (applied per-model in
      `build_feature_matrices`)
    - Per-algorithm correlation verification (§3.3): compute correlation matrix
      within each algorithm subset; compare to pooled Phase 3.1 block structure;
      report any Δ|r| > 0.10
    - DP compositional check (§3.4): verify `include_count + exclude_count + tie_count`
      exactly equals `total_evaluations`; if exact, flag for subset-only inclusion
    - Save per-algorithm prepared dataframes:
      - `output/prepared/Greedy.pkl`
      - `output/prepared/DP.pkl`
      - `output/prepared/BandB.pkl`
    - Save per-algorithm correlation report:
     - `output/diagnostics/correlation_verification_{algorithm}.csv`

**Outputs:**
- `output/prepared/{Greedy,DP,BandB}.pkl` — cleaned, transformed, correlation-block-filtered data
- `output/diagnostics/correlation_verification_{algorithm}.csv`
- `output/diagnostics/dp_composition_check.txt`

**Dependencies:** None (first milestone).

**Estimated complexity:** ~500 lines of Python (config: 150, utils: 250, script: 100)

**Estimated runtime:** < 30 seconds (data is 18,000 × ~60 after exclusions)

**Completion criteria:**
- [ ] `config.py` defines every constant referenced by downstream scripts
- [ ] All 6 utility modules import cleanly
- [ ] `1_prepare_data.py` runs end-to-end without errors
- [ ] Output dataframes have expected columns per design §7.2 table
- [ ] Per-algorithm correlation verification report documents no surprises (Δ|r| ≤ 0.10)
- [ ] DP compositional check confirms or documents the relationship
- [ ] Correlation-block decisions (§6.3) are applied: `cells_allocated` and `nonzero_value_states` dropped; `capacity_density` and `solution_density` dropped; `cell_value_variance` and `include_count` dropped

---

### Phase 3.3.2 — OLS Models (5 Continuous Responses)

**Objective:** Fit M1 and M2 for all OLS-model responses, with LOFO CV and 5-fold CV.
Compute all continuous-response metrics.

**Models covered:**
| Algorithm | Response | Status | M2 predictors |
|-----------|----------|--------|---------------|
| Greedy | `log_time_millis` | Confirmatory | 6 Greedy metrics |
| DP | `log_time_millis` | Confirmatory | 14 DP metrics |
| DP | `log_memory_mb` | Exploratory | ~11 DP metrics (excl. circular) |
| B&B | `log_time_millis` | Confirmatory | ~21 B&B metrics |
| B&B | `log_nodes_explored` | Supplementary | ~19 B&B metrics (excl. circular+bounds) |

**Inputs:**
- `output/prepared/{Greedy,DP,BandB}.pkl`
- Model specifications from `config.py`

**Steps:**
1. Write `utils/models.py`:
   - `fit_ols(X_train, y_train)` → fits statsmodels OLS, returns fitted model
   - `ols_coefficients(model, X_scaler)` → extract β with SEs, CIs, p-values
   - `predict_ols(model, X_test)` → y_pred
2. Write script `scripts/2a_fit_ols.py`:
    - For each OLS-spec in `config.MODEL_SPECS`:
      a. Load corresponding algorithm dataframe
      b. Build **unscaled** M1 feature matrix (Group A + n + log(n) + cap_mode + family dummies)
      c. Build **unscaled** M2 feature matrix (M1 + algorithm-specific Group B after model exclusions)
      d. **LOFO CV** (§8.1) — uses unscaled predictors only:
         - For each family fold:
           - Train/test split
           - Fit M1 and M2 on **unscaled** training set
           - Predict on held-out fold
           - Compute per-fold metrics: R², R²_adj, RMSE, MAE
           - Store fold-level predictions
         - Compute mean ± SD across folds
         - Compute 95% CI using t₄
      e. **5-fold CV** (§8.2):
         - Repeat with random stratified folds on **unscaled** data
      f. **Full-sample fit** (for coefficients, diagnostics, β weights):
         - Fit M1 and M2 on all 6,000 rows (**unscaled** predictors for coefficient
           estimation; OLS is scale-invariant for predictions)
         - Compute cluster-robust SEs by `instance_id`
         - Compute incremental F-test (§7.6)
         - Compute Cohen's f²
         - **Standardised β pipeline (separate, descriptive only):**
           - Take the full-sample fitted model
           - Build a **scaled** copy of the same full-sample feature matrix
             (centre to mean=0, scale to SD=1 for all numeric predictors)
           - Refit OLS on the scaled predictors (or extract β = coef × (SD_x / SD_y))
           - This scaling step is purely for coefficient interpretation.
             It is NOT applied during CV and does not influence any predictive
             performance metric.
      g. **Back-transformed RMSE** (§9.1):
         - Compute Duan's smearing φ from log-scale residuals
         - Compute back-transformed RMSE
      h. Save per-model results:
        - `output/results/ols_metrics_{algorithm}_{response}.csv`
        - `output/cross_validation/lofo_folds_{algorithm}_{response}.csv`
        - `output/cross_validation/cv5_folds_{algorithm}_{response}.csv`
        - `output/diagnostics/full_sample_coefs_{algorithm}_{response}.csv`

**Outputs:**
- Per-model: metrics, fold-level results, full-sample coefficients
- One row per (algorithm, response, model) in aggregated metrics

**Dependencies:** Phase 3.3.1 (prepared data must exist)

**Estimated complexity:** ~400 lines (utils/models.py: 100, script: 300)

**Estimated runtime:** ~6 minutes (5 models × 2 CV schemes × 2 M1/M2 × per fold + 1999 bootstrap resamples × 2 refits × 5 models)

**Completion criteria:**
- [ ] All 5 OLS models complete without convergence errors
- [ ] LOFO and 5-fold CV metrics are available per fold
- [ ] Full-sample coefficients with cluster-robust SEs are saved
- [ ] Incremental F-test p-values are computed for each pair
- [ ] Bootstrap ΔR² CI computed: pairs bootstrap, stratified by family, 1999 resamples,
      M1 and M2 refit per resample, percentile CI reported
- [ ] Standardised β computed from a separate scaled-only pipeline (not from CV-scaled data)
- [ ] Back-transformed RMSE with Duan's smearing is reported
- [ ] Spot-check: Greedy `log_time_millis` M1 should have R² > 0.8 (instance chars
      are known to explain most runtime variance from Phase 3.1)

---

### Phase 3.3.3 — Fractional Logit Models (2 Responses)

**Objective:** Fit M1 and M2 for fractional logit responses with LOFO CV.

**Models covered:**
| Algorithm | Response | Status | M2 predictors |
|-----------|----------|--------|---------------|
| Greedy | `optimality_gap` | Confirmatory | 6 Greedy metrics |
| DP | `fill_rate` | Supplementary | ~11 DP metrics (excl. circular) |

**Inputs:**
- `output/prepared/Greedy.pkl`, `output/prepared/DP.pkl`

**Steps:**
1. Extend `utils/models.py`:
   - `fit_fractional_logit(X_train, y_train)` → statsmodels GLM with
     `family=Binomial()`, `link=Logit()`, `cov_type='HC3'`
   - `predict_fractional_logit(model, X_test)` → predicted probabilities
2. Write `utils/preprocessing.py` additions:
   - `verify_fractional_logit_response(y)` → ensure y ∈ [0, 1]; warn if any y
     outside (0,1) without boundary
3. Write script `scripts/2b_fit_fractional_logit.py`:
   - For each fractional-logit spec:
     a. Build M1 and M2 feature matrices (same structure as OLS)
     b. Do NOT scale response — fractional logit handles bounded scale natively
     c. Do NOT centre/scale predictors for fit (statsmodels GLM does not require it)
        but scale a copy for standardised β later
     d. **LOFO CV** (§8.1):
        - Per fold: fit M1 and M2, predict held-out fold
        - Compute McFadden pseudo-R² (§9.1)
        - Compute RMSE, MAE on probability scale
     e. **Full-sample fit:**
        - Fit M1 and M2 on all rows
        - Compare standard and sandwich SEs (§11.2)
        - If ratio > 2 for any coefficient, flag for bootstrap SEs
     f. Save per-model results (same structure as OLS)

**Outputs:**
- `output/results/flogit_metrics_{algorithm}_{response}.csv`
- `output/cross_validation/lofo_folds_flogit_{algorithm}_{response}.csv`
- `output/diagnostics/full_sample_coefs_flogit_{algorithm}_{response}.csv`
- `output/diagnostics/se_comparison_{algorithm}_{response}.csv`

**Dependencies:** Phase 3.3.1

**Estimated complexity:** ~250 lines (extend models.py: 50, script: 200)

**Estimated runtime:** ~2 minutes (2 models × 5 LOFO folds = 10 fits per model,
GLM fit is slower than OLS)

**Completion criteria:**
- [ ] Both fractional logit models converge (check GLM convergence flag)
- [ ] Pseudo-R² and RMSE are reported per fold and overall
- [ ] Sandwich vs. standard SE comparison is saved
- [ ] All predictions are in [0, 1]
- [ ] Spot-check: `optimality_gap` M1 pseudo-R² should be lower than OLS R²,
      consistent with fractional logit scaling (§9.1)

---

### Phase 3.3.4 — Elastic-Net and Hurdle Models (B&B)

**Objective:** Fit the B&B-specific models: elastic-net logistic for `optimal` and
two-part hurdle for `solution_gap`.

**Models covered:**
| Algorithm | Response | Status | Notes |
|-----------|----------|--------|-------|
| B&B | `optimal` | Exploratory | Elastic-net logistic, nested CV λ, zero-event handling |
| B&B | `solution_gap` | Supplementary | Two-part hurdle (logistic + fractional logit) |

**Inputs:**
- `output/prepared/BandB.pkl`

**Steps:**

#### Part A: Elastic-Net (B&B `optimal`)

1. Extend `utils/models.py`:
   - `fit_elasticnet(X_train, y_train, alpha=0.5, cv_folds=5)` → sklearn
     `LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5)`
     with `C` selected via `GridSearchCV` (note: sklearn uses C = 1/λ)
   - `predict_elasticnet(model, X_test)` → predicted probabilities
   - `elasticnet_lambda_path(model, X_train, y_train)` → CV deviance vs log(λ)
2. Write script `scripts/2c_fit_elasticnet.py`:
   - For each LOFO fold:
     a. Determine if held-out family has any `optimal=False` events
     b. Training set: perform internal 5-fold CV for λ selection (§8.4)
        - Use 1-SE rule (simplest model within 1 SE of min deviance)
     c. Refit on full training set at selected λ
     d. Predict on held-out fold
     e. Compute metrics:
        - AUC-ROC (if held-out fold has ≥ 1 event)
        - Brier score (always computable)
        - Accuracy, precision, recall, F1 for minority class
     f. Store λ path data and selected λ
   - Full-sample fit (with internal CV λ selection):
     - Fit elastic-net on all B&B rows
     - Report nonzero coefficients at optimal λ (§9.4)
     - Generate λ path plot and coefficient trace plot (§15.4)
   - Handle zero-event families (§8.3):
     - Record which families have zero events
     - Note effective fold count for AUC

#### Part B: Two-Part Hurdle (B&B `solution_gap`)

1. Extend `utils/models.py`:
   - `fit_hurdle(X, y)` → returns dict with `part1` (LogisticRegression, unregularised)
     and `part2` (fractional logit on y > 0 subset)
   - `predict_hurdle(model, X)` → combined prediction: P(y>0) × E(y|y>0)
2. Write script `scripts/2d_fit_hurdle.py`:
   - Part 1 (zero vs. positive):
     - Response: binary `solution_gap > 0`
     - M1 and M2: unregularised logistic
     - LOFO CV
     - Metrics: AUC, Brier, accuracy
   - Part 2 (positive gap values):
     - Subset to 197 rows where `solution_gap > 0`
     - Response: `solution_gap` in (0, 1)
     - M1 and M2: fractional logit
     - LOFO CV (note: some families may have zero or one positive-gap rows)
     - Metrics: pseudo-R², RMSE on gap>0 subset
   - Combined hurdle prediction:
     - E[gap] = P(gap>0) × E[gap | gap>0]
     - Overall RMSE, MAE across all 6,000 rows
   - Explicitly note: second-stage EPV ≈ 197 / 19 ≈ 10.4; caveat:
     this is a descriptive supplement, not formal inference

**Outputs:**
- `output/results/elasticnet_metrics.csv`
- `output/cross_validation/lofo_folds_elasticnet.csv`
- `output/figures/lambda_path_fold_{f}.png` (5 plots, one per LOFO fold)
- `output/figures/coefficient_trace.png`
- `output/cross_validation/lofo_folds_hurdle.csv`
- `output/results/hurdle_metrics.csv`
- `output/diagnostics/zero_event_families.txt`

**Dependencies:** Phase 3.3.1

**Estimated complexity:** ~500 lines (extend models.py: 150, elastic-net script: 200,
hurdle script: 150)

**Estimated runtime:** ~10 minutes (elastic-net nested CV is expensive: 5 LOFO ×
5 internal CV × ~10 λ × 2 models = ~500 fits)

**Completion criteria:**
- [ ] Elastic-net converges for all LOFO folds (saga solver should handle this)
- [ ] λ path plots show sensible U-shaped deviance curves
- [ ] Zero-event families are correctly identified and handled
- [ ] Hurdle model part 1 (logistic) and part 2 (fractional logit) both complete
- [ ] Combined hurdle predictions are in [0, 1]
- [ ] Spot-check: elastic-net nonzero coefficient count should be well below 67
      (expect 10–20 nonzero with α=0.5, given EPV ≈ 3)

---

### Phase 3.3.5 — Feature Importance

**Objective:** Compute all feature importance measures for every model.

**Inputs:**
- All fitted models from Phase 3.3.2–3.3.4
- Full-sample fits saved in `output/results/` and `output/diagnostics/`

**Steps:**
1. Write `utils/importance.py`:
   - `standardized_beta(model, X_scaled, y)` → β with 95% CI
   - `permutation_importance(model, X, y, n_repeats=20, rng, metric)` → importance
     mean ± SD per predictor
   - `delta_r2_partitioning(X, y, top_k_predictors, base_model)` → ΔR² from
     removing each predictor individually
   - `elasticnet_nonzero_coefs(model, feature_names)` → nonzero coefficients at
     optimal λ with magnitudes
2. Write script `scripts/3_compute_importance.py`:
   - For each (algorithm, response) pair:
     a. **Standardised β** (§10.1):
        - Load full-sample fitted model
        - Compute β with CIs for all M2 predictors
        - Applicable: OLS and fractional logit only
        - Save top-20 ranked by |β|
     b. **Permutation importance** (§10.2):
        - 20 repeats per predictor
        - Using LOFO test-set R²/AUC/Brier as metric
        - Report mean ± SD
        - Separate rankings for instance characteristics vs execution metrics
     c. **Elastic-net nonzero coefficients** (§10.3):
        - For B&B `optimal` only
        - Report coefficients at optimal λ
     d. **Δ-R² partitioning** (§10.4):
        - For top-10 metrics by permutation importance
        - Fit M2 without each metric, record ΔR²
     e. Save all results

**Outputs:**
- `output/feature_importance/standardized_beta_{algorithm}_{response}.csv`
- `output/feature_importance/permutation_importance_{algorithm}_{response}.csv`
- `output/feature_importance/delta_r2_partitioning_{algorithm}_{response}.csv`
- `output/figures/importance_{algorithm}_{response}.png` (horizontal bar chart,
  top-10 metrics)

**Dependencies:** Phase 3.3.2, 3.3.3, 3.3.4 (needs fitted models)

**Estimated complexity:** ~350 lines (utils/importance.py: 200, script: 150)

**Estimated runtime:** ~20 minutes (permutation importance: 20 repeats × 18 models
× ~30–60 predictors = 10,800–21,600 refit+score operations; each is cheap but
the total adds up)

**Completion criteria:**
- [ ] Standardised β with CIs computed for all OLS and fractional logit models
- [ ] Permutation importance completes for all models
- [ ] Elastic-net nonzero coefficients reported for B&B `optimal`
- [ ] Δ-R² partitioning completed for top-10 metrics
- [ ] Importance figures generated
- [ ] Spot-check: top execution metrics by importance should differ meaningfully
      between algorithms (e.g., Greedy should show selection-position metrics as
      important; DP should show evaluation metrics; B&B should show pruning metrics)

---

### Phase 3.3.6 — Diagnostic Checks

**Objective:** Run all diagnostic checks from §11, produce diagnostic plots and tables.

**Inputs:** Full-sample fitted models from Phase 3.3.2–3.3.4

**Steps:**
1. Write `utils/diagnostics.py`:
   - All diagnostic functions from §11
2. Write script `scripts/4_diagnostics.py`:
   - For each (algorithm, response) pair:
     a. **OLS diagnostics** (§11.1):
        - Partial residual plots for top-5 predictors
        - Q-Q plot with confidence envelope
        - Residual histogram
        - Residual-vs-fitted plot
        - Breusch-Pagan test for heteroscedasticity
        - Cook's distance plot (identify any > 1)
        - VIF table for all predictors
        - Residual autocorrelation plot by n and by instance_id
     b. **Fractional logit diagnostics** (§11.2):
        - Link test (ŷ² significance)
        - Boundary sensitivity (fit with/without Smithson-Verkuilen transform)
        - Sandwich vs. standard SE comparison table
     c. **Elastic-net diagnostics** (§11.3):
        - λ stability across LOFO folds (report λ range)
        - Calibration curve (observed vs. predicted probability)
        - Component + residual plots for top-3 predictors
     d. **Smearing factor** (§11.4):
        - Pooled Duan's φ for each log-transformed model
        - Family-specific φ
        - Compare pooled vs. family-specific back-transformed RMSE
      e. **VIF-thinned vs raw ΔR² comparison** (§6.2 step 3):
         - If any predictor in any OLS model has VIF > 10:
           - Record which predictors exceed VIF > 10
           - For each affected model, refit on the VIF-thinned set
             (iteratively remove highest-VIF predictors until all ≤ 10;
              removal is per-model, per-fit, not global)
           - Compute ΔR² (M2 − M1) on the VIF-thinned re-fit
           - Compare to the primary (raw) ΔR²
           - If ΔR² differs by > 0.02, flag for discussion in §16
         - If no predictor exceeds VIF > 10, note "No VIF thinning needed"
    - Generate per-model diagnostic figure pages

**Outputs:**
- `output/diagnostics/assumption_summary_{algorithm}_{response}.txt`
- `output/diagnostics/vif_{algorithm}_{model}.csv` — post-fit VIF for all predictors
- `output/diagnostics/vif_removed_predictors_{algorithm}_{model}.csv` — list of predictors removed if any VIF > 10 found
- `output/diagnostics/vif_thinned_delta_r2_comparison.csv` — raw vs thinned ΔR²
- `output/diagnostics/residual_tests_{algorithm}.csv`
- `output/diagnostics/smearing_factors.csv`
- `output/figures/diagnostic_{algorithm}_{response}.png` (multi-panel diagnostic
  figure per model)
- `output/figures/qq_{algorithm}_{response}.png`
- `output/figures/residual_vs_fitted_{algorithm}_{response}.png`
- `output/figures/calibration_curve_{algorithm}_{response}.png`

**Dependencies:** Phase 3.3.2, 3.3.3, 3.3.4 (needs fitted models)

**Estimated complexity:** ~500 lines (utils/diagnostics.py: 350, script: 150)

**Estimated runtime:** ~2 minutes (mostly plotting)

**Completion criteria:**
- [ ] All diagnostic plots generated without errors
- [ ] VIF tables show all predictors with VIF < 10 — or document which predictors exceed threshold
- [ ] VIF-thinned vs raw ΔR² comparison computed: if any VIF > 10, the comparison table exists; if none, a note confirms "No VIF thinning needed"
- [ ] Link test for both fractional logit models is not significant (ŷ² p > 0.05)
      — or flag if significant
- [ ] Breusch-Pagan results saved for each OLS model
- [ ] Cook's distance identifies any influential points
- [ ] Smearing factors computed and compared
- [ ] No diagnostic reveals a violation that invalidates the model family choice
      (if any does, document and flag — do not change methodology without approval)

---

### Phase 3.3.7 — Sensitivity and Subgroup Analyses

**Objective:** Run the stratification and sensitivity analyses from §12.

**Inputs:**
- `output/prepared/{Greedy,DP,BandB}.pkl`
- Model scripts from Phase 3.3.2–3.3.4 (reuse fitting functions)

**Steps:**
1. Write script `scripts/5_sensitivity.py`:

   a. **Capacity-mode stratification** (§12.1):
      - For each (algorithm, response) pair:
        - Split data into `capacity_mode=0` (fixed) and `capacity_mode=1` (scaled)
        - Fit M1 and M2 separately per mode (reuse same fitting functions from
          Phase 3.3.2–3.3.4)
        - Report ΔR² per mode
        - Compare: does ΔR² differ substantially (>0.05) between modes?
      - Output: `output/results/capacity_mode_sensitivity.csv`

   b. **B&B complete-only sensitivity** (§12.3):
      - For B&B `log_time_millis` and `log_nodes_explored`:
        - Filter to `optimal=True` (5,803 rows)
        - Fit M1 and M2 on complete-only subset
        - Compare ΔR² to full-sample (6,000 rows) results
        - If ΔR² changes by > 0.05, flag and discuss censoring bias
      - Output: `output/results/bb_complete_only_sensitivity.csv`

   c. **Family-level models** (§12.2):
      - If LOFO performance heterogeneity is large (SD across folds > 0.15 in R²):
        - Fit separate M1/M2 per family (5 families × (algorithm, response) pairs)
        - Report family-level ΔR²
        - Output: `output/results/family_level_delta_r2.csv`

   d. **DP compositional sensitivity** (§3.4):
      - If `include_count + exclude_count + tie_count = total_evaluations` exactly:
        - Run DP models with subset-only DP evaluation predictors (e.g.,
          `total_evaluations` + `include_ratio` only)
        - Compare to primary results — if different, document

**Outputs:**
- `output/results/capacity_mode_sensitivity.csv`
- `output/results/bb_complete_only_sensitivity.csv`
- `output/results/family_level_delta_r2.csv`
- `output/figures/capacity_mode_comparison.png`

**Dependencies:** Phase 3.3.1–3.3.4

**Estimated complexity:** ~300 lines (script only, reuses utils)

**Estimated runtime:** ~5 minutes (refitting models per subgroup)

**Completion criteria:**
- [ ] Capacity-mode stratified results are consistent with pooled results
- [ ] B&B complete-only sensitivity shows ΔR² change ≤ 0.05 (or documented if larger)
- [ ] Family-level models produce interpretable results
- [ ] DP compositional handling is documented

---

### Phase 3.3.8 — Summarise and Report

**Objective:** Aggregate all results, apply BH multiplicity correction, produce
LaTeX tables and summary.

**Inputs:** All output CSV files from Phase 3.3.2–3.3.7

**Steps:**
1. Write `utils/reporting.py`:
   - `aggregate_results(output_dir)` → master DataFrame with one row per
     (algorithm, response, model) containing all metrics
   - `bh_adjust(p_values, alpha=0.05)` → BH-corrected q-values (§9.3)
   - `latex_primary_table(agg_df, algo)` → LaTeX table per §15.1
   - `latex_importance_table(imp_df, algo)` → LaTeX table per §15.2
   - `latex_family_matrix(fold_metrics)` → LaTeX table per §15.3
   - `save_metrics_csv(agg_df, path)`
2. Write script `scripts/6_summarize.py`:
   a. Load all metrics CSVs from `output/results/`
   b. Merge into single aggregated DataFrame
   c. Apply BH adjustment to the 4 confirmatory model p-values
   d. Generate per-algorithm primary result tables (LaTeX)
   e. Generate feature importance tables (LaTeX)
   f. Generate family-level heterogeneity matrix (LaTeX)
   g. Generate elastic-net summary (§15.4):
      - λ path plots copied to output/figures/
      - Nonzero coefficient table
      - Per-family Brier and AUC
   h. Write summary CSV:
      - `output/results/master_results.csv` — all metrics, all models
   i. Write diagnostics appendix reference:
      - `output/diagnostics/README.md` — lists all generated diagnostics
        with interpretation guidance

**Outputs:**
- `output/tables/primary_results_greedy.tex`
- `output/tables/primary_results_dp.tex`
- `output/tables/primary_results_bb.tex`
- `output/tables/feature_importance_greedy.tex`
- `output/tables/feature_importance_dp.tex`
- `output/tables/feature_importance_bb.tex`
- `output/tables/family_heterogeneity_matrix.tex`
- `output/tables/elasticnet_summary.tex`
- `output/results/master_results.csv`
- `output/diagnostics/README.md`

**Dependencies:** Phase 3.3.2–3.3.7 (all results must exist)

**Estimated complexity:** ~300 lines (utils/reporting.py: 200, script: 100)

**Estimated runtime:** < 10 seconds

**Completion criteria:**
- [ ] Master results CSV contains 18 rows (9 responses × M1/M2 combined-hurdle);
      sub-model parts (hurdle logistic + fractional logit) are in supplementary outputs only
- [ ] BH-adjusted q-values reported for 4 confirmatory models
- [ ] All LaTeX tables compile without errors (check with a LaTeX linter)
- [ ] Primary results table distinguishes C, E, S designations
- [ ] Family heterogeneity matrix shows fold-level R² per held-out family

---

## 3. Model Implementation Roadmap

### 3.1 Greedy `log_time_millis` (OLS, Confirmatory)

| Property | Specification |
|----------|--------------|
| Response | `log(time_millis + 1e-9)` |
| M1 predictors | 35 Group A + n + log(n) + cap_mode + 4 family dummies (42 params) |
| M2 additional | 6 Greedy metrics: `selected_count`, `last_selected_position`, `first_skipped_position`, `solution_density`, `residual_capacity`, `capacity_utilization` |
| Model-specific exclusions | None |
| Preprocessing | Log-transform response. Log/sqrt transforms on skewed Group A predictors (§5.2). Arctanh on correlation predictors. One-hot family encoding. Correlation-block filter (§6.2 step 1, §6.3) |
| Model family | OLS (Gaussian, identity) via `statsmodels.OLS` |
| Diagnostics | §11.1: linearity (partial residuals), normality (Q-Q), homoscedasticity (BP test), independence (cluster-robust SEs by instance_id), VIF, Cook's distance |
| Validation | LOFO CV (5 folds × family), secondary 5-fold CV. Report fold-level R², RMSE, MAE, back-transformed RMSE |
| Key outputs | LOFO R² (mean ± SD, fold-level), ΔR²_adj, F-test p-value, Cohen's f², standardised β, permutation importance, Δ-R² partitioning |
| Special notes | Confirmatory — BH-adjusted p-value across 4 confirmatory models |

### 3.2 Greedy `optimality_gap` (Fractional Logit, Confirmatory)

| Property | Specification |
|----------|--------------|
| Response | `optimality_gap` = (DP_val − Greedy_val) / DP_val, bounded [0, 1]. Raw, no transform |
| M1 predictors | Same as §3.1 (42 params) |
| M2 additional | Same 6 Greedy metrics |
| Model-specific exclusions | None |
| Preprocessing | Response computed via DP join before any filtering. Bounded [0, 1] — verify no values outside this range. No log/square-root transform of response (§2.2). Standardise numeric predictors for β only (descriptive, separate scaled pipeline) |
| Model family | Fractional logit: statsmodels GLM with `family=Binomial()`, `link=Logit()`, `cov_type='HC3'` |
| Diagnostics | §11.2: link test (ŷ²), boundary sensitivity (gap=0 rows), sandwich vs. standard SE comparison |
| Validation | LOFO CV. Report pseudo-R² (McFadden), probability-scale RMSE/MAE |
| Key outputs | LOFO pseudo-R², Δ pseudo-R², QLR p-value, Cohen's f² (using pseudo-R²), standardised β, permutation importance |
| Special notes | 1,200 rows with gap=0 (Inverse Correlated) — this is expected, fractional logit handles it naturally. Confirmatory — BH adjusted |

### 3.3 DP `log_time_millis` (OLS, Confirmatory)

| Property | Specification |
|----------|--------------|
| Response | `log(time_millis + 1e-9)` |
| M1 predictors | Same 42 params |
| M2 additional | 14 DP metrics: `total_evaluations`, `include_count`, `exclude_count`, `tie_count`, `include_ratio`, `zero_value_states`, `mean_cell_value`, `updates_per_cell`, `cells_allocated`, `nonzero_value_states`, `fill_rate`, `dp_sum_improvement_amount`, `dp_mean_improvement_amount` |
| Model-specific exclusions | None for this response |
| Preprocessing | Same as §3.1 (correlation-block filter). Log-transform skewed DP metrics (§5.2). DP compositional check (§3.4) |
| Model family | OLS |
| Diagnostics | Same as §11.1 |
| Validation | LOFO + 5-fold CV |
| Key outputs | Same as §3.1. Note: `total_evaluations` is causal but not definitional — it is intentionally retained (§3.2 audit cross-check) |
| Special notes | Confirmatory — BH adjusted |

### 3.4 DP `log_memory_mb` (OLS, Exploratory)

| Property | Specification |
|----------|--------------|
| Response | `log(memory_mb + 1e-9)` |
| M1 predictors | Same 42 params |
| M2 additional | DP metrics minus `cells_allocated`, `nonzero_value_states`, `zero_value_states` (~11 metrics) |
| Model-specific exclusions | `cells_allocated`, `nonzero_value_states`, `zero_value_states` excluded (§4.6) |
| Preprocessing | Same as §3.3 (correlation-block filter), but apply model-specific exclusions before fitting M2 |
| Model family | OLS |
| Diagnostics | Same as §11.1 |
| Validation | LOFO + 5-fold CV |
| Key outputs | Same as §3.1. Explicit note: model is conservative — most powerful predictors removed |
| Special notes | Exploratory — unadjusted p-values, explicit caveats |

### 3.5 DP `fill_rate` (Fractional Logit, Supplementary)

| Property | Specification |
|----------|--------------|
| Response | `fill_rate = nonzero_value_states / cells_allocated`, bounded [0, 1]. Raw, no transform |
| M1 predictors | Same 42 params |
| M2 additional | DP metrics minus `fill_rate`, `cells_allocated`, `nonzero_value_states` (~11 metrics) |
| Model-specific exclusions | `fill_rate`, `cells_allocated`, `nonzero_value_states` excluded (§4.6) |
| Preprocessing | Response is computed from columns that are excluded from M2 predictors. Verify fill_rate ∈ [0, 1]. Correlation-block filter (shared) |
| Model family | Fractional logit |
| Diagnostics | §11.2: same as §3.2 |
| Validation | LOFO CV |
| Key outputs | LOFO pseudo-R², Δ pseudo-R², Cohen's f², standardised β, permutation importance |
| Special notes | Supplementary — effect sizes only, no formal inference |

### 3.6 B&B `log_time_millis` (OLS, Confirmatory)

| Property | Specification |
|----------|--------------|
| Response | `log(time_millis + 1e-9)` |
| M1 predictors | Same 42 params |
| M2 additional | B&B metrics minus `mean_bound`, `max_bound`, `min_bound` (~21 metrics) |
| Model-specific exclusions | `mean_bound`, `max_bound`, `min_bound` excluded (§4.6, §6.3) |
| Preprocessing | Log-transform skewed B&B metrics (§5.2). Apply bound exclusions. Correlation-block filter (shared) |
| Model family | OLS |
| Diagnostics | Same as §11.1 |
| Validation | LOFO + 5-fold CV. B&B complete-only sensitivity (§12.3) |
| Key outputs | Same as §3.1 |
| Special notes | Confirmatory — BH adjusted. 197 incomplete runs may bias runtime models (§12.3, §16.1) |

### 3.7 B&B `optimal` (Elastic-Net Logistic, Exploratory)

| Property | Specification |
|----------|--------------|
| Response | `optimal` (binary: True/False). 197 False (3.28%) |
| M1 predictors | Same 42 params. No regularisation for M1 (§7.2) |
| M2 additional | B&B metrics minus bound exclusions (~21 metrics) |
| Model-specific exclusions | `mean_bound`, `max_bound`, `min_bound` excluded. Regularisation applied to M2 |
| Preprocessing | Standardise all numeric predictors (elastic-net requires scaled data). No transform on binary response. Correlation-block filter (shared) |
| Model family | Elastic-net logistic: sklearn `LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5)`. λ (C = 1/λ) via GridSearchCV |
| Diagnostics | §11.3: calibration curve, λ stability, component+residual plots, separation check |
| Validation | Nested LOFO CV: internal 5-fold CV for λ selection (1-SE rule). Zero-event handling: Brier for families with 0 events, AUC + Brier for families with ≥ 1 |
| Key outputs | LOFO AUC (per family, where computable), Brier score (all folds), accuracy, precision/recall/F1, λ path plots, coefficient trace, nonzero coefficient count |
| Special notes | Exploratory — unadjusted p-values. EPV ≈ 3 for full specification, elastic-net mitigates this. α = 0.5 fixed (equal L1/L2) |

### 3.8 B&B `log_nodes_explored` (OLS, Supplementary)

| Property | Specification |
|----------|--------------|
| Response | `log(nodes_explored + 1)` |
| M1 predictors | Same 42 params |
| M2 additional | B&B metrics minus bound exclusions, minus `nodes_generated`, minus `internal_nodes` (~19 metrics) |
| Model-specific exclusions | `mean_bound`, `max_bound`, `min_bound`, `nodes_generated`, `internal_nodes` (§4.6) |
| Preprocessing | Same as §3.6 (correlation-block filter), plus apply node-exclusion |
| Model family | OLS |
| Diagnostics | Same as §11.1 |
| Validation | LOFO + 5-fold CV. Complete-only sensitivity |
| Key outputs | Same as §3.1 |
| Special notes | Supplementary — effect sizes only. Most powerful predictors excluded; conservative test |

### 3.9 B&B `solution_gap` (Two-Part Hurdle, Supplementary)

| Property | Specification |
|----------|--------------|
| Response | `solution_gap = (optimal_val − solution_val) / optimal_val`. 0 for 5,803 complete runs, >0 for 197 incomplete runs |
| M1 predictors | Same 42 params (part 1: logistic for 0 vs >0; part 2: fractional logit on gap>0) |
| M2 additional | Same as §3.8 (~19 metrics), same exclusions |
| Model-specific exclusions | Same as §3.8 |
| Preprocessing | Compute `solution_gap` for B&B rows. Split into binary (gap=0 vs gap>0) and continuous (gap>0). Correlation-block filter (shared) |
| Model family | Part 1: sklearn `LogisticRegression` (unregularised). Part 2: fractional logit (statsmodels GLM) |
| Diagnostics | No dedicated §11 subsection; use logistic diagnostics (calibration) for part 1 and fractional logit diagnostics (§11.2) for part 2 |
| Validation | LOFO CV for each part separately. Combined prediction evaluated on all 6,000 rows |
| Key outputs | Part 1: AUC, Brier. Part 2: pseudo-R² on gap>0 subset. Combined: RMSE, MAE across all rows |
| Special notes | Supplementary — descriptive only. Second-stage sample: n=197, EPV ≈ 10.4. Explicitly caveat limited power |

---

## 4. Common Preprocessing Pipeline

Every model shares the following preprocessing, implemented in `utils/preprocessing.py`
and orchestrated by `1_prepare_data.py`.

### 4.1 Pipeline Steps (in order)

```
raw DataFrame (18,000 × 110)
│
├─ 1. LOAD ───────────────────────────────────── utils/data.py
│   load_canonical() → df
│
├─ 2. COMPUTE GREEDY OPTIMALITY GAP ──────────── utils/data.py
│   compute_optimality_gap(df):
│     - Join Greedy rows to DP rows on (instance_id, capacity_mode)
│     - gap = (DP.solution_value − Greedy.solution_value) / DP.solution_value
│     - Write result to df.loc[greedy_mask, 'optimality_gap']
│
├─ 3. COMPUTE B&B SOLUTION GAP ───────────────── utils/data.py
│   For B&B rows: (optimal_value − solution_value) / optimal_value
│   Write to df.loc[bb_mask, 'solution_gap']
│
├─ 4. GLOBAL EXCLUSIONS (§4.1–4.5) ──────────── utils/preprocessing.py
│   apply_global_exclusions(df):
│     - Constants (§4.1): first_improvement_node, leaf_nodes, min_depth,
│       seed, skipped_by_cap
│     - Near-constants (§4.2): explored_generated_ratio
│     - Redundant (§4.3): time_nanos, capacity, algorithm, instance_id
│     - Structurally missing (§4.4): optimal_value (Greedy rows only,
│       already handled via DP join)
│   Note: algorithm is excluded. instance_id is retained for cluster-robust
│       SE grouping (§11.1) but never enters any predictor matrix
│
├─ 5. PER-ALGORITHM FILTERING ────────────────── utils/data.py
│   filter_algorithm(df, algo) → 6,000 rows
│
├─ 6. RESPONSE TRANSFORMS (§2.3) ─────────────── utils/preprocessing.py
│   For each response:
│     - log_time_millis: y' = ln(y + 1e-9)
│     - log_memory_mb: y' = ln(y + 1e-9)
│     - optimality_gap: raw (fractional logit)
│     - fill_rate: raw (fractional logit)
│     - log_nodes_explored: y' = ln(y + 1)
│     - optimal: raw (binary, elastic-net)
│     - solution_gap: raw (hurdle)
│   (Applied per-model at fit time; prepare_data creates both raw and
│    log-transformed response columns)
│
├─ 7. PREDICTOR TRANSFORMS (§5.2) ────────────── utils/preprocessing.py
│   log_transform/arctanh_transform on specified columns:
│     - Log: total_weight, total_value, total_evaluations, average_fillable_items,
│       slack, unique_ratio_count, unique_weights, unique_values, unique_pairs,
│       duplicate_items, duplicate_pairs, bound_variance, sum_improvement_amount,
│       pruned_by_bound, mean_bound_gap, bound_gap_variance, mean_queue_size,
│       final_queue_size, left_branches, right_branches, explored_children,
│       skipped_children, skipped_infeasible, skipped_by_bound, include_count,
│       exclude_count, tie_count, updates_per_cell, dp_sum_improvement_amount,
│       dp_mean_improvement_amount, cells_allocated, nonzero_value_states,
│       zero_value_states, nodes_generated, internal_nodes
│     - Arctanh (clip ±0.9999): pearson_corr, spearman_corr, kendall_corr
│     - Raw (no transform): all ratio variables, fill_rate, solution_density,
│       capacity_utilization, avg_branching_factor, mean_ratio, median_ratio,
│       std_ratio, ratio_entropy, include_ratio, selected_count (or sqrt),
│       capacity_ratio
│
├─ 8. CATEGORICAL ENCODING (§5.3) ────────────── utils/preprocessing.py
│   encode_family(df): 5 levels → 4 dummies, reference = Uncorrelated
│   encode_capacity_mode(df): 0 = fixed, 1 = scaled
│   Include raw n and log(n) as default predictors (§5.3)
│
├─ 9. PER-ALGORITHM CORRELATION VERIFICATION (§3.3)
│   For each algorithm subset:
│     - Compute correlation matrix of all predictors
│     - Compare to Phase 3.1 block structure (Block 1–4)
│     - Report any Δ|r| > 0.10
│     - Special note: Block 2 (capacity_density, solution_density) spans
│       algorithms; per-algorithm verification is essential
│
├─ 10. DP COMPOSITIONAL CHECK (§3.4)
│    Only for DP subset:
│      - Check include_count + exclude_count + tie_count vs total_evaluations
│      - If exact equality, flag for subset-only inclusion
│
├─ 11. CORRELATION-BLOCK PRE-FILTER (§6.2 step 1, §6.3)
│    For each algorithm subset:
│      - Block 1: drop cells_allocated, nonzero_value_states
│      - Block 2: drop capacity_density, solution_density
│      - Block 3: drop cell_value_variance, include_count
│      - Block 4: mean_bound/max_bound/min_bound are structural exclusions
│        (§4.6), applied per-model in build_feature_matrices
│    (No VIF removal here — VIF is a post-fit diagnostic only, §6.2 step 3)
│
└─ 12. SAVE PREPARED DATAFRAMES
     - output/prepared/Greedy.pkl
     - output/prepared/DP.pkl
     - output/prepared/BandB.pkl
```

### 4.2 What Should Be Reusable Utilities

| Component | Module | Reused By |
|-----------|--------|-----------|
| `apply_global_exclusions()` | `utils/preprocessing.py` | All scripts (1. prepare_data, 2a–2d, 5_sensitivity) |
| `log_transform()`, `arctanh_transform()` | `utils/preprocessing.py` | 1_prepare_data only (applied once) |
| `encode_family()`, `encode_capacity_mode()` | `utils/preprocessing.py` | 1_prepare_data only |
| `apply_block_filter()` | `utils/preprocessing.py` | 1_prepare_data only |
| `build_m1_matrix()`, `build_m2_matrix()` | `utils/preprocessing.py` | All model scripts (2a–2d, 5) — builds feature matrix from prepared df, applying model-specific exclusions |
| `lofo_split()`, `five_fold_split()` | `utils/cv.py` | All model scripts |
| `stratified_bootstrap()` | `utils/cv.py` | 3_importance (for β CIs) + 2a (for ΔR² CI) |
| All metric functions | `utils/metrics.py` | 2a–2d, 3, 6 |
| All model fit/predict functions | `utils/models.py` | 2a–2d, 5 |
| All importance functions | `utils/importance.py` | 3_importance |
| All diagnostic functions | `utils/diagnostics.py` | 4_diagnostics |
| All reporting functions | `utils/reporting.py` | 6_summarize |

### 4.3 Per-Algorithm Feature Matrix Construction (Reusable)

A key reusable function:

```python
def build_feature_matrices(df, algo, response, model_specs, config):
    """
    Returns (X_m1, X_m2, y, predictor_names_m1, predictor_names_m2).

    - Extracts Group A predictors from prepared df (already transformed)
    - Adds n, log(n), cap_mode, family dummies
    - For M2: adds Group B predictors minus model-specific exclusions
    - Returns unscaled matrices for OLS (no scaling before CV per C1).
      Scaling for standardised β is handled in a separate pipeline
      (full-sample only, after all CV is complete).
    - Does NOT scale binary/dummy predictors
    - Applies response transform per config
    """
```

---

## 5. Output Organisation

### 5.1 Directory Tree

```
output/
├── prepared/
│   ├── Greedy.pkl               # Prepared DataFrame (after exclusions, transforms,
│   │                           #   correlation-block filter)
│   ├── DP.pkl
│   └── BandB.pkl
│
├── results/
│   ├── master_results.csv        # All metrics, all models (primary aggregation;
│   │                           #   18 rows: 9 responses × M1/M2 combined-hurdle)
│   ├── ols_metrics_{algo}_{resp}.csv
│   ├── flogit_metrics_{algo}_{resp}.csv
│   ├── elasticnet_metrics.csv
│   ├── hurdle_metrics.csv
│   ├── delta_r2.csv              # ΔR² per (algo, response, model) with CIs
│   ├── vif_thinned_delta_r2_comparison.csv  # Raw vs VIF-thinned ΔR² (§6.2 step 3)
│   ├── capacity_mode_sensitivity.csv
│   ├── bb_complete_only_sensitivity.csv
│   └── family_level_delta_r2.csv
│
├── cross_validation/
│   ├── lofo_folds_{algo}_{resp}.csv    # Fold-level metrics
│   ├── cv5_folds_{algo}_{resp}.csv     # 5-fold random metrics
│   ├── lofo_folds_flogit_{algo}_{resp}.csv
│   ├── lofo_folds_elasticnet.csv
│   ├── lofo_folds_hurdle.csv
│   ├── per_family_r2.csv               # R² matrix: family × model
│   └── lofo_summary.csv                # Mean ± SD across folds per model
│
├── figures/
│   ├── diagnostic_{algo}_{resp}.png    # Multi-panel: Q-Q, resid-v-fitted, Cook's
│   ├── qq_{algo}_{resp}.png
│   ├── residual_vs_fitted_{algo}_{resp}.png
│   ├── importance_{algo}_{resp}.png    # Top-10 horizontal bar
│   ├── lambda_path_fold_{f}.png        # Elastic-net λ path per LOFO fold
│   ├── coefficient_trace.png           # Elastic-net coefficient magnitude vs λ
│   ├── calibration_curve_{algo}_{resp}.png
│   └── capacity_mode_comparison.png
│
├── tables/
│   ├── primary_results_greedy.tex
│   ├── primary_results_dp.tex
│   ├── primary_results_bb.tex
│   ├── feature_importance_greedy.tex
│   ├── feature_importance_dp.tex
│   ├── feature_importance_bb.tex
│   ├── family_heterogeneity_matrix.tex
│   └── elasticnet_summary.tex
│
├── diagnostics/
│   ├── vif_{algo}_{model}.csv           # VIF after fit (all predictors)
│   ├── vif_removed_predictors_{algo}_{model}.csv  # Predictors removed if VIF > 10
│   ├── correlation_verification_{algo}.csv
│   ├── dp_composition_check.txt
│   ├── assumption_summary_{algo}_{resp}.txt
│   ├── residual_tests_{algo}.csv        # BP test, DW test, etc.
│   ├── se_comparison_{algo}_{resp}.csv  # Sandwich vs. standard SE
│   ├── smearing_factors.csv             # Pooled and family-specific φ
│   ├── full_sample_coefs_{algo}_{resp}.csv
│   ├── zero_event_families.txt
│   └── README.md                        # Index of diagnostics
│
└── feature_importance/
    ├── standardized_beta_{algo}_{resp}.csv
    ├── permutation_importance_{algo}_{resp}.csv
    ├── delta_r2_partitioning_{algo}_{resp}.csv
    └── elasticnet_nonzero_coefs.csv
```

### 5.2 File Naming Conventions

| Entity | Pattern |
|--------|---------|
| Prepared data | `{Algorithm}.pkl` (Greedy, DP, BandB) |
| Model results | `{family}_metrics_{algorithm}_{response}.csv` |
| CV fold data | `{cv_type}_folds_{family}_{algorithm}_{response}.csv` |
| Coefficients | `full_sample_coefs_{family}_{algorithm}_{response}.csv` |
| Standardised β | `standardized_beta_{algorithm}_{response}.csv` |
| Permutation importance | `permutation_importance_{algorithm}_{response}.csv` |
| Δ-R² partitioning | `delta_r2_partitioning_{algorithm}_{response}.csv` |
| Diagnostics | `{diagnostic_type}_{algorithm}_{response}.csv` or `.png` |
| LaTeX tables | `{table_type}_{algorithm}.tex` |

### 5.3 Reproducibility Guarantees

- All random processes use `numpy.random.default_rng(42)` (not global `numpy.random`).
- Intermediate DataFrames are saved as `.pkl` (full precision) not CSV (float rounding).
- Each script reads from `output/prepared/` and `output/results/` — scripts can be
  re-run independently as long as dependencies are satisfied.
- A `requirements.txt` is generated alongside the pipeline with all package versions
  pinned.

---

## 6. Verification Checkpoints

Each milestone must pass its verification before the next milestone begins.

### Phase 3.3.1 — Checkpoint

- [ ] `config.py` imports without errors
- [ ] All 6 utility modules have passing import tests
- [ ] `1_prepare_data.py` runs to completion
- [ ] `Greedy.pkl` contains exactly columns: all Group A (35), all Greedy metrics (6),
      n, log(n), cap_mode, family dummies (4), `optimality_gap`, `log_time_millis`
- [ ] `DP.pkl` contains exactly columns: all Group A (35), all DP metrics (15),
      n, log(n), cap_mode, family dummies (4), `log_time_millis`, `log_memory_mb`, `fill_rate`
- [ ] `BandB.pkl` contains exactly columns: all Group A (35), B&B metrics after
      global exclusions (~24), n, log(n), cap_mode, family dummies (4),
      `log_time_millis`, `optimal`, `log_nodes_explored`, `solution_gap`
    - [ ] Correlation-block filter removes exactly: cells_allocated, nonzero_value_states,
      capacity_density, solution_density, cell_value_variance, include_count
- [ ] Per-algorithm correlation report shows no Δ|r| > 0.10 for block-defining pairs
- [ ] DP compositional check output is written to disk
- [ ] Greedy `optimality_gap` has range [0, 1]; values match manual computation on
      a random sample of 5 rows
- [ ] B&B `solution_gap` = 0 for all complete rows, > 0 for incomplete rows

### Phase 3.3.2 — Checkpoint

- [ ] All 5 OLS models converge (statsmodels reports no singular matrix warnings)
- [ ] Per-fold LOFO R² values are within expected range (0.5–0.99) for each model
- [ ] ΔR²_adj (M2 − M1) is positive for all 5 models (execution metrics should add
      some value)
- [ ] Standardised β CIs are finite for all predictors
- [ ] Back-transformed RMSE < raw RMSE on log scale (smearing correction is working)
- [ ] 5-fold CV results are within ±0.05 R² of LOFO results (if not, note the
      discrepancy for discussion)
- [ ] Cluster-robust SEs are computed and differ from naive SEs (expected given
      within-instance correlation)
- [ ] Bootstrap ΔR² CI is computed (1999 resamples, pairs bootstrap stratified by family,
      percentile CI) for all 5 OLS models

### Phase 3.3.3 — Checkpoint

- [ ] Both fractional logit models converge (GLM `converged` flag = True)
- [ ] All predictions are in [0, 1] (clipped if necessary)
- [ ] Pseudo-R² for `optimality_gap` M1 is lower than OLS R² for same data
      (pseudo-R² is on a different scale; this is expected — verify by
      comparing to McFadden's reference: pseudo-R² > 0.2 is "excellent")
- [ ] Sandwich vs. standard SE ratio is documented; if ratio > 2 for any coefficient,
      bootstrap SEs are computed as backup
- [ ] `optimality_gap` link test: ŷ² coefficient is not significant (p > 0.05)

### Phase 3.3.4 — Checkpoint

- [ ] Elastic-net converges for all 5 LOFO folds (saga solver reaches tolerance)
- [ ] λ path plots show clear minimum deviance for each fold
- [ ] Number of nonzero coefficients at optimal λ: between 10 and 30 (not 0 and not 67)
- [ ] Zero-event families are correctly identified (should be at least Uncorrelated
      which has 0 incomplete runs)
- [ ] For zero-event folds, Brier score is the only reported metric
- [ ] Hurdle model part 1 (logistic) converges
- [ ] Hurdle model part 2 (fractional logit on n=197) converges
- [ ] Combined hurdle predictions are in [0, 1]
- [ ] Elastic-net λ stability: log(λ) SD across folds < 2.0 (or documented)

### Phase 3.3.5 — Checkpoint

- [ ] Standardised β rankings are computed for all OLS and fractional logit models
- [ ] Importance rankings are not dominated by a single predictor type
      (e.g., execution metrics should appear in top-10 for most models)
- [ ] Permutation importance has finite mean ± SD for all predictors
- [ ] Δ-R² partitioning results sum to approximately the total ΔR² (M2 − M1)
      (within rounding, ≈ total — note: partial contributions don't sum exactly
      due to correlation, but they should be in the same ballpark)
- [ ] Elastic-net nonzero coefficients are visually interpretable
- [ ] Top-3 consistent across standardised β, permutation importance, and Δ-R²
      (if not, the discrepancy is itself a finding to report)

### Phase 3.3.6 — Checkpoint

- [ ] All diagnostic figures generated without matplotlib errors
- [ ] VIF for all predictors ≤ 10 in every model (or documented)
- [ ] VIF-thinned ΔR² comparison available if any VIF > 10 found
- [ ] Q-Q plots show no extreme violations (heavy tail deviation is acceptable
      at n=6000; systematic S-shape or gaps are not)
- [ ] Breusch-Pagan p < 0.05 is expected (heteroscedasticity is common) — what
      matters is whether the residual-vs-fitted plot shows a clear pattern
- [ ] No Cook's distance > 1 for any observation (if any exist, document them)
- [ ] Smearing factors φ are computed: pooled and family-specific
- [ ] Calibration curves for elastic-net: predicted vs. observed probabilities
      should be near the diagonal (Brier < 0.05 indicates good calibration)
- [ ] Link test for both fractional logit models: ŷ² p > 0.05 (or flagged)

### Phase 3.3.7 — Checkpoint

- [ ] Capacity-mode stratified ΔR² values differ by ≤ 0.05 from pooled (or documented)
- [ ] B&B complete-only ΔR² differs by ≤ 0.05 from full-sample (or documented)
- [ ] Family-level ΔR² are computed if LOFO heterogeneity is high (SD > 0.15)
- [ ] DP compositional adjustment results (if applicable) are documented

### Phase 3.3.8 — Checkpoint

- [ ] `master_results.csv` has exactly 9 × 2 = 18 rows (9 responses × M1/M2)
- [ ] BH-adjusted q-values for 4 confirmatory models are < 0.05 or > 0.05 as computed
- [ ] All LaTeX tables compile (run `pdflatex` or at minimum `pylatex` format check)
- [ ] Primary results table shows: R²/pseudo-R², RMSE/Brier, ΔR²_adj, Cohen's f²,
      BH adj. p (confirmatory) or unadjusted p (exploratory)
- [ ] Feature importance table shows top-5 execution metrics per model with CIs
- [ ] Family heterogeneity matrix shows fold-level R² (5 rows × 18 columns)
- [ ] Elastic-net summary shows nonzero count, λ path, per-family Brier/AUC

---

## 7. Risk Assessment

### 7.1 Convergence Risks

| Risk | Models Affected | Likelihood | Impact | Mitigation |
|------|----------------|------------|--------|------------|
| OLS singular design matrix | Any OLS model | Low | Model cannot be estimated | Correlation-block filter (§6.2 step 1) and structural exclusions (§4.6) prevent known singularities. Post-fit VIF diagnostics (§11.1) catch any remaining collinearity for discussion. If still singular, check for remaining collinear pairs or constant columns not caught by global exclusions |
| GLM (fractional logit) non-convergence | Greedy `optimality_gap`, DP `fill_rate` | Low–Medium | Model fit fails | Increase max_iter (default 100 → 500). If still fails, try `method='bfgs'` or `'newton'`. If response has values exactly 0 or 1, fractional logit can have boundary issues — Papke-Wooldridge QMLE is robust but statsmodels GLM may warn. Last resort: manually adjust boundary (clip to [ε, 1−ε]) |
| Elastic-net non-convergence (saga solver) | B&B `optimal` | Low | Model fit fails | Increase `max_iter` (default 1000 → 10000). Ensure data is standardised. `saga` is robust but slow; `liblinear` could be used for L1-only but we need elastic-net. If saga truly fails, fall back to `sag` (no L1) or `lbfgs` (no L1) with reduced α |
| Hurdle part 2 (n=197) convergence | B&B `solution_gap` | Medium | Model fit fails | Only 197 positive-gap observations. If fractional logit on this subset fails to converge, either increase max_iter, simplify by using OLS on logit(gap) as a descriptive substitute, or note non-convergence as a limitation |
| VIF post-fit diagnostic iterative removal never terminates | Any (diagnostic) | Low | Infinite loop during VIF-thinned refit | Set `max_rounds=20`. If removal continues beyond 20 rounds, stop and report all VIF values > 10 as-is |

### 7.2 Numerical Stability Risks

| Risk | Models Affected | Likelihood | Impact | Mitigation |
|------|----------------|------------|--------|------------|
| Log of zero | Log-transformed responses/predictors | Low | -inf in data | Add ε = 1e-9 before log for responses (§2.3). For predictors, check for zeros and add small ε or use log1p where appropriate |
| Arctanh of ±1 | Correlation predictors | Low | ±inf in data | Clip to ±0.9999 before arctanh (§5.2). Verify no correlation = ±1.0000 in data |
| Duan's smearing with extreme residuals | Log-transformed models | Low | φ >> 1 | Compute separately for each family. If family-specific φ > 5, flag as potential heteroscedasticity issue and report raw (un-smeared) back-transform as lower bound |
| Pseudo-R² computation with near-perfect fit | Any | Low | Division by zero | If ln(L_model) ≈ 0 (near-perfect fit), pseudo-R² = 1 − 0/ln(L_null) = 1. This is fine. Guard against ln(L_null) = 0 (should not happen for any non-trivial model) |
| Bootstrap CI with small n | Hurdle part 2 (n=197) | Medium | Wide CIs, unstable | Use BCa (bias-corrected accelerated) bootstrap instead of percentile. Increase resamples to 9999 for this model. If estimates are unstable, report descriptive stats only |

### 7.3 Implementation Risks

| Risk | Phase | Likelihood | Impact | Mitigation |
|------|-------|------------|--------|------------|
| Missing column in transformed data | 3.3.1 | Medium | Pipeline fails at model fit | Each model script should assert that required columns exist before fitting. Write a `validate_columns()` check |
| Family dummies create perfect collinearity after correlation-block filter | 3.3.2 | Low | Singular matrix | The reference category (Uncorrelated) prevents this for the dummies. But if block-filter drops other columns, some combination could become rank-deficient. Check with `numpy.linalg.matrix_rank` before fit |
| Elastic-net λ grid too coarse | 3.3.4 | Low | Suboptimal λ chosen | Use sklearn's `LogisticRegressionCV` with `Cs=50` (50 log-spaced values). If LOFO fold λ varies widely, increase to 100 |
| Memory pressure from permutation importance | 3.3.5 | Low | OOM for large models | Permutation importance refits models 20× per predictor. For OLS this is fast (~10ms per refit). For elastic-net this is slow (~1s per refit). Total: 20 × 21 × ~1s = ~7 min for elastic-net, acceptable |
| Back-transformed RMSE computation on held-out folds | 3.3.2 | Low | Wrong metric on log-scale | Compute smearing φ from training-set residuals only (not test-set). Apply φ to test-set predictions. This avoids data leakage |
| Statsmodels GLM `family=Binomial()` handles proportion response incorrectly | 3.3.3 | Medium | Incorrect standard errors | statsmodels expects `endog` as 2-column array for binomial counts. For fractional logit with proportions, pass `endog` as the proportion and use `var_weights` = 1 (or the number of trials). The `HC3` covariance type provides robust SEs regardless. Verify that coefficient estimates match Papke-Wooldridge (1996) on a test dataset. **Implement a unit test:** generate synthetic data with known logit coefficients, fit fractional logit, verify coefficients are recovered |

### 7.4 Data Quality Risks

| Risk | Phase | Likelihood | Impact | Mitigation |
|------|-------|------------|--------|------------|
| B&B `solution_gap` computation: division by zero if `optimal_value = 0` | 3.3.1 | Low | -inf in data | Check for `optimal_value = 0` rows. If any exist, add small ε to denominator or exclude that row. From Phase 3.1, `optimal_value` should always be positive (knapsack solution value) |
| Greedy `optimality_gap` DP-join: missing DP match | 3.3.1 | Low | Missing rows | The join is on `(instance_id, capacity_mode)`; both exist for all Greedy and DP rows. Verify join completeness: all 6,000 Greedy rows should match exactly one DP row |
| String histograms not fully excluded | 3.3.1 | Low | TypeError in model fit | `depth_histogram`, `queue_histogram`, `improvement_depths`, `improvement_nodes` are strings. Verify they are in the global exclusion list (§3.2) and not present in any feature matrix |

---

## 8. Final Deliverable

This document (`governance/PHASE_3_3_IMPLEMENTATION_PLAN.md`) is the final deliverable
of this session. It serves as the sole implementation roadmap for Phase 3.3.

### Document Status

- [x] Phase 3.2 design fully read and understood (818 lines)
- [x] All 9 models enumerated with full specifications
- [x] Preprocessing pipeline designed with shared utilities
- [x] Output structure designed with reproducibility in mind
- [x] Execution order defined as 8 independently verifiable milestones
- [x] Verification checkpoints specified for each milestone
- [x] Implementation risks identified with mitigations
- [x] No changes to methodology — faithful to frozen design

### Next Steps (for the implementer)

1. Create directory structure: `mkdir -p Phase_3_3_Modeling/{utils,scripts,output/{prepared,results,cross_validation,figures,tables,diagnostics,feature_importance}}`
2. Begin Phase 3.3.1: write `config.py`, then `utils/` modules, then `1_prepare_data.py`
3. Run `1_prepare_data.py` and verify against Phase 3.3.1 checkpoint
4. Proceed milestone by milestone, verifying each checkpoint before moving on
5. Do not skip checkpoints — unverified previous work invalidates all downstream results
