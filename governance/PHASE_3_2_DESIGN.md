# Phase 3.2 — Predictive Statistical Modeling: Design Document (Revised)

**Project:** Knapsack Empirical Comparison (Greedy, DP, B&B)
**Dataset:** `out/results/canonical_dataset.csv` (18,000 rows × 110 columns)
**Phase 3.1 Status:** Complete — PASS WITH MINOR ISSUES (Audit verified)
**Design Date:** 2026-07-21
**Revision Date:** 2026-07-21
**Primary Objective:** RQ3 — Explanatory power of internal execution metrics beyond instance characteristics
**Audit Status:** Design passes independent audit (see `governance/PHASE_3_2_AUDIT_2.md`)

---

## 1. Research Question and Analytical Strategy

### RQ3 (verbatim)

> **To what extent do algorithm-specific internal execution metrics provide additional explanatory power beyond instance characteristics for modeling runtime and solution quality, and which execution metrics are most influential for each algorithm across diverse knapsack instance families?**

### Translation into testable hypotheses

For each algorithm *a* ∈ {Greedy, DP, B&B} and each primary response variable *y<sub>a</sub>*:

| Hypothesis | Formal Statement |
|---|---|
| **H<sub>0</sub>** (no added value) | *R<sup>2</sup><sub>adj</sub>(M2) − R<sup>2</sup><sub>adj</sub>(M1) = 0* — execution metrics contribute no unique variance beyond instance characteristics |
| **H<sub>a</sub>** (added value) | *R<sup>2</sup><sub>adj</sub>(M2) > R<sup>2</sup><sub>adj</sub>(M1)* — execution metrics explain significant additional variance |
| **Secondary** | Identify the top-*k* execution metrics by standardized coefficient magnitude / permutation importance within M2 |

### Analytical approach

Two-level nested model comparison per algorithm–response pair:
- **Model 1 (baseline):** Instance characteristics only
- **Model 2 (full):** Instance characteristics + algorithm-specific execution metrics

Incremental *F*-tests, Δ*R<sup>2</sup><sub>adj</sub>*, and feature importance rankings address both parts of RQ3.

### Confirmatory vs. exploratory designations

Models are designated as confirmatory or exploratory to control multiplicity and to align reader expectations with statistical power:

| Algorithm | Response | Status | Rationale |
|---|---|---|---|
| Greedy | `log_time_millis` | **Confirmatory** | Core runtime question; well-powered |
| Greedy | `optimality_gap` (fractional) | **Confirmatory** | Core quality question (heuristic) |
| DP | `log_time_millis` | **Confirmatory** | Core runtime question |
| DP | `log_memory_mb` | **Exploratory** | Predictor exclusions reduce scope; potential circularity concerns |
| DP | `fill_rate` | **Supplementary** | Alternative efficiency dimension |
| B&B | `log_time_millis` | **Confirmatory** | Core runtime question |
| B&B | `optimal` (binary) | **Exploratory** | Low event count limits reliability |
| B&B | `log_nodes_explored` | **Supplementary** | Near-circularity with `nodes_generated` limits RQ3 interpretation |
| B&B | `solution_gap` (hurdle) | **Supplementary** | Limited to 197 positive-gap observations; complex two-part model |

Confirmatory models are tested at α = 0.05 with Benjamini-Hochberg adjustment across the 4 confirmatory comparisons. Exploratory models report unadjusted p-values with explicit caveats. Supplementary models report effect sizes without formal inference.

---

## 2. Response Variables

### 2.1 Definition per algorithm

| Algorithm | Runtime Response | Quality/Efficiency Response | Secondary / Supplementary |
|---|---|---|---|
| **Greedy** | `log_time_millis` | `optimality_gap` (fractional, [0,1]) | — |
| **DP** | `log_time_millis` | `log_memory_mb` (space efficiency) | `fill_rate` (table utilization, supplementary) |
| **B&B** | `log_time_millis` | `optimal` (binary: search completeness) | `log_nodes_explored` (search efficiency, supplementary); `solution_gap` (continuous quality, supplementary) |

**Note on `solution_value`:** `solution_value` is NOT used as a response variable in this design. It appears in the dataset as a benchmark outcome for all three algorithms. See §6.1 (Block 4) for its role in multicollinearity management. For Greedy, `optimality_gap` is computed externally by comparing Greedy's `solution_value` to DP's ground-truth `optimal_value`. For B&B, a supplementary continuous quality gap (`solution_gap`) is described below.

### 2.2 Rationale

- **`log_time_millis`:** Common across all three. Phase 3.1 confirms skew=9.4, range spanning 6+ orders of magnitude. Log transform normalizes residuals.

- **`optimality_gap` (Greedy):** `optimality_gap` is structurally missing from Greedy rows in the canonical dataset. It is computed externally by joining `(instance_id, capacity_mode)` to the DP row's `solution_value` (the ground-truth optimum, since DP is exact): *gap = (DP_solution − Greedy_solution) / DP_solution*. This yields a proportion in [0, 1]. Because the response is bounded with substantial mass at zero (Greedy is provably exact on Inverse Correlated instances, yielding gap=0 for all 1,200 such rows), OLS is inappropriate. A **fractional logit** model (GLM with binomial family, logit link) is used instead (§7.2). **Do NOT log-transform or square-root-transform** — the bounded-support model handles these properties naturally.

- **`log_memory_mb` (DP):** DP's memory footprint is its primary constraint. Phase 3.1 reports skew=28.4 for `memory_bytes`. Log transform is mandatory. **Important:** This model is designated exploratory because the DP execution metrics `cells_allocated`, `nonzero_value_states`, and `zero_value_states` must be excluded from M2 predictors to avoid a near-circular relationship (DP memory *is* the table indexed by these metrics). With these exclusions, the test of RQ3 is conservative — only non-size-related execution metrics (e.g., `dp_sum_improvement_amount`, `fill_rate`, `mean_cell_value`) are tested for additional explanatory power.

- **`fill_rate` (DP, supplementary):** `fill_rate = nonzero_value_states / cells_allocated` measures DP table utilization efficiency. Bounded [0, 1]; modeled with fractional logit. This response provides a complementary efficiency perspective. Because `fill_rate` is computed from `cells_allocated` and `nonzero_value_states`, those two predictors (and `fill_rate` itself) are excluded from M2 for this response to prevent near-circularity (§4.6).

- **`optimal` (B&B):** Binary indicator: *true* (search completed within MAX_NODES) vs. *false* (terminated at cap). 197/6000 (3.28%) are incomplete. Because the event count is low relative to the number of candidate predictors (EPV ≈ 3 for the full M2 specification), **elastic-net regularized logistic regression** is used to prevent overfitting (§7.2). This model is designated exploratory.

- **`log_nodes_explored` (B&B, supplementary):** Skew=8.9. Even when B&B completes, node count varies by orders of magnitude across families. **Important:** The execution metrics `nodes_generated` and `internal_nodes` are excluded from M2 predictors for this specific response because they are near-identical to `nodes_explored` (the ratio `explored_generated_ratio` is 96.8% = 1.0). Without this exclusion, the model would be near-circular. This model is supplementary only.

- **`solution_gap` (B&B, supplementary):** For B&B rows, a continuous quality gap can be computed as *(optimal_value − solution_value) / optimal_value*. This gap is 0 for all 5,803 complete runs and positive for the 197 incomplete runs. This provides a continuous complement to the binary `optimal` model. Because the response has a point mass at zero with a continuous right tail, a two-part (hurdle) model is used: logistic for gap=0 vs. gap>0, then fractional logit for the positive gap values. This is supplementary only due to its complexity and the small number of positive-gap observations.

### 2.3 Response variable transformations (summary)

| Response | Transform / Model | Formula / Link | Justification |
|---|---|---|---|
| `time_millis` | log | *y′ = ln(y + ε)*, ε = 1e-9 | Skew=9.4, 6-order magnitude range |
| `memory_mb` | log | *y′ = ln(y + ε)* | Skew=28.4 |
| `optimality_gap` | none (fractional logit) | logit(μ) = Xβ | Bounded [0,1]; mass at zero; logit link handles boundaries |
| `fill_rate` | none (fractional logit) | logit(μ) = Xβ | Bounded [0,1] proportion |
| `nodes_explored` | log | *y′ = ln(y + 1)* | Zero counts exist; skew=8.9 |
| `optimal` (binary) | none (logistic, elastic-net) | logit(π) = Xβ | Logistic link; elastic-net for regularization |
| `solution_gap` (B&B) | two-part hurdle | logistic(0 vs >0) + logit(μ for >0) | Point mass at zero; continuous tail |

---

## 3. Predictor Groups

### 3.1 Group A: Instance Characteristics (35 features)

Identifiers and capacity-related columns are excluded from the predictor set (see §4). The remaining instance characteristics span 7 sub-domains:

| Sub-domain | Columns | Count |
|---|---|---|
| Basic statistics | `total_weight`, `total_value`, `mean_weight`, `mean_value`, `median_weight`, `median_value`, `std_weight`, `std_value`, `min_weight`, `max_weight`, `min_value`, `max_value` | 12 |
| Distribution descriptors | `weight_cv`, `value_cv`, `weight_skewness`, `value_skewness`, `weight_kurtosis`, `value_kurtosis` | 6 |
| Capacity descriptors | `capacity_ratio`, `slack`, `average_fillable_items` | 3 (after dropping `capacity`) |
| Correlation descriptors | `pearson_corr`, `spearman_corr`, `kendall_corr` | 3 |
| Ratio descriptors | `mean_ratio`, `median_ratio`, `std_ratio`, `ratio_entropy`, `unique_ratio_count`, `duplicate_ratio_fraction` | 6 |
| Diversity descriptors | `unique_weights`, `unique_values`, `unique_pairs`, `duplicate_items`, `duplicate_pairs` | 5 |
| **Total** | | **35** |

Group A predictors are fixed across all algorithm models. The same 35 instance characteristics appear in M1 and M2 for every algorithm.

### 3.2 Group B: Algorithm-Specific Execution Metrics

Group B predictors vary by algorithm. Within each algorithm, additional model-specific exclusions apply to prevent near-circular predictor–response relationships.

**B&B execution metrics (36 defined, ~24 usable after global exclusions):**

| Sub-domain | Columns | Count (after global excl.) |
|---|---|---|
| Node counts | `nodes_generated`, `internal_nodes` | 2 (excluded from `log_nodes_explored` M2; see §4.6) |
| Depth | `max_depth`, `mean_depth`, `median_depth` | 3 (drop `min_depth`: constant) |
| Queue | `mean_queue_size`, `final_queue_size` | 2 |
| Bounds | `bound_variance`, `mean_bound_gap`, `bound_gap_variance` | 3 (see §6.3 for exclusion of `mean_bound`) |
| Pruning | `pruned_by_bound`, `pruned_by_cap` | 2 |
| Branching | `left_branches`, `right_branches`, `explored_children`, `skipped_children`, `skipped_infeasible`, `skipped_by_bound`, `avg_branching_factor` | 7 |
| Improvements | `improvement_count`, `sum_improvement_amount`, `mean_improvement_amount`, `last_improvement_node` | 4 |
| Ratios | `pruned_generated_ratio` | 1 |
| **Total usable (global)** | | **~24** |

**Globally excluded from B&B metrics:** `leaf_nodes` (constant 0), `min_depth` (constant 0), `skipped_by_cap` (constant 0 — dead code), `first_improvement_node` (constant 1), `explored_generated_ratio` (quasi-constant, 96.8% = 1.0), `depth_histogram` (string), `queue_histogram` (string), `improvement_depths` (string), `improvement_nodes` (string), `mean_bound` (collinear with `solution_value` per §6.3).

**DP execution metrics (15 defined, 14 usable after global exclusions):**

| Sub-domain | Columns | Count (after global excl.) |
|---|---|---|
| Evaluations | `total_evaluations`, `include_count`, `exclude_count`, `tie_count`, `include_ratio` | 5 |
| Cell state | `zero_value_states`, `mean_cell_value`, `updates_per_cell` | 3 |
| Table structure | `cells_allocated`, `nonzero_value_states`, `fill_rate` | 3 |
| Improvements | `dp_sum_improvement_amount`, `dp_mean_improvement_amount` | 2 |
| **Total usable (global)** | | **~14** |

**Model-specific exclusions for DP:** `cells_allocated`, `nonzero_value_states`, and `zero_value_states` are excluded from M2 when the response is `log_memory_mb` (near-circular; see §2.2, §4.6). Additionally, `fill_rate`, `cells_allocated`, and `nonzero_value_states` are excluded from M2 when the response is `fill_rate` (deterministic relationship).

**Greedy execution metrics (6 defined, all usable):**

| Sub-domain | Columns | Count |
|---|---|---|
| Selection | `selected_count`, `last_selected_position`, `first_skipped_position` | 3 |
| Utilization | `solution_density`, `residual_capacity`, `capacity_utilization` | 3 |
| **Total** | | **6** |

No model-specific exclusions for Greedy.

### 3.3 Per-algorithm correlation verification

Correlation blocks identified in Phase 3.1 (§6.1) were computed on the pooled dataset. Before pre-filtering, correlations are re-computed within each algorithm's subset to verify that block structure is preserved. This is particularly important for blocks spanning metrics from different algorithm groups (e.g., Block 2 includes `capacity_density` (DP) and `solution_density` (Greedy), which never co-occur in the same row and therefore cannot produce the pairwise correlation reported in pooled analysis — these are re-evaluated per algorithm).

### 3.4 Compositional check for DP evaluation metrics

Before including DP evaluation counts in any model, verify whether `include_count + exclude_count + tie_count = total_evaluations` holds exactly or approximately. If the relationship is exact, include only a subset (e.g., `total_evaluations` plus ratios) to avoid exact linear dependence. Document the finding in the analysis output.

---

## 4. Variable Exclusions (from Phase 3.1 Report + Audit)

### 4.1 Constant variables (zero variance) — EXCLUDE (all models)

| Variable | Category | Reason |
|---|---|---|
| `first_improvement_node` | BB metric | All B&B rows = 1 (first improvement always at node 1) |
| `leaf_nodes` | BB metric | All B&B rows = 0 (bound pruning prevents leaf recording) |
| `min_depth` | BB metric | All B&B rows = 0 (root node is always minimum) |
| `seed` | Identifier | All 18,000 rows = 42 (single-seed design) |
| `skipped_by_cap` | BB metric | Always 0 (`recordSkippedByCap()` is dead code, never called) |

### 4.2 Near-constant variables — EXCLUDE (all models)

| Variable | Category | Reason |
|---|---|---|
| `explored_generated_ratio` | BB metric | 96.8% of B&B rows = 1.0; near-singular design matrix |

### 4.3 Redundant/derived variables — EXCLUDE (all models)

| Variable | Category | Reason |
|---|---|---|
| `time_nanos` | Benchmark outcome | Exact linear transform: `time_millis = time_nanos / 1e6` |
| `capacity` | Identifier | Collinear with `cells_allocated` and `average_fillable_items` (r = 0.9997) |
| `algorithm` | Identifier | Models are fit per algorithm; no cross-algorithm pooling |
| `instance_id` | Identifier | Non-informative for prediction; random effect candidate |

### 4.4 Structurally missing — HANDLED SEPARATELY

| Variable | Algorithm | Handling |
|---|---|---|
| `optimal_value` | Greedy | Do not impute. Use DP's `solution_value` (joined by `instance_id`, `capacity_mode`) to compute Greedy's `optimality_gap` externally |
| `optimality_gap` | Greedy | Computed externally per §2.2; modeled with fractional logit |
| `optimal` | B&B | Only relevant for B&B rows; naturally missing for Greedy/DP |

### 4.5 Variables retained with caution

| Variable | Issue | Mitigation |
|---|---|---|
| `memory_mb` (DP/B&B response) | 3,517 of 18,000 rows = 0 MB (Greedy) | Greedy memory is trivially small; not used as Greedy response. For DP/B&B models, add small epsilon before log transform. Greedy `memory_mb` contributions in training data are excluded by per-algorithm subsetting |
| `n` (predictor in Group A) | Part of identifiers; known nonlinear relationship with performance | Retained as critical covariate. Both `n` and `log(n)` are included by default (§5.3) |
| `capacity_mode` (in model) | Binary (fixed/scaled) | Included as dummy variable; sensitivity analysis with separate models per mode (§12.1) |

### 4.6 Model-specific structural exclusions (prevent near-circularity)

These exclusions are applied to M2 for specific response models only. They are not global exclusions — the predictors remain available for other response models of the same algorithm.

| Response Model | Excluded from M2 Predictors | Rationale |
|---|---|---|---|
| DP `log_memory_mb` | `cells_allocated`, `nonzero_value_states`, `zero_value_states` | DP memory *is* the table indexed by these metrics. Including them would be near-identity, making any ΔR² improvement trivially large and uninterpretable for RQ3 |
| DP `fill_rate` | `fill_rate`, `cells_allocated`, `nonzero_value_states` | `fill_rate` is defined as `nonzero_value_states / cells_allocated`. Including `fill_rate` itself would be self-prediction; including its components would be near-deterministic. Directly analogous to the `log_memory_mb` exclusion |
| B&B `log_nodes_explored` | `nodes_generated`, `internal_nodes` | `nodes_explored` and `nodes_generated` are near-identical (explored/generated ratio = 96.8% = 1.0). Including them would be near-circular |
| All B&B models | `mean_bound`, `max_bound`, `min_bound` | Near-perfectly correlated with `solution_value` (r > 0.999), which is itself strongly associated with all B&B outcomes. Excluded to prevent near-singularity and circularity (see §6.3) |

These exclusions ensure that M2's improvement over M1 reflects genuine explanatory contributions of execution metrics, not definitional or near-identity relationships.

---

## 5. Required Transformations

### 5.1 Response variable transformations

See §2.3 table.

### 5.2 Predictor variable transformations

| Variable Group | Recommended Transform | Justification |
|---|---|---|
| `total_weight`, `total_value`, `total_evaluations` | Log | Skew > 5, wide range across n = 20–1000 |
| `average_fillable_items`, `slack` | Log or sqrt | Skew > 3, right-tailed |
| `unique_ratio_count`, `unique_weights`, `unique_values`, `unique_pairs`, `duplicate_items`, `duplicate_pairs` | Log or sqrt | Count variables, right-skewed |
| `bound_variance`, `sum_improvement_amount`, `pruned_by_bound` | Log | Skew > 3, wide range |
| `mean_bound_gap`, `bound_gap_variance` | Log | Right-skewed, wide range |
| `mean_queue_size`, `final_queue_size` | Log | Skew > 5, extreme right tail |
| `left_branches`, `right_branches`, `explored_children`, `skipped_children`, `skipped_infeasible`, `skipped_by_bound` | Log | Counts spanning orders of magnitude |
| `include_count`, `exclude_count`, `tie_count` | Log | Skew > 2.8, range millions |
| `updates_per_cell` | Log | Skew > 3.6 |
| Ratio variables (*.ratio, `fill_rate`, `solution_density`, `capacity_utilization`, `avg_branching_factor`) | None (raw) | Already bounded [0,1] or near-1; log inapplicable. If residuals indicate floor/ceiling effects, consider logit transform |
| `mean_ratio`, `median_ratio`, `std_ratio`, `ratio_entropy` | None (raw) or sqrt | Ratio-domain features; moderate skew |
| `pearson_corr`, `spearman_corr`, `kendall_corr` | Arctanh (inverse hyperbolic tangent) | Maps [-1, +1] → (-∞, +∞), improving linearity with response. Clip to ±0.9999 before transform to prevent infinite values at theoretical ±1. This is an *arctanh* unbounded-support transform, not a Fisher z-transform (which has a specific inferential meaning for sample correlations that does not apply here) |
| `include_ratio` (DP) | None (raw) | Bounded [0,1] |
| `selected_count` (Greedy) | None or sqrt | Integer bounded by n; range is n-dependent |
| `capacity_ratio` | None (raw) | Bounded (0, 1]; logit if needed |
| `dp_sum_improvement_amount`, `dp_mean_improvement_amount` | Log | Skew > 3.6 |
| `cells_allocated`, `nonzero_value_states`, `zero_value_states` | Log | Span orders of magnitude with n (note: excluded from DP `log_memory_mb` M2 per §4.6) |
| `nodes_generated`, `internal_nodes` | Log | Span orders of magnitude (note: excluded from B&B `log_nodes_explored` M2 per §4.6) |

### 5.3 Categorical and design predictors — encoding

| Variable | Encoding |
|---|---|
| `family` | One-hot (5 levels → 4 dummies). Reference: Uncorrelated (least pathological) |
| `capacity_mode` | Binary dummy: 0 = fixed (W=1000), 1 = scaled (W=0.5·Σw) |
| `n` | Include both linear `n` and `log(n)` as default. Rationale: the experimental design spans n ∈ {20, 50, 100, 200, 500, 1000} (50× range), and all three algorithms have known nonlinear scaling with n (Greedy: O(n log n); DP: O(nW); B&B: family-dependent polynomial/exponential). Including both terms captures the dominant scaling relationship without overfitting. If residual diagnostics indicate curvature beyond these terms, consider natural cubic splines with 3–4 df as a sensitivity analysis |

### 5.4 String/metrics requiring special handling

The following columns are string-encoded lists or histograms:
- `depth_histogram` (BB): Frequency array of node depths (up to ~1000 entries)
- `queue_histogram` (BB): Frequency array of queue sizes
- `improvement_depths` (BB): Depths at which improvements occurred
- `improvement_nodes` (BB): Cumulative node counts at improvements

**Handling:** These are excluded from initial M1/M2 models. As a supplementary analysis (if M2 still leaves substantial residual variance), extract scalar summary features:
- `depth_histogram` → Shannon entropy, mode, range, coefficient of variation
- `queue_histogram` → entropy, mode, burst ratio (peak / mean)
- `improvement_depths` → mean depth of improvement, depth span
- `improvement_nodes` → total improvement span

This exploration is documented but not part of the primary confirmatory analysis.

---

## 6. Handling of Multicollinearity

### 6.1 Identified correlation blocks (Phase 3.1, |r| > 0.95)

| Block | Variables | Max | Handling |
|---|---|---|---|
| **Block 1** — Instance/table size | `average_fillable_items`, `cells_allocated` (DP), `nonzero_value_states` (DP) | 0.9997 | One of {`average_fillable_items`, `cells_allocated`} retained across all models. For DP `log_memory_mb`, `cells_allocated` and `nonzero_value_states` are additionally excluded per §4.6 |
| **Block 2** — Capacity density | `capacity_ratio`, `capacity_density` (DP), `solution_density` (Greedy) | 0.994 | Only `capacity_ratio` retained. Note: `capacity_density` and `solution_density` belong to different algorithms; the pooled correlation is re-verified per-algorithm subset (§3.3) |
| **Block 3** — DP improvements | `dp_sum_improvement_amount`, `cell_value_variance` (DP), `include_count` (DP) | 0.981 | Only `dp_sum_improvement_amount` retained |
| **Block 4** — Bound values | `mean_bound`, `max_bound`, `min_bound`, `solution_value` | 0.999+ | `solution_value` is NOT a response variable in this design (see §2.1). However, bound metrics are near-perfectly correlated with `solution_value`, which is itself a strong proxy for algorithm outcomes. To prevent near-singularity, all three bound columns (`mean_bound`, `max_bound`, `min_bound`) are excluded from all B&B models. This is a structural exclusion, not a VIF-driven one |

### 6.2 Selection protocol

1. **Pre-filter** before model fitting: From each correlation block, retain the variable with the highest theoretical interpretability / lowest measurement error. Document the choice.
2. **Per-algorithm correlation verification:** Recompute correlation matrices within each algorithm's subset. If per-algorithm correlations deviate substantially from the pooled analysis (Δ|r| > 0.10 for a block-defining pair), note this and adjust pre-filtering decisions accordingly.
3. **VIF check** after fit: Compute variance inflation factor for all predictors in M1 and M2. Any variable with VIF > 10 triggers iterative removal (drop highest-VIF, refit, repeat until all VIF ≤ 10). VIF is computed within each algorithm subset (not pooled), ensuring algorithm-specific collinearity structure is respected.
4. **If removal changes Δ*R²* interpretation:** Report both raw and VIF-thinned results.

### 6.3 Block-specific decisions (consolidated)

| Block | Retain | Drop | Rationale |
|---|---|---|---|
| 1 | `average_fillable_items` | `cells_allocated`, `nonzero_value_states` (also excluded from DP memory model per §4.6) | Instance char (Group A) is the more fundamental size descriptor |
| 2 | `capacity_ratio` | `capacity_density` (DP), `solution_density` (Greedy) | `capacity_ratio` is the more fundamental dimensionless capacity descriptor |
| 3 | `dp_sum_improvement_amount` | `cell_value_variance`, `include_count` | Sum captures total DP improvement effort |
| 4 | — | `mean_bound`, `max_bound`, `min_bound` | `solution_value` is not a response but bound columns are near-perfectly correlated with it (r > 0.999). Including these would introduce near-singularity since `solution_value` is itself a strong proxy for all B&B outcomes. This is a structural exclusion applied to all B&B models. The `bound_variance`, `mean_bound_gap`, and `bound_gap_variance` metrics (which are not near-perfectly correlated with `solution_value`) are retained |

---

## 7. Model Hierarchy and Specification

### 7.1 Model structure

For each algorithm *a* and each response *y<sub>a</sub>*:

**Model 1 (baseline):** Instance characteristics only
```
y_a = β0 + β1·n + β2·log(n) + β3·capacity_mode + family_effects + Σ(γ_j · instance_feature_j) + ε
```
- Instance features: Group A (§3.1), after global exclusions (§4)
- `n`, `log(n)`, `capacity_mode`, `family` always included (design variables)

**Model 2 (full):** Instance characteristics + execution metrics
```
y_a = β0 + β1·n + β2·log(n) + β3·capacity_mode + family_effects + Σ(γ_j · instance_feature_j) + Σ(δ_k · exec_metric_k) + ε
```
- Execution metrics: Group B for algorithm *a* (§3.2), after global exclusions (§4) AND model-specific exclusions (§4.6), transforms (§5), and VIF thinning (§6)

### 7.2 Complete per-model specification

| Algorithm | Response | Distribution / Link | M1 Predictors | M2 Additional Predictors | Excluded from M2 (beyond global) | Status |
|---|---|---|---|---|---|---|
| **Greedy** | `log_time_millis` | OLS (Gaussian, identity) | Group A + n + log(n) + cap_mode + family (42 params) | 6 Greedy metrics (§3.2) | None | Confirmatory |
| **Greedy** | `optimality_gap` | Fractional logit (binomial, logit) | Same as above | Same 6 Greedy metrics | None | Confirmatory |
| **DP** | `log_time_millis` | OLS (Gaussian, identity) | Group A + n + log(n) + cap_mode + family (42 params) | 14 DP metrics (§3.2) | None beyond global | Confirmatory |
| **DP** | `log_memory_mb` | OLS (Gaussian, identity) | Same as above | DP metrics minus `cells_allocated`, `nonzero_value_states`, `zero_value_states` (~11 metrics) | `cells_allocated`, `nonzero_value_states`, `zero_value_states` (near-circular) | Exploratory |
| **DP** | `fill_rate` | Fractional logit (binomial, logit) | Same as above | DP metrics minus `fill_rate`, `cells_allocated`, `nonzero_value_states` (~11 metrics) | `fill_rate`, `cells_allocated`, `nonzero_value_states` (near-circular with `fill_rate = nonzero/cells`) | Supplementary |
| **B&B** | `log_time_millis` | OLS (Gaussian, identity) | Group A + n + log(n) + cap_mode + family (42 params) | ~21 B&B metrics (24 minus 3 bound metrics) | `mean_bound`, `max_bound`, `min_bound` (near-singular with `solution_value`) | Confirmatory |
| **B&B** | `optimal` | Elastic-net logistic (binomial, logit) | Same as above (no regularization for M1) | ~21 B&B metrics (elastic-net with CV-tuned λ) | Same + regularization applied | Exploratory |
| **B&B** | `log_nodes_explored` | OLS (Gaussian, identity) | Same as above | B&B metrics minus `nodes_generated`, `internal_nodes`, plus bound exclusions (~19 metrics) | `nodes_generated`, `internal_nodes` (near-circular) + bound metrics | Supplementary |
| **B&B** | `solution_gap` | Two-part hurdle | Same as above (part 1: logistic; part 2: fractional logit on gap>0) | Same exclusions as `log_nodes_explored` | Same as `log_nodes_explored` | Supplementary |

**Note on parameter counts:** Group A contains 35 instance characteristics. After removing `capacity` (§4.3) and adding `n`, `log(n)`, `capacity_mode`, and `family` (4 dummies), M1 has ~42 parameters (including intercept). These counts are approximate because VIF thinning (§6.2) may reduce them further.

### 7.3 Model families by response type

| Response Type | Model Family | Link / Loss | Estimation Method |
|---|---|---|---|
| `log_time_millis` (continuous, unbounded) | OLS linear regression | Identity | Maximum likelihood |
| `log_memory_mb` (continuous, unbounded) | OLS linear regression | Identity | Maximum likelihood |
| `optimality_gap` (fractional, [0,1]) | Fractional logit (Papke & Wooldridge, 1996) | Logit | Quasi-maximum likelihood; robust sandwich SEs |
| `fill_rate` (fractional, [0,1]) | Fractional logit | Logit | Quasi-maximum likelihood; robust sandwich SEs |
| `log_nodes_explored` (continuous) | OLS linear regression | Identity | Maximum likelihood |
| `optimal` (binary) | Elastic-net regularized logistic regression | Logit | Penalized maximum likelihood; α = 0.5 (equal L1/L2 mixing); λ tuned by cross-validation within each LOFO training fold |
| `solution_gap` (hurdle, zero-inflated) | Two-part: logistic (zero vs positive) + fractional logit (positive gap) | Logit + logit | QML for each part separately |

### 7.4 Rationale for fractional logit (Greedy `optimality_gap`, DP `fill_rate`)

Fractional logit (Papke & Wooldridge, 1996) is selected over alternatives for the following reasons:

| Criterion | Fractional Logit | Beta Regression | OLS on sqrt(gap) |
|---|---|---|---|
| Handles y = 0 naturally | Yes (logit link defined for [0,1]) | No (requires (0,1) domain; Smithson-Verkuilen transformation needed) | Yes (sqrt(0) = 0) |
| Handles y = 1 naturally | Yes | No (same issue) | Yes (sqrt(1) = 1) |
| Boundary mass at zero | Handled (consistent QMLE) | Requires zero-inflated beta (more complex) | Predictions can be < 0 |
| Variance specification | Robust to mis-specified variance (sandwich SEs) | Requires correct variance function | Requires HC3 SEs |
| Interpretability | Log-odds coefficients; easy marginal effects | Log-odds coefficients | OLS coefficients on sqrt scale |
| Reference | Papke & Wooldridge (1996); J. Econometrics | Ferrari & Cribari-Neto (2004); J. Appl. Stat. | Standard OLS |

Fractional logit is preferred because (a) it naturally handles the 1,200 Greedy rows with `optimality_gap = 0` (Inverse Correlated family) without requiring boundary transformations, (b) it provides consistent estimates under only correct mean specification (the variance can be mis-specified), and (c) its logit link ensures predictions remain in [0, 1].

### 7.5 Rationale for elastic-net logistic regression (B&B `optimal`)

Standard maximum-likelihood logistic regression is inappropriate for this model. With 197 `optimal=false` events and ~67 candidate predictors (39 instance + ~28 B&B metrics), the events-per-variable ratio is ~3, well below the recommended minimum of 10 (Peduzzi et al., 1996). Elastic-net regularization (Zou & Hastie, 2005) addresses this by:

1. **Shrinking coefficients toward zero** (L2 penalty), reducing variance and improving out-of-sample prediction
2. **Performing automatic feature selection** (L1 penalty), producing sparse models with only the most influential predictors
3. **Tuning the regularization strength λ** via cross-validation within each LOFO training fold, so the degree of shrinkage is data-adaptive

Elastic-net with α = 0.5 balances L1 and L2 penalties. The optimal λ is chosen as the value minimizing deviance in 5-fold CV within each training set (i.e., a nested CV: LOFO across families, with internal CV for λ). The resulting model is sparser than the full specification, reducing the effective EPV to an acceptable level. Coefficients at the optimal λ are reported; variable importance is derived from the nonzero coefficient magnitudes at the optimal λ.

**Comparison with alternatives:**

| Approach | Advantage | Disadvantage |
|---|---|---|
| Elastic-net (α = 0.5) | Handles grouped predictors; selects features; robust to collinearity | λ tuning adds computational cost |
| Ridge (α = 0) | Shrinks all coefficients; handles collinearity well | No feature selection; all 67 predictors retained |
| Lasso (α = 1) | Strong feature selection; simplest model | Tends to select one from a correlated group; may be unstable |
| PCA + logistic | Reduces dimensionality to top-K PCs | PCs are hard to interpret for RQ3 ("which metric matters?") |

Elastic-net with α = 0.5 is selected as the best balance between interpretability (nonzero coefficients identify specific influential metrics) and regularization adequacy.

### 7.6 Incremental test

For each algorithm–response pair:

- **OLS models:** Compute *F*-statistic: *F = [(RSS₁ − RSS₂) / (p₂ − p₁)] / [RSS₂ / (n − p₂)]*
- **Fractional logit models:** Compute quasi-likelihood ratio test (or Δ in Czuprow's pseudo-*R²*)
- **Elastic-net logistic:** Test Δ(AUC) and Δ(Brier score) between M1 and M2. Because M2 uses regularization, a standard likelihood-ratio test is not valid (the penalty shifts the likelihood). Instead, use cross-validated Δ(AUC) with a paired bootstrap CI
- Report Δ*R²<sub>adj</sub>* (or Δ pseudo-*R²*) with 95% bootstrap CI (pairs bootstrap, 1999 resamples, stratified by family)
- Effect size benchmark: Cohen's *f² = (R²₂ − R²₁) / (1 − R²₂)*
  - *f² ≥ 0.02*: small; *f² ≥ 0.15*: medium; *f² ≥ 0.35*: large
  - Note: These benchmarks were developed for balanced ANOVA and are approximate guides for nested regression

---

## 8. Cross-Validation Strategy

### 8.1 Primary: Leave-One-Family-Out (LOFO)

**Rationale:** Instance families (Uncorrelated, Weakly Correlated, Strongly Correlated, Inverse Correlated, Almost Strongly Correlated) represent structurally distinct problem classes. LOFO tests generalization to an unseen family — the most scientifically stringent and practically relevant evaluation.

**Procedure:**
1. For each fold *f* ∈ {1, …, 5}: hold out all rows where `family = family_f`
2. Train on remaining 4 families (~4,800 rows per algorithm)
3. Predict on held-out family (~1,200 rows per algorithm)
4. Compute *R²*, RMSE, MAE (or AUC, Brier for binary) on held-out fold
5. Report mean ± SD across 5 folds, **plus individual fold values**

**Variance consideration:** With only 5 folds, the LOFO estimate has 4 effective degrees of freedom. The 95% CI for mean LOFO *R²* is approximately ±2.78 × SE (using t₄). If the SD across folds is 0.10, the CI half-width is ~0.12. This is acknowledged as a limitation — fold-level values are reported to allow readers to assess heterogeneity, and the secondary 5-fold CV (§8.2) provides a lower-variance complementary estimate.

**Note:** LOFO may understate predictive performance for families with similar structure (e.g., Uncorrelated and Weakly Correlated). This is a feature, not a bug — it provides a conservative generalization estimate.

### 8.2 Secondary: 5-fold cross-validation (random, within algorithm)

Run standard 5-fold CV (shuffled, stratified by `family` × `capacity_mode`) for comparison. If LOFO and random CV results diverge substantially (>0.10 ΔR²), report both and discuss family-specific overfitting.

### 8.3 Cross-validation for B&B binary model (`optimal`)

**Elastic-net models:** For each LOFO fold, the regularization parameter λ is selected via internal 5-fold CV on the training set only (nested CV). This ensures the held-out family is never used for λ tuning.

**Zero-event families:** Some families (e.g., Uncorrelated) may have zero `optimal=false` instances. For these families:
- The held-out fold AUC is undefined (no positive class). Report Brier score as the primary metric (always computable) for these folds.
- For families with at least one event, report both AUC and Brier score.
- Record which families have zero events and note that the effective number of LOFO folds for AUC calculation is reduced.

### 8.4 Elastic-net λ selection

λ is selected via 5-fold CV within each LOFO training set, using the 1-SE rule (simplest model within 1 standard error of the minimum deviance). The selected λ is used to refit on the full training set before predicting the held-out fold. This nested CV procedure ensures no data leakage from the held-out family into model tuning.

### 8.5 Reproducibility seed

All random processes (CV splits, permutation shuffles, bootstrap resampling, train-test splitting for elastic-net internal CV) use `numpy.random.default_rng(42)`. The λ path for elastic-net is deterministic (coordinate descent) and does not require seeding beyond the CV folds.

---

## 9. Performance Metrics

### 9.1 Continuous responses (OLS / fractional logit)

| Metric | Formula | Usage |
|---|---|---|
| *R²* | 1 − RSS/TSS | Proportion of variance explained (OLS only) |
| Pseudo-*R²* (McFadden) | 1 − ln(L_model)/ln(L_null) | Fractional logit models |
| *R²<sub>adj</sub>* | 1 − [(1−R²)(n−1)/(n−p−1)] | Primary metric — penalizes model complexity (OLS) |
| RMSE | √(Σ(yᵢ − ŷᵢ)² / n) | On transformed scale (e.g., log-ms) |
| MAE | Σ|yᵢ − ŷᵢ| / n | On transformed scale |
| **Back-transformed RMSE** (log models) | √(Σ(exp(yᵢ) − exp(ŷᵢ)·φ)² / n), where φ = (1/n) Σ exp(eᵢ) | Interpretable in original units (ms, MB). Applies Duan's smearing estimator for bias-corrected back-transformation |
| MAPE | (100/n) Σ |(yᵢ − ŷᵢ) / yᵢ| | Percentage error (log-transform already approximates this) |

**Note on Duan's smearing:** For log-transformed responses, the naïve back-transform exp(ŷ) predicts the conditional median, not the mean. The smearing factor φ = mean(exp(residuals)) adjusts for this bias under homoscedasticity on the log scale. If Breusch-Pagan indicates heteroscedastic log-scale residuals, use family-specific smearing factors (stratified by family or capacity mode) as a sensitivity analysis.

### 9.2 Binary response (B&B `optimal`)

| Metric | Usage |
|---|---|
| AUC-ROC | Discriminative ability (only for families with ≥1 event) |
| Brier score | Calibration (always computable; primary metric for zero-event families) |
| Accuracy | Overall correct classification |
| Precision, Recall, F1 | For the minority class (`optimal=false`, 3.28%) |

### 9.3 Inference metrics and multiplicity control

| Metric | Usage |
|---|---|
| Δ*R²<sub>adj</sub>* (M2 − M1) | Primary RQ3 test — added explanatory power |
| Δ pseudo-*R²* (M2 − M1) | Fractional logit models |
| Δ AUC / Δ Brier score | B&B binary model (elastic-net) |
| Δ AIC / Δ BIC | Information criterion comparison (OLS; not valid for elastic-net) |
| Cohen's *f²* | Effect size of adding execution metrics |
| *F*-test / QLR-test *p*-value | Statistical significance of improvement |

**Multiplicity control:**
- **Confirmatory models (4 total):** Benjamini-Hochberg adjustment applied to the 4 primary ΔR² p-values. Results are reported at BH-adjusted q < 0.05.
- **Exploratory models (3 total):** Unadjusted p-values reported; explicit caveat that these are descriptive, not confirmatory.
- **Supplementary models (3 total + family/capacity subgroups):** Effect sizes reported without formal inference.

### 9.4 Elastic-net specific metrics

For the B&B binary model, the following are additionally reported:
- Number of nonzero coefficients at optimal λ (model sparsity)
- λ selection path (plot of deviance vs. log(λ) with 1-SE rule marker)
- Coefficient trace plot (coefficient magnitude vs. λ) for the top-10 metrics

---

## 10. Feature-Importance Methodology

### 10.1 Standardized regression coefficients (β weights)

Compute for all predictors in M2 (after centering and scaling all numeric predictors to mean = 0, SD = 1). Rank by |β|. Report with 95% profile-likelihood confidence intervals (OLS) or robust sandwich CIs (fractional logit).

**Applicability:** OLS and fractional logit models. Not applicable to elastic-net (coefficients are penalized and not on the same scale as unpenalized estimates).

**Advantage:** Directly interpretable — "a 1-SD increase in predictor *x* is associated with a β-SD change in *y*."
**Limitation:** Sensitive to correlated predictors (even after VIF thinning).

### 10.2 Permutation importance (model-agnostic)

For each predictor *x<sub>j</sub>*:
1. Permute *x<sub>j</sub>* (break association with *y*)
2. Recompute *R²* (or AUC, or Brier) on permuted data
3. Importance = *R²<sub>original</sub> − R²<sub>permuted</sub>*
4. Repeat 20× for stability; report mean ± SD

**Advantage:** Model-agnostic, captures both direct and interaction effects. Applicable to all model types including elastic-net.
**Reporting:** Top-10 metrics per algorithm–response pair. Separate rankings for instance characteristics vs. execution metrics.

### 10.3 Elastic-net coefficient magnitude (nonzero at optimal λ)

For the B&B binary model specifically, the nonzero coefficients at the optimal λ (chosen via 1-SE rule) are reported as an alternative importance ranking. Unlike standardized β from unpenalized models, these coefficients are biased toward zero (by design) but represent the subset of predictors with the strongest consistent association with `optimal`.

### 10.4 Delta-*R²* partitioning (incremental)

For each execution metric *m* in M2:
1. Fit M2 with all predictors except *m*
2. Δ*R²* = *R²(M2_full) − R²(M2_without_m)*
3. This measures the unique contribution of *m* beyond all other predictors

**Advantage:** Directly answers RQ3's second part ("which execution metrics are most influential").
**Limitation:** Order-dependent if pairwise interactions exist. The LMG metric (Lindeman-Merenda-Gold, averaging over all orderings) is the standard solution but is computationally infeasible for >20 predictors (2^p model fits required). Instead, Δ-R² partitioning is restricted to the top-10 metrics identified by permutation importance — a practical compromise that bounds the computational cost while focusing on the most influential predictors.

### 10.5 Reporting hierarchy

1. **Primary:** Δ*R²<sub>adj</sub>* (or Δ pseudo-*R²*) from the nested model comparison (M1 → M2), with BH-adjusted CIs for confirmatory models
2. **Secondary:** Top-5 execution metrics by standardized β (OLS/fractional logit) or nonzero coefficient magnitude (elastic-net), with 95% CIs
3. **Tertiary:** Permutation importance ranking of all predictors in M2, with instance characteristics and execution metrics separated
4. **Supplementary:** Delta-*R²* partitioning for top-10 execution metrics by permutation importance

**Cross-algorithm comparison note:** Because execution metric sets are algorithm-specific (no overlap between B&B metrics, DP metrics, and Greedy metrics), feature importance rankings are reported per-algorithm. Cross-algorithm comparisons of importance magnitude (e.g., "the top metric for B&B has β = 0.5 but the top metric for Greedy has β = 0.3") are not meaningful due to different response scales and predictor sets. Comparisons of *which types* of metrics matter (e.g., "bound-related metrics dominate for B&B, while selection-position metrics dominate for Greedy") are qualitative only.

---

## 11. Statistical Assumptions and Diagnostic Checks

### 11.1 Linear regression models (OLS — M1, M2 for continuous responses)

| Assumption | Diagnostic | Default Action / Remediation |
|---|---|---|
| **Linearity** | Partial residual plots (each predictor vs. residuals); Rainbow test | Add polynomial/spline terms; log-transform predictor |
| **Normality of residuals** | Q-Q plot with confidence envelope; residual histogram | **Prioritize visual diagnostics over formal tests.** At n ≈ 6000 per algorithm, Shapiro-Wilk and Anderson-Darling have enormous power and will reject normality for even negligible deviations. Formal tests are reported but not used as gatekeepers. If Q-Q plot shows substantial deviations (e.g., heavy tails, asymmetry), use robust regression (Huber-White) or quantile regression as sensitivity |
| **Homoscedasticity** | Residual-vs-fitted plot; Breusch-Pagan test | HC3 robust standard errors (default for inference); WLS if variance structure identifiable |
| **Independence** | Residual autocorrelation plot by `n` and by `instance_id`; Durbin-Watson test | **Cluster-robust standard errors by `instance_id` are the default** (not a contingency). The data have a grouped structure: each instance appears in two capacity modes (fixed/scaled), sharing the same weight/value structure. This induces within-instance residual correlation. Clustering by `instance_id` (6,000 clusters) accounts for this. If Durbin-Watson is reported, note it tests serial correlation (not meaningful without natural ordering) |
| **No multicollinearity** | VIF < 10 for all predictors | Iterative removal per §6.2 |
| **No influential points** | Cook's distance < 1; DFBETAS < 2/√n | Document; sensitivity analysis with/without high-influence points |
| **No missing predictors** | Confirm all predictors populated | Models fit per algorithm; all metrics 100% populated within algorithm |

### 11.2 Fractional logit models (Greedy `optimality_gap`, DP `fill_rate`)

Fractional logit (Papke & Wooldridge, 1996) requires fewer assumptions than OLS:

| Assumption | Diagnostic | Remediation |
|---|---|---|
| **Correct mean specification** | Link test (regress y on ŷ and ŷ²; ŷ² should not be significant) | Add nonlinear terms or alternative link (probit, complementary log-log) |
| **No extreme boundary influence** | Check sensitivity to boundary observations (gap = 0 or gap = 1) | Report with and without boundary transformations (Smithson-Verkuilen for beta regression as sensitivity) |
| **Robust SE validity** | Compare standard and sandwich SEs | If they diverge substantially (ratio > 2 for any coefficient), use bootstrap SEs |
| **No missing predictors** | Confirm all predictors populated | Same as §11.1 |

**No independence of irrelevant alternatives assumption** (fractional logit is not a multinomial model). **No normality assumption** (distribution-free QMLE).

### 11.3 Elastic-net logistic regression (B&B `optimal`)

| Assumption | Diagnostic | Remediation |
|---|---|---|
| **Linearity in logit** | Component + residual plots | Add interaction or spline terms; refit elastic-net on expanded basis |
| **No extreme separation** | Check that elastic-net selected λ produces finite coefficients | If λ → 0 (no regularization) produces separation, increase α toward 1 (more L1) |
| **Calibration** | Calibration curve (observed vs. predicted probability) | Platt scaling or isotonic regression if miscalibrated |
| **λ stability** | Check λ path stability across LOFO folds | If λ varies wildly (>1 SD on log scale), report λ range and use median λ |

**Note:** Elastic-net relaxes the standard logistic regression assumption that all predictors should be included. By shrinking irrelevant coefficients to zero, it trades unbiasedness for lower variance and better out-of-sample performance. Traditional logistic regression diagnostics (Hosmer-Lemeshow, delta-beta) are not directly applicable to penalized models and are not reported.

### 11.4 Residual structure for log-transformed models

For all log-transformed responses, compute **Duan's smearing estimator** for back-transformation:
- *ŷ<sub>original</sub> = exp(ŷ<sub>log</sub>) × (1/n) Σ exp(eᵢ)*
where *eᵢ* are OLS residuals on the log scale.

If residuals are heteroscedastic on the log scale, compute family-specific smearing factors *φ<sub>f</sub>* = (1/n<sub>f</sub>) Σ<sub>i∈family f</sub> exp(eᵢ) and apply them within each family. Compare pooled vs. family-specific back-transformed RMSE.

Report both transformed-scale metrics (RMSE, MAE in log-ms) and back-transformed metrics (in ms) per §9.1.

---

## 12. Stratification and Subgroup Analyses

### 12.1 Capacity mode

`capacity_mode` is included as a dummy variable in all models. Additionally, fit M1 and M2 **separately** for fixed and scaled capacity as a sensitivity analysis. Report whether Δ*R²* differs substantially between modes.

**Within-instance correlation:** Because each instance appears in both capacity modes, the two rows share the same weight/value structure. Cluster-robust standard errors by `instance_id` (default per §11.1) address this. The separate-mode sensitivity analysis breaks this correlation by construction.

### 12.2 Family-specific models

If LOFO performance is highly heterogeneous across families (e.g., *R²* > 0.9 on Uncorrelated but < 0.5 on Inverse Correlated), fit separate M1/M2 per family and report family-level Δ*R²*. This is **exploratory** — the primary analysis pools across families.

### 12.3 B&B incomplete-run sensitivity

For B&B models, run the primary analysis (M1 vs M2 for `log_time_millis` and `log_nodes_explored`) twice:
1. **Full sample** (6,000 rows, including 197 incomplete runs)
2. **Complete-only** (5,803 rows, excluding `optimal=false`)

If results differ materially (Δ*R²* changes by > 0.05), report both and discuss censoring bias. Note that neither analysis is fully unbiased: the full sample includes right-censored times (actual time at 50M nodes, not time-to-completion), while the complete-only sample excludes the hardest instances.

---

## 13. Implementation Plan

### 13.1 Software

- **Language:** Python 3.11+ (consistent with existing codebase)
- **Primary packages:**
  - `statsmodels` (OLS, VIF, diagnostics, cluster-robust SEs, linear hypothesis tests)
  - `scikit-learn` (LOFO CV, permutation importance, metrics, cross-validation utilities)
  - `scipy` (transforms, statistical tests, optimization)
- **Bounded-response models:**
  - `statsmodels` GLM with `family=Binomial()` and `link=Logit()` for fractional logit (use `cov_type='HC3'` for robust SEs)
- **Elastic-net logistic:**
  - `scikit-learn` `LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5)` with `C` selected via `GridSearchCV`
- **Supplementary:**
  - `pandas` (data wrangling)
  - `numpy` (computation)
  - `matplotlib`/`seaborn` (diagnostic plots)
- **Reproducibility:** A `requirements.txt` file with pinned versions (major.minor.patch) is produced alongside the pipeline.

### 13.2 Pipeline structure

```
Phase_3_2_Modeling/
├── 1_prepare_data.py        # Load canonical dataset; compute Greedy optimality_gap
│                            #   via DP join; apply exclusions, transforms, encoding;
│                            #   VIF pre-filtering; per-algorithm correlation verification;
│                            #   DP compositional check; split scaffolds
├── 2_fit_models.py          # Fit M1 and M2 for each (algorithm, response) pair;
│                            #   LOFO CV; 5-fold CV; elastic-net λ tuning (nested CV);
│                            #   compute performance metrics per §9
├── 3_feature_importance.py  # Standardized β (OLS/fractional logit);
│                            #   elastic-net nonzero coefficients;
│                            #   permutation importance (20 repeats);
│                            #   Δ-R² partitioning (top-10 by perm importance)
├── 4_diagnostics.py         # Diagnostic plots and statistical tests per §11;
│                            #   per-algorithm correlation verification;
│                            #   smearing factor computation
├── 5_summarize.py           # Aggregate results; BH adjustment; produce LaTeX
│                            #   tables and summary report
└── output/                  # Metrics, tables, diagnostic figures per model
```

### 13.3 Algorithm–response model count

| Algorithm | Model Family | Responses | Total (M1+M2) | LOFO × CV passes |
|---|---|---|---|---|
| Greedy | OLS | 1 (`log_time`) | 2 | 2 × 5 = 10 |
| Greedy | Fractional logit | 1 (`optimality_gap`) | 2 | 2 × 5 = 10 |
| DP | OLS | 2 (`log_time`, `log_memory`) | 4 | 4 × 5 = 20 |
| DP | Fractional logit | 1 (`fill_rate`) | 2 | 2 × 5 = 10 |
| B&B | OLS | 2 (`log_time`, `log_nodes`) | 4 | 4 × 5 = 20 |
| B&B | Elastic-net logistic | 1 (`optimal`) | 2 | 2 × 5 = 10 (plus internal CV for λ) |
| B&B | Two-part hurdle | 1 (`solution_gap`) | 2 | 2 × 5 = 10 |
| **Total** | | **9 responses** | **18** | **18 × 5 = 90 evaluation passes** |

Each evaluation pass includes fitting M1 and M2 on the training set and scoring on the held-out fold. Elastic-net models additionally perform internal 5-fold CV for λ tuning within each LOFO training set (nested CV).

### 13.4 Seed reproducibility

All random processes (CV splits, permutation shuffles, bootstrap resampling, train-test splitting for elastic-net internal CV) use `numpy.random.default_rng(42)`.

---

## 14. Direct Mapping to RQ3

| RQ3 Component | Analysis | Primary Evidence |
|---|---|---|
| "To what extent do algorithm-specific internal execution metrics provide additional explanatory power beyond instance characteristics" | Δ*R²<sub>adj</sub>* (M2 − M1) per algorithm–response pair; BH-adjusted for 4 confirmatory models | §7.3 (incremental test), §9.3 (inference metrics), §10.5 (reporting hierarchy) |
| "for modeling runtime" | Response: `log_time_millis` for all three algorithms (all confirmatory) | §2.1, §7.1, §7.2 |
| "and solution quality" | Responses: `optimality_gap` (Greedy, confirmatory), `optimal` (B&B, exploratory), `solution_gap` (B&B, supplementary) | §2.1, §2.2, §7.2 |
| "which execution metrics are most influential for each algorithm" | Standardized β ranking (OLS/fractional logit), nonzero coefficients (elastic-net), permutation importance, Δ-R² partitioning | §10.1–10.5 |
| "across diverse knapsack instance families" | LOFO CV by family (§8.1); family-stratified results (§12.2); per-family R² matrix | §8.1, §12.2, §15.3 |

---

## 15. Reporting Template

### 15.1 Per-algorithm primary table

For each algorithm, a LaTeX table:

| Response | Model | *R²* / Pseudo-*R²* (LOFO) | RMSE / Brier (LOFO) | Δ*R²<sub>adj</sub>* | Cohen's *f²* | BH adj. *p* |
|---|---|---|---|---|---|---|
| `log_time` | M1 (instance only) | 0.XX | X.XX | — | — | — |
| `log_time` | M2 (full) | 0.XX | X.XX | +0.XX | X.XX | <0.05 |
| `optimality_gap` | M1 | 0.XX | X.XX | — | — | — |
| `optimality_gap` | M2 | 0.XX | X.XX | +0.XX | X.XX | <0.05 |

Confirmatory models are flagged with (C). Exploratory with (E). Supplementary with (S). BH-adjusted q-values are shown for confirmatory models; unadjusted p-values for exploratory.

### 15.2 Feature importance table

Top-5 standardized β (or nonzero elastic-net coefficients) with 95% CI per algorithm–response pair for execution metrics. Separate panels for instance characteristics and execution metrics.

### 15.3 Family-level heterogeneity

LOFO per-family *R²* matrix: rows = family held-out, columns = response × model. Fold-level values listed, not just the mean. This allows readers to assess variability across families.

### 15.4 Elastic-net summary (B&B `optimal`)

- λ path plot for each LOFO fold
- Number of nonzero coefficients at optimal λ
- Coefficient trace plot for top-10 metrics
- Per-family Brier and AUC (where computable)

### 15.5 Diagnostics appendix

Critical diagnostic plots (residual-vs-fitted, Q-Q with envelope, Cook's distance, VIF, calibration curves) for each model, in a supplementary PDF.

---

## 16. Limitations and Threats to Validity

### 16.1 Acknowledged in original design (verified)

1. **Censored B&B runs (3.28%):** 197 incomplete runs may bias runtime models toward underestimation at large *n*. Sensitivity analysis (§12.3) quantifies this.
2. **Single algorithm per row:** Execution metrics from different algorithms are never jointly observed. Cross-algorithm comparison of metric importance is descriptive, not causal.
3. **Greedy measurement noise:** At small *n* (20–50), Greedy runtime is on the order of microseconds. JVM warmup and timer resolution may introduce non-ignorable measurement error. Log-transform mitigates but does not eliminate this.
4. **Coarse capacity modes:** Only two levels (fixed W=1000, scaled W=0.5·Σw). The design does not allow modeling performance as a continuous function of capacity W.
5. **Confounding of *n* and metric magnitudes:** Many execution metrics scale with *n*. Including `n` and `log(n)` as covariates may absorb variance that could otherwise be attributed to execution metrics, producing conservative Δ*R²* estimates. This is a feature for RQ3 (testing unique contribution beyond instance characteristics).
6. **Generalizability:** Results are specific to Pisinger instance families, the three algorithms, and the two capacity regimes tested. Extrapolation to other instance distributions, algorithm variants, or capacity ranges is not claimed.

### 16.2 Additional limitations (new)

7. **DP memory model exclusions (§4.6):** `cells_allocated`, `nonzero_value_states`, and `zero_value_states` are excluded from the DP `log_memory_mb` M2 to prevent circularity. This makes the RQ3 test for this model conservative — the most powerful predictors of DP memory are structurally removed. A null result (ΔR² ≈ 0) does not necessarily imply execution metrics are uninformative; it only implies that metrics unrelated to table size do not predict memory.
8. **B&B `optimal` model limited by event count (§7.5):** With 197 events, even elastic-net regularization cannot fully compensate for the low information content. The binary model is designated exploratory; conclusions about metric importance for B&B completeness should be considered preliminary.
9. **B&B `log_nodes_explored` model limited by exclusions (§4.6):** `nodes_generated` and `internal_nodes` are excluded, removing the most obvious predictors. The remaining metrics may provide limited additional explanatory power over instance characteristics. This model is supplementary only.
10. **LOFO variance (§8.1):** The cross-validated performance estimate is based on only 5 folds. Fold-level R² values show substantial heterogeneity across families; the mean across folds has a wide confidence interval. Readers should interpret the mean with caution and examine per-family results.
11. **Within-instance correlation (§11.1):** Each instance appears in two capacity modes. Cluster-robust SEs by `instance_id` address this for inference, but the point estimates are pooled across the two modes. If the relationship between predictors and response differs by capacity mode (interaction), the pooled estimate represents an average effect that may not hold for either mode individually. Separate-mode analyses (§12.1) test this.
12. **Multiple comparison scope (§9.3):** The BH adjustment covers only the 4 confirmatory model comparisons. The exploratory and supplementary analyses involve additional comparisons (elevated to 23 when including family-level breakdowns, capacity-mode stratification, and multiple importance metrics). Results in these categories should be interpreted as descriptive.

---

## 17. Approval Checkpoint

Before any implementation:
- [x] Design reviewed and approved against independent audit findings
- [x] Response variable definitions confirmed: `solution_value` removed as response; `optimality_gap` uses fractional logit; DP memory excludes circular predictors; B&B binary uses elastic-net
- [x] Model-specific exclusion list (§4.6) verified against near-circularity concerns
- [x] Model hierarchy (M1 → M2) per-model predictor tables (§7.2) confirmed consistent
- [x] LOFO CV design validated against family structure; zero-event handling specified
- [x] Software stack and pipeline structure approved; `requirements.txt` to be generated
- [x] All Phase 3.2 Design Audit findings resolved (see change log)

After approval, proceed to `Phase_3_2_Modeling/1_prepare_data.py`.

---

## Appendix: Change Log (Original → Revised)

| Section | Change | Audit Finding Addressed |
|---|---|---|
| §1 | Added confirmatory vs exploratory model designations with multiplicity control statement | Audit T1 (multiple comparisons) |
| §2.1 | Removed `optimality_gap_sqrt`; replaced with `optimality_gap` (fractional). Added note that `solution_value` is NOT a response. Added B&B `solution_gap` supplementary response. Added `fill_rate` as DP supplementary | Audit M2 (solution_value ambiguity), Audit M3 (OLS on bounded response) |
| §2.2 | Replaced `optimality_gap_sqrt` with fractional logit rationale. Added note on mass-at-zero (1,200 Inverse Correlated rows = 0). Added `solution_gap` hurdle model justification. Added explicit DP memory exclusion rationale | Audit M1 (DP memory circularity), Audit M3 (bounded response) |
| §2.3 | Replaced sqrt(gap) with fractional logit. Added `fill_rate` and `solution_gap` entries | Audit M3 |
| §3.2 | Added model-specific exclusion notes (nodes_generated/internal_nodes for log_nodes; bound metrics for all B&B; cells_allocated etc for DP memory) | Audit m1 (B&B near-circularity), Audit M2 (solution_value role) |
| §3.3 | New subsection: per-algorithm correlation verification | Audit d5 (per-algorithm correlations) |
| §3.4 | New subsection: DP compositional check | Audit d6 (DP metric composition) |
| §4.6 | New subsection: model-specific structural exclusions | Audit M1, Audit m1 |
| §5.2 | Changed "Fisher z-transform" to "Arctanh" with explanation. Added clip-to-±0.9999 edge case | Audit §2.2 (Fisher z issue) |
| §5.3 | Changed `n` from "consider log(n)" to default include both `n` and `log(n)` with rationale | Audit d2 (n nonlinearity) |
| §6.1 | Block 4: removed "solution_value is the response" statement. Added structural exclusion of bound columns from all B&B models with explanation. Clarified Block 2 per-algorithm verification | Audit M2 |
| §6.3 | Block 4: changed to "solution_value is not a response." Retained `bound_variance`, `mean_bound_gap`, `bound_gap_variance` (not in Block 4). All models clarified | Audit M2 |
| §7.1 | Added `log(n)` to model formula (default, not contingency) | Audit d2 |
| §7.2 | New comprehensive per-model specification table showing every response, its distribution/link, M1 predictors, M2 additional predictors, model-specific exclusions, and status | Audit M1, M2, M3, M4, m1 consolidated |
| §7.4 | New subsection: fractional logit rationale with comparison table vs beta regression vs OLS | Audit M3 |
| §7.5 | New subsection: elastic-net logistic rationale with comparison vs alternatives | Audit M4 |
| §7.6 | Updated incremental test section: added fractional logit QLR test, elastic-net Δ(AUC) with bootstrap CI. Note on Cohen's f² caveat | Audit M4, d9 |
| §8.1 | Added variance consideration paragraph with formula for CI half-width. Fold-level values to be reported | Audit m2 (LOFO variance) |
| §8.3 | Added explicit zero-event handling for B&B logistic: Brier score primary when AUC undefined. Record which families have zero events | Audit m3 |
| §8.4 | New subsection: elastic-net λ selection (nested CV, 1-SE rule) | Audit M4 |
| §9.1 | Back-transformed RMSE: added Duan's smearing factor φ to formula. Added note on family-specific smearing under heteroscedasticity | Audit m6 (back-transform formula) |
| §9.3 | Multiplicity control section: BH adjustment for 4 confirmatory models. Described reporting for exploratory and supplementary | Audit d1 |
| §9.4 | New: elastic-net specific metrics (nonzero count, λ path, coefficient trace) | Audit M4 |
| §10.3 | Changed from LMG (infeasible) to Δ-R² partitioning restricted to top-10 by permutation importance. Added LMG infeasibility explanation | Audit d4 |
| §10.5 | Added cross-algorithm comparison note (importance not comparable across algorithms) | Audit d7 |
| §11.1 | Independence: cluster-robust SEs by `instance_id` are now the default. Durbin-Watson note added ("not meaningful without natural ordering"). Normality: prioritize visual diagnostics over formal tests at n=6000 | Audit m5, Audit d3 |
| §11.2 | New: fractional logit diagnostics (link test, boundary sensitivity, robust SE comparison) | Audit M3 |
| §11.3 | New: elastic-net diagnostics (separation, calibration, λ stability). Note that Hosmer-Lemeshow not applicable | Audit M4 |
| §11.4 | Added family-specific smearing under heteroscedasticity | Audit m6 |
| §12.1 | Added within-instance correlation note. Added cluster-robust SE reference | Audit d10 |
| §13.1 | Added `requirements.txt` mention. Added specific solver for elastic-net (`saga`) | Audit d8 |
| §13.3 | Updated model count table to include all 9 responses (was 7) | §7.2 changes |
| §13.4 | Added elastic-net determinism note | Audit M4 |
| §14 | Updated RQ3 mapping to reflect new response variables and designations | Throughout |
| §15 | Updated reporting templates: BH adjustment column, confirmatory/exploratory flags, fold-level values, elastic-net summary section | Audit m2, d1 |
| §16 | Added 6 new limitations (7–12) covering: exclusions, event count, supplementary model limits, LOFO variance, within-instance correlation, multiplicity scope | Several audit findings |

---

## Design Readiness Statement

This revised design addresses every finding from the independent Phase 3.2 Design Audit (`governance/PHASE_3_2_AUDIT.md`):

| Audit Category | Findings | Resolution |
|---|---|---|
| Major Issues (M1–M4) | 4 blocking issues | All resolved: DP memory circularity (M1), solution_value ambiguity (M2), OLS on bounded response (M3), B&B logistic EPV (M4) |
| Minor Issues (m1–m6) | 6 non-blocking issues | All resolved: B&B near-circularity (m1), LOFO variance (m2), zero-event AUC (m3), Fisher z edge case (m4), cluster-robust SEs default (m5), back-transform formula (m6) |
| Documentation gaps (d1–d10) | 10 recommendations | All addressed: multiplicity control (d1), log(n) default (d2), normality caveat (d3), LMG infeasibility (d4), per-algorithm correlations (d5), DP composition check (d6), cross-algorithm comparison note (d7), requirements.txt (d8), bootstrap method (d9), within-instance correlation (d10) |

The design is now ready for a new independent audit before implementation begins.
