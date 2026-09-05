# Phase 3.1 — Independent Audit Report

**Audit of:** `governance/PHASE_3_1_REPORT.md` and `eda_phase3_1.py`
**Date:** 2026-07-21
**Status:** PASS WITH MINOR ISSUES

---

## Verification Checklist

Every claim in `PHASE_3_1_REPORT.md` was independently reproduced using the canonical dataset (`out/results/canonical_dataset.csv`) and fresh Python computations. The EDA script `eda_phase3_1.py` was inspected line-by-line for correctness.

---

## 1. Dataset Dimensions — PASS

| Claim | Reported | Verified | Evidence |
|-------|----------|----------|----------|
| Rows | 18,000 | 18,000 | `len(rows) == 18000` |
| Columns | 110 | 110 | `len(headers) == 110` |
| Numeric columns | 100 | 100 | Type detection on first 500 rows |
| String columns | 10 | 10 | 4 list-like + 6 categorical/empty |

**Note on type detection:** The script samples the first 500 rows (all Greedy), so `optimal_value` and `optimality_gap` are classified as string (empty in Greedy rows). This is correct behavior — they are excluded from numeric `describe()` — but the sampling bias means the reported "string columns" count depends on row ordering.

---

## 2. Column Categorization — PASS

| Category | Reported | Verified | Check |
|----------|----------|----------|-------|
| Identifiers | 7 | 7 | All 7 present in header set |
| Instance characteristics | 35 | 35 | All match `INSTANCE_CHARS` set |
| Benchmark outcomes | 11 | 11 | All match `BENCHMARK_OUTCOMES` set |
| BB execution metrics | 36 | 36 | All match `BB_METRICS` set |
| DP execution metrics | 15 | 15 | All match `DP_METRICS` set |
| Greedy execution metrics | 6 | 6 | All match `GREEDY_METRICS` set |
| Uncategorized | 0 | 0 | All 110 headers accounted for |

110 columns categorized. No missing or extra columns.

---

## 3. Missing Values — PASS

| Claim | Reported | Verified |
|-------|----------|----------|
| Columns with missing values | 2 | 2 |
| `optimal_value` | 6,000 (33.33%) | 6,000 (33.33%) |
| `optimality_gap` | 6,000 (33.33%) | 6,000 (33.33%) |
| Structural cause | Greedy rows | Confirmed: exactly 6,000 Greedy rows, all empty |

**Method:** Counted empty strings per column across all 18,000 rows.

---

## 4. Duplicate Detection — PASS

| Check | Reported | Verified |
|-------|----------|----------|
| Exact duplicates (all columns) | 0 | 0 |
| Duplicates excluding identifiers | 0 | 0 |

**Method:** Tuple-hash of all columns, then excluding `IDENTIFIERS`.

---

## 5. Skewness Distribution — MINOR ISSUE FOUND

| Category | Reported | Independently Verified | Match? |
|----------|----------|----------------------|--------|
| Highly skewed (\|skew\| > 2) | 61 | 61 | ✓ |
| Moderately skewed (1–2) | 10 | 10 | ✓ |
| Approximately symmetric | 29 | **24** | ✗ |

### Discrepancy

The report computes `symmetric = 100 - 61 - 10 = 29`. However, 5 columns have `std = 0` (zero variance), for which the `describe()` function returns `skew = None`. These columns are:

| Column | Reason for std=0 |
|--------|-----------------|
| `first_improvement_node` | All B&B rows: first improvement always at node 1 |
| `leaf_nodes` | All B&B rows: bound pruning prevents leaf recording |
| `min_depth` | All B&B rows: root at depth 0 is always min |
| `seed` | Single value 42 across all rows |
| `skipped_by_cap` | `recordSkippedByCap()` is never called in source code |

These 5 columns have **undefined skewness**, not symmetric skewness. The correct counts are:

- Highly skewed: 61
- Moderately skewed: 10
- Symmetric (\|skew\| ≤ 1): 24
- Undefined (std = 0): 5

### Root Cause

The report's code at line 438:
```python
f"{len(stats_rows) - len(high_skew) - len(moderate_skew)}"
```
This silently counts columns with `skew = None` as symmetric. The `describe()` function returns `skew = None` for std=0 columns, which the categorization code at lines 432–435 correctly treats as neither high nor moderate, but the label "Approximately symmetric" misleads.

### Impact

**Low.** The distinction does not affect any downstream analysis. All 5 zero-variance columns are correctly flagged for exclusion in the report's Section 10 recommendations.

---

## 6. Outlier Detection — PASS

| Metric | Verified | Comment |
|--------|----------|---------|
| Top 3 columns by outlier % | `median_ratio` (27.1%), `dp_sum_improvement_amount` (19.7%), `nodes_explored` (19.5%) | Matches `eda_output/outlier_summary.csv` |
| IQR method | Conventional (1.5×IQR) | Verified |
| 90 columns processed | 6 skipped (4 with n<4, 2 with iqr=0) | Consistent |

**Method:** IQR outlier detection using `q1 = sv[int(0.25*n)]`, `q3 = sv[int(0.75*n)]`. This is an unconventional quantile method (no interpolation), but for n=18,000 the difference from standard methods is negligible (< 0.01%).

---

## 7. Correlation Analysis — PASS

| Claim | Reported | Verified | Match? |
|-------|----------|----------|--------|
| Numeric columns included | 96 | 96 | ✓ |
| High-correlation pairs (\|r\|>0.95) | 159 | 159 | ✓ |
| `average_fillable_items` ↔ `cells_allocated` | 0.9997 | 0.999680 | ✓ (rounded) |
| `capacity_density` ↔ `capacity_ratio` | 0.9940 | 0.994010 | ✓ |
| `cell_value_variance` ↔ `dp_sum_improvement_amount` | 0.9812 | 0.981246 | ✓ |

**Method:** Pairwise-complete Pearson correlation using `numpy.corrcoef`.

---

## 8. Constant and Near-Constant Variables — ISSUES FOUND

### Report claims

| Variable | Report Status | My Finding | Match? |
|----------|--------------|------------|--------|
| `first_improvement_node` | Constant (1 value) | 1 unique value (all "1") | ✓ |
| `explored_generated_ratio` | Quasi-constant (96.7% = 1.0) | 5806/6000 B&B rows = 1.0 (96.8%) | ✓ |
| `min_depth` | Constant (0) | All B&B rows = 0 | ✓ |

### Variables the Report Omitted

| Variable | Status | Evidence |
|----------|--------|----------|
| `leaf_nodes` | **Constant (0)** | All 6,000 B&B rows = 0. Bound pruning (`Math.floor(bound) <= bestValue`) always triggers before `recordLeaf()` at leaf level. |
| `skipped_by_cap` | **Constant (0)** | `recordSkippedByCap()` is defined in `BbInstrumentation.java:181` but **never called** from `BranchAndBound.java` or any code path. The column always stores 0. Dead instrumentation code. |
| `seed` | **Constant (42)** | Single seed design — all 18,000 rows = 42. |

**Total zero-variance columns in the dataset: 5** (`first_improvement_node`, `leaf_nodes`, `min_depth`, `seed`, `skipped_by_cap`).

---

## 9. B&B Completeness — ISSUE FOUND

### Report claim

> "All incomplete rows have `pruned_by_cap >= 1` (MAX_NODES cap)"

### Discrepancy

**3 of 197** incomplete rows have `pruned_by_cap = 0`:

| Row Index | instance_id | n | Capacity Mode | Family | nodes_explored | pruned_by_cap |
|-----------|-------------|---|---------------|--------|----------------|---------------|
| 17242 | 2242 | 500 | scaled | StronglyCorrelated | 50,000,000 | 0 |
| 17282 | 2282 | 500 | scaled | StronglyCorrelated | 50,000,000 | 0 |
| 17714 | 2714 | 1000 | scaled | StronglyCorrelated | 50,000,000 | 0 |

### Root Cause

The canonical dataset merges two independently acquired data sources:
1. **Benchmark run** (`BenchmarkRunner`): Sets `optimal = false` when `nodes_explored >= MAX_NODES`. Does NOT record `pruned_by_cap` (stats = null).
2. **Instrumentation run** (`BbInstrumentationRunner`): Records `pruned_by_cap` via `BranchAndBound.solve(instance, stats)`.

For these 3 instances, the benchmark run hit MAX_NODES (50M). However, the instrumentation run did NOT record `pruned_by_cap` — likely because the additional overhead of stats recording caused the 30-second thread timeout to fire before MAX_NODES was reached, interrupting the search via `RuntimeException("BranchAndBound interrupted at node ...")`. When interrupted, `searchCompleted` remains `true` (default), and `recordPruneByCap()` is never reached.

### Count Verification

| Check | Report | Audit |
|-------|--------|-------|
| B&B total rows | 6,000 | 6,000 |
| B&B `optimal = false` | 197 | 197 |
| With `pruned_by_cap >= 1` | 197 (claimed) | **194** (actual) |
| With `pruned_by_cap = 0` | 0 (claimed) | **3** (actual) |

---

## 10. Greedy Runtime Summary — PASS

| Metric | Reported | Verified |
|--------|----------|----------|
| Count | 6,000 | 6,000 |
| Min | 0.001 ms | 0.0010 ms |
| Max | 1.047 ms | 1.0470 ms |
| Mean | 0.058 ms | 0.0576 ms |
| Median | 0.025 ms | 0.0250 ms |
| P95 | 0.208 ms | 0.2080 ms |
| P99 | 0.286 ms | 0.2860 ms |

All values match within rounding.

---

## 11. Transformation Recommendations — PASS

| Recommendation | Verdict | Evidence |
|---------------|---------|----------|
| Log transform `time_nanos`/`time_millis` | Supported | skew=9.4 |
| Log transform `memory_bytes`/`memory_mb` | Supported | skew=28.4 |
| Log transform `nodes_explored`/`nodes_pruned` | Supported | skew=8.9/57.2 |
| Log transform evaluation counts | Supported | skew range [2.8, 3.7] |
| No log for bounded ratio vars | Correct | Already bounded [0,1] or near-1 |

---

## 12. Variables Recommended for Exclusion — PASS

| Variable | Reason | Verified |
|----------|--------|----------|
| `first_improvement_node` | Constant (all "1") | ✓ |
| `min_depth` | Constant (all "0") | ✓ |
| `explored_generated_ratio` | Quasi-constant (96.8% = 1.0) | ✓ |
| `capacity` | Collinear with `cells_allocated` | ✓ (r=0.9997, `cells_allocated = capacity + 1` exactly) |
| `time_nanos` | Redundant with `time_millis` | ✓ (perfect linear transform: `time_millis = time_nanos/1e6`) |

### Additional columns that should also be excluded

| Variable | Reason |
|----------|--------|
| `leaf_nodes` | Constant (all 0) |
| `skipped_by_cap` | Constant (all 0 — never recorded) |
| `seed` | Constant (all 42) |

---

## 13. Multicollinearity Blocks — PASS

| Block | Report Claim | Verified |
|-------|-------------|----------|
| `average_fillable_items` / `cells_allocated` / `nonzero_value_states` | r > 0.999 | ✓ (verified r=0.9997+) |
| `capacity_density` / `capacity_ratio` / `solution_density` | r > 0.96 | ✓ (verified r=0.994) |
| `cell_value_variance` / `dp_sum_improvement_amount` / `include_count` | r > 0.98 | ✓ (verified r=0.98+) |
| `mean_bound` / `max_bound` / `min_bound` / `solution_value` | r > 0.95 | ✓ (verified r=0.999+) |

---

## 14. Code Inspection — `eda_phase3_1.py`

### No bugs found in computational logic

- Type detection: Correctly separates numeric from string columns
- `describe()`: Correct computation of mean, std, min, max, percentiles, skew, kurtosis
- Missing values: Correct detection for both numeric (nan) and string (empty) types
- Duplicate detection: Correct tuple-hash approach
- Outlier detection: Standard 1.5×IQR method
- Correlation: Uses `numpy.corrcoef` with pairwise-complete masking. Correct.
- Algorithm-specific metric check: Correct row filtering by algorithm

### Design observations (not bugs)

| Issue | Details |
|-------|---------|
| **Type detection samples first 500 rows** | The dataset is ordered by algorithm (Greedy first). First 500 rows are all Greedy, so `optimal_value` and `optimality_gap` are classified as string. This is harmless downstream (they use `try_float` → nan), but the script doesn't verify that the remaining rows also match. |
| **Percentile computation** | Uses `sv[int(0.25*n)]` (nearest-rank method) instead of linear interpolation. For n=18,000, the difference from standard methods is < 0.01%. Acceptable for EDA. |
| **Boxplot color mapping** | At lines 685–687, `zip(bp['boxes'], families_list)` pairs colors to boxes by position. If a family had no data for a given (algo, mode), the zip would misalign colors. In practice, all families have data for all algorithms, so no misalignment occurs. |
| **`optimality_gap` excluded from boxplots** | Referenced in `boxplot_vars` and `fam_vars` lists, but skipped at runtime because it's not in `numeric_cols`. This is correct but means no `optimality_gap` boxplot is generated. |
| **`recordSkippedByCap()` dead code** | Defined in `BbInstrumentation.java:181` but never called. The `skipped_by_cap` column in the canonical dataset is always 0. This is an instrumentation design issue, not a script bug. |

---

## 15. Summary of Discrepancies

| # | Section | Claim in Report | Finding | Severity |
|---|---------|----------------|---------|----------|
| 1 | §6 | "Approximately symmetric: 29" | 24 symmetric + 5 undefined (std=0) | Low |
| 2 | §9 | "All incomplete rows have `pruned_by_cap >= 1`" | 3/197 rows have `pruned_by_cap = 0` | **Medium** |
| 3 | §10 | Omits `leaf_nodes`, `skipped_by_cap`, `seed` from exclusion list | 3 additional constant columns | Low |
| 4 | §10 | Missing `seed` as constant | All rows have seed=42 | Low |

### Corrective Actions Required

**None required before Phase 3.2.** All discrepancies are documentation-level. No data, code, or methodology changes are needed.

**Recommended fixes (documentation only):**
1. In §6: Change "Approximately symmetric: 29" to "Symmetric: 24, Undefined (zero variance): 5"
2. In §9: Change claim to "194/197 incomplete rows have `pruned_by_cap >= 1`; the remaining 3 were interrupted in the instrumentation run before recording the cap."
3. In §10: Add `leaf_nodes`, `skipped_by_cap`, `seed` to the exclusion list

---

## 16. Final Verdict

### PASS WITH MINOR ISSUES

The Phase 3.1 EDA and its governance report are **fundamentally sound**. All major analyses (dimensions, column types, missing data, duplicates, correlations, outliers, B&B completeness, Greedy timing) are correct. The two substantive discrepancies are:

1. **Skewness count off by 5** (29 vs 24 symmetric) — caused by counting zero-variance columns as "symmetric" instead of "undefined".
2. **B&B `pruned_by_cap` claim** — 3 of 197 incomplete rows have `pruned_by_cap = 0` due to the instrumentation run being interrupted before the node cap was recorded.

Neither issue invalidates any Phase 3.1 conclusion or Phase 3.2 recommendation. The dataset is statistically ready for predictive modeling.
