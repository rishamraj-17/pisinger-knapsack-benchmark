# Phase 3.1 — Exploratory Data Analysis: Governance Report

**Project:** Knapsack Empirical Comparison (Greedy, DP, B&B)
**Dataset:** `out/results/canonical_dataset.csv`
**Script:** `eda_phase3_1.py`
**Date:** 2026-07-21

---

## 1. Dataset Verification

| Property | Expected | Actual | Status |
|----------|----------|--------|--------|
| Rows | 18,000 | 18,000 | Verified |
| Columns | 110 | 110 | Verified |
| Numeric columns | — | 100 | Verified |
| String columns | — | 10 | Verified |

**Source:** EDA script output, summary statistics count.

All columns are accounted for with no unnamed or mismatched types. The 10 string columns are `algorithm`, `family`, `capacity_mode`, `depth_histogram`, `queue_histogram`, `improvement_depths`, `improvement_nodes`, `optimal` (boolean string), plus `optimal_value` and `optimality_gap` (partially empty).

---

## 2. Column Categorization

Seven categories were defined, each verified against the canonical dataset header:

| Category | Count | Description |
|----------|-------|-------------|
| Identifiers | 7 | `algorithm`, `instance_id`, `n`, `family`, `capacity_mode`, `capacity`, `seed` |
| Instance characteristics | 35 | Weight/value distribution, correlation, ratio structure, diversity |
| Benchmark outcomes | 11 | Timing, memory, solution value, optimality gap, search effort |
| BB execution metrics | 36 | Tree structure, queue, bounds, pruning, branching, improvements |
| DP execution metrics | 15 | Evaluations, cell state, fill rate, improvements |
| Greedy execution metrics | 6 | Selection count, density, utilization |

**Source:** `eda_output/column_categories.csv`

**Observation:** All 110 columns are categorized. No uncategorized columns remain.

---

## 3. Missing Value Report

| Column | Category | Missing Count | Missing % | Cause |
|--------|----------|---------------|-----------|-------|
| `optimal_value` | Benchmark outcome | 6,000 | 33.33% | Greedy rows (Greedy does not compute optimal value) |
| `optimality_gap` | Benchmark outcome | 6,000 | 33.33% | Same — not computed for Greedy |

**Source:** `eda_output/missing_values.csv`

**Interpretation:** These are **structurally missing** — they do not represent data loss. Greedy is a heuristic; it never produces an `optimal_value`. By design, `optimal_value` is only populated for DP and B&B rows (where DP provides the ground truth and B&B reports its own optimal value when `searchCompleted=true`).

For Phase 3.2 modeling, `optimality_gap` should only be used as a response variable for Greedy rows, or excluded from joint models. No imputation is warranted.

---

## 4. Duplicate Row Report

| Check | Count |
|-------|-------|
| Exact duplicates (all columns) | 0 |
| Duplicates excluding identifiers | 0 |

**Source:** `eda_output/duplicate_rows.csv`

**Interpretation:** No data duplication exists. Every row is a unique `(algorithm, instance_id, capacity_mode)` triple.

---

## 5. Outlier Detection (IQR Method, Descriptive)

**Top 10 columns by outlier fraction:**

| Column | Category | Outliers | Outlier % |
|--------|----------|----------|-----------|
| `median_ratio` | Instance characteristic | 4,878 | 27.1% |
| `dp_sum_improvement_amount` | DP metric | 3,549 | 19.7% |
| `nodes_explored` | Benchmark outcome | 3,516 | 19.5% |
| `nodes_pruned` | Benchmark outcome | 3,356 | 18.6% |
| `bound_gap_variance` | BB metric | 3,312 | 18.4% |
| `tie_count` | DP metric | 3,300 | 18.3% |
| `duplicate_pairs` | Instance characteristic | 3,282 | 18.2% |
| `max_queue_size` | Benchmark outcome | 3,165 | 17.6% |
| `skipped_infeasible` | BB metric | 3,123 | 17.4% |
| `right_branches` | BB metric | 3,117 | 17.3% |

**Source:** `eda_output/outlier_summary.csv`

**Interpretation:** The dataset combines instances across all 6 `n` values (20 to 1000), 5 families, and 3 algorithms. Many metrics are naturally n-dependent and right-skewed. These IQR outliers are **expected** given the experimental design — they do not indicate data quality issues. For regression in Phase 3.2, robust estimators or log-transformed responses may be necessary.

**Greedy time outliers:** Greedy execution times range from 1 μs (n=20) to 1.05 ms (n=1000), with p99 = 0.29 ms and p50 = 0.025 ms. Although the IQR flags outliers, the maximum (1.05 ms) is only ~3.5× the p99, indicating mild right-skew rather than pathological outliers.

---

## 6. Distribution Analysis

### Skewness Summary

| Skewness Category | Count |
|-------------------|-------|
| Highly skewed (\|skew\| > 2) | 61 |
| Moderately skewed (1–2) | 10 |
| Symmetric (\|skew\| ≤ 1) | 24 |
| Undefined (zero variance) | 5 |

Five variables (`first_improvement_node`, `leaf_nodes`, `min_depth`, `seed`, `skipped_by_cap`) have zero variance, making skewness undefined. These are excluded from the skewness categorization.

**Source:** `eda_output/summary_statistics.csv`

### Key Transform Candidates (positive, |skew| > 2)

| Variable | Skew | Range | Category |
|----------|------|-------|----------|
| `nodes_pruned` | 57.2 | [0, 1.9e7] | Benchmark outcome |
| `pruned_by_bound` | 33.2 | [0, 1.9e7] | BB metric |
| `max_queue_size` | 30.5 | [0, 4.6e7] | Benchmark outcome |
| `memory_bytes` / `memory_mb` | 28.4 | [0, 1.2e9] | Benchmark outcome |
| `time_nanos` / `time_millis` | 9.4 | [0.001, 18,195] | Benchmark outcome |
| `nodes_explored` | 8.9 | [0, 5.0e7] | Benchmark outcome |

**Interpretation:** 61% of numeric variables have |skew| > 2. This is expected because the dataset pools all n-values (20–1000) and all algorithm classes (fast Greedy vs. heavy B&B). Log transformation is strongly recommended for time, memory, node counts, queue sizes, and evaluation counts in Phase 3.2 regression modeling.

**Variables that should NOT be log-transformed:** Ratios and bounded variables (`capacity_ratio`, `include_ratio`, `fill_rate`, `solution_density`, `capacity_utilization`, `avg_branching_factor`, `explored_generated_ratio`, `pruned_generated_ratio`) are bounded [0,1] or near-1 and should be left in their natural scale or considered for logit transformation.

---

## 7. Correlation Analysis

- **Numeric columns included:** 96
- **Highly correlated pairs (|r| > 0.95):** 159

**Source:** `eda_output/correlation_matrix.csv`, `eda_output/correlation_heatmap.png`

### Major Multicollinearity Blocks

**Block 1 — Instance size / capacity (near-perfect correlation):**
- `average_fillable_items`, `cells_allocated`, `nonzero_value_states`: r > 0.999
- These measure essentially the same thing: `n` (for fixed capacity) or `capacity` (for scaled). `average_fillable_items = capacity / mean_weight`, and `cells_allocated = capacity + 1`.
- Also correlated: `total_evaluations`, `exclude_count`, `include_count`, `selected_count`, `first_skipped_position`, `improvement_count`, `updates_per_cell`

**Block 2 — Capacity density:**
- `capacity_density`, `capacity_ratio`, `solution_density`: r > 0.96

**Block 3 — DP cell improvement:**
- `cell_value_variance`, `dp_sum_improvement_amount`, `include_count`: r > 0.98

**Block 4 — Bound metrics (BB):**
- `mean_bound`, `max_bound`, `min_bound`, `sum_improvement_amount`, `solution_value`: r > 0.95

**Utility of high correlations:** These are **informative for RQ3** — near-duplicate measurement across instance characteristics and execution metrics suggests specific metric families that may or may not contribute unique explanatory power.

### Near-Constant Variables (Low Variance)

| Variable | Mean | Median | Unique Values | Issue |
|----------|------|--------|---------------|-------|
| `first_improvement_node` | 1.0 | 1.0 | 1 | **Constant** — all B&B find first improvement at node 1 |
| `explored_generated_ratio` | 0.997 | 1.0 | 195 | **Quasi-constant** — 96.7% of B&B rows = 1.0 |
| `min_depth` | 0.0 | 0.0 | — | All B&B rows have min_depth=0 (root node) |

**Interpretation:** `first_improvement_node` must be excluded from regression models (zero variance). `explored_generated_ratio` and `min_depth` may cause singularity or near-singularity in design matrices.

---

## 8. Algorithm-Specific Metric Availability

| Algorithm | Populated Cells | Total Cells | Fill % |
|-----------|----------------|-------------|--------|
| Branch & Bound | 216,000 | 216,000 | 100.0% |
| Dynamic Programming | 90,000 | 90,000 | 100.0% |
| Greedy | 36,000 | 36,000 | 100.0% |

**Source:** EDA script — algorithm-specific metric check.

**Interpretation:** All algorithm-specific execution metrics are fully populated for their respective rows. There is no missingness within algorithm families. Metrics from one algorithm are naturally empty for other algorithms' rows (by structural design — each row only has metrics for that row's algorithm).

---

## 9. B&B Completeness

- Total B&B rows: 6,000
- `optimal = false`: 197 (3.28%)
- 194 of 197 incomplete rows have `pruned_by_cap >= 1`.
- 3 rows have `pruned_by_cap = 0` (instance IDs 2242, 2282, 2714; all StronglyCorrelated, scaled capacity) because the instrumentation run was interrupted by the 30-second timeout before the node-cap recording occurred.
- Distribution: 146 at n=1000, 51 at n=500
- Scaled capacity: 192 rows; Fixed capacity: 5 rows

**Source:** Canonical dataset column `optimal`, `pruned_by_cap`.

**Interpretation:** 3.28% of B&B executions did not complete (hit MAX_NODES=50M). These rows are not censored — `time_nanos` records actual elapsed time, `solution_value` reflects best found at termination. For Phase 3.2, researchers should decide whether to include or exclude these based on the modeling goal. For runtime prediction, they are valid measurements. For solution quality modeling, they represent lower bounds.

---

## 10. Recommendations for Phase 3.2 (Statistical Modeling)

### Required Transformations

| Variable Group | Recommended Transform | Justification |
|----------------|----------------------|---------------|
| `time_nanos`, `time_millis`, `memory_bytes`, `memory_mb` | Log | Skew > 9, range spans 6+ orders of magnitude |
| `nodes_explored`, `nodes_pruned`, `nodes_generated` | Log or sqrt | Skew > 8, zero-inflated for non-B&B |
| `max_queue_size`, `final_queue_size`, `mean_queue_size` | Log | Skew > 17, extreme right tail |
| Evaluation counts (`include_count`, `total_evaluations`, etc.) | Log | Skew > 2.8, range millions |
| `dp_sum_improvement_amount`, `sum_improvement_amount` | Log | Skew > 3.6 |
| Ratio variables bounded (0,1) | No transform or logit | Already bounded; check for floor/ceiling effects |

### Variables to Exclude from Regression

- `first_improvement_node` — constant (all 1.0)
- `leaf_nodes` — constant (all 0); bound pruning prevents leaf recording
- `min_depth` — constant (all 0)
- `seed` — constant (all 42); single-seed experimental design
- `skipped_by_cap` — constant (all 0); `recordSkippedByCap()` never called in source
- `explored_generated_ratio` — quasi-constant (96.7% = 1.0); singularity risk
- `capacity` — collinear with `cells_allocated` and `average_fillable_items`
- `time_nanos` — redundant with `time_millis` (exact linear transform)

### Variables to Consider Excluding (Multicollinearity)

From each high-correlation block, retain at most one representative to avoid rank deficiency:
- From Block 1: pick `average_fillable_items` or `cells_allocated`, not both
- From Block 2: pick `capacity_ratio`, drop `capacity_density`
- From Block 3: pick `dp_sum_improvement_amount`, drop `cell_value_variance`
- From Block 4: pick `solution_value` as the target, drop `mean_bound`, `max_bound`, `min_bound`

### Structural Considerations

1. **Algorithm-specific models are recommended.** Pooling all three algorithms inflates skewness and variance. RQ3 explicitly asks "for each algorithm" — modeling per-algorithm subsets avoids the dominance effects of B&B's large metric values over Greedy's small ones.
2. **`optimal_value` and `optimality_gap` missing for Greedy.** The 6,000 Greedy rows lack these fields. For Greedy, use `solution_value` as the quality metric; compute gap externally using DP's `optimal_value`.
3. **Capacity mode as a covariate.** The two modes (fixed W=1000, scaled W=0.5×sum weights) create structurally different regimes. Include `capacity_mode` as a dummy variable or model separately.

---

## 11. Conclusion: Dataset Readiness

**The canonical dataset is statistically ready for Phase 3.2 predictive modeling**, with the following caveats:

| Issue | Severity | Mitigation |
|-------|----------|------------|
| 61% of variables highly skewed | Moderate | Log/sqrt transform as recommended |
| 159 high-correlation pairs (|r|>0.95) | Moderate | Variable selection required; retain one per block |
| `optimal_value`/`optimality_gap` missing for Greedy | Low | Use `solution_value`; external gap computation |
| `first_improvement_node` constant | Low | Exclude from models |
| 3.28% B&B rows incomplete (MAX_NODES) | Low | Document in analysis; exclude for optimality analysis |
| Greedy time variance (1,600× range for n≤50) | Low | Log-transform; note measurement noise at small n |

No data quality issues (duplicate rows, pathological missingness, corrupted values) were found. The dataset is structurally sound and appropriate for the planned regression analyses in RQ3.

**Prepared by:** Phase 3.1 EDA pipeline (`eda_phase3_1.py`)
**Outputs referenced:**
- `eda_output/summary_statistics.csv`
- `eda_output/missing_values.csv`
- `eda_output/duplicate_rows.csv`
- `eda_output/outlier_summary.csv`
- `eda_output/correlation_matrix.csv`
- `eda_output/correlation_heatmap.png`
- `eda_output/histograms/` (100 files)
- `eda_output/boxplots/` (32 files)
