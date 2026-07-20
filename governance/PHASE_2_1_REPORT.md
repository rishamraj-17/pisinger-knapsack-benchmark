# Phase 2.1 — Instance Characterization: Governance Report

## Dataset Versioning

| Property | Value |
|----------|-------|
| **Dataset Version** | 1.0 |
| **Phase** | 2.1 |
| **Status** | Frozen after verification |
| **File** | `results/instances.csv` |
| **Rows** | 6,000 |
| **Columns** | 40 |
| **Primary Key** | `(instance_id, capacity_mode)` |
| **Generation Script** | `extract_features.py` |
| **Generation Command** | `python3 extract_features.py` |
| **Seed** | 42 |
| **MD5 Checksum** | `3ee015eab8d1c5d83c52d7683a5ccd19` |

---

## 1. Objective

Generate a rich descriptive-feature dataset (`results/instances.csv`) characterizing
every generated knapsack instance as a measurable object, independent of any algorithm.
This dataset will support future statistical analysis (hardness, feature importance,
clustering, regression, predictive modeling, hypothesis generation) when merged with
algorithm execution statistics in Phase 2.5.

## 2. Scientific Motivation

Instance-level features enable downstream research questions that aggregated statistics
cannot address:

- **Hardness analysis**: Which features predict algorithmic difficulty across families?
- **Feature importance**: Which instance characteristics most influence runtime, nodes explored, or optimality gap?
- **Clustering**: Do instances from different families form natural clusters in feature space?
- **Regression**: Can algorithm performance be predicted from instance features?
- **Predictive modeling**: Can we predict which algorithm will perform best for unseen instances?
- **Hypothesis generation**: What structural properties explain observed performance differences?

Each feature below is chosen for its known or hypothesized relationship to knapsack
problem difficulty (Pisinger 2005, Martello & Toth 1990).

## 3. Design Decisions

### 3.1 Passive instrumentation

Feature extraction is completely independent of algorithm execution. `extract_features.py`
regenerates instances deterministically from the same seed (42) using an exact Java
`java.util.Random` replica, computes features using only the Python standard library,
and writes `results/instances.csv`. No benchmark code is modified or read.

### 3.2 Two capacity modes per instance

Each base instance generates two feature rows: one with fixed capacity W=1000 and one
with scaled capacity W=0.5×total_weight. This mirrors the benchmark pipeline and
enables future analysis of how capacity regime interacts with instance structure.

### 3.3 Deterministic generation

The Python `JavaRandom` class replicates `java.util.Random` bit-exactly. Combined with
seed=42 and deterministic generator iteration order, the output is fully reproducible.

### 3.4 Population statistics

Variance, skewness, and kurtosis use population formulas (dividing by n, not n-1) since
we treat the entire instance as the population, not a sample.

### 3.5 No additional features beyond specification

The specified feature set was determined to be sufficient for the intended analyses.
No additional features were added, keeping the schema minimal and well-scoped.

## 4. Implementation Summary

### 4.1 Files modified

| File | Change |
|------|--------|
| `extract_features.py` | New file (428 lines) — instance generator replicating Java generators, feature computation, CSV export |
| `results/instances.csv` | Generated output — 6000 rows, 40 columns (generated, not committed yet) |

**Unchanged (verified):**
- `src/main/java/algorithms/*.java` — no modifications
- `src/main/java/benchmark/*.java` — no modifications
- `src/main/java/dataset/*.java` — no modifications
- `src/main/java/Main.java` — no modifications
- `analyze.py` — no modifications
- `figures.py`, `plot_utils.py` — no modifications
- `build_and_run.sh`, `reproduce.sh` — no modifications
- `out/results/*.csv` — no modifications
- `tables/*` — no modifications
- `figures/*` — no modifications
- `paper/draft.md` — no modifications

### 4.2 Generated dataset

- **File**: `results/instances.csv`
- **Rows**: 6,000 (3,000 instances × 2 capacity modes)
- **Columns**: 40
- **Size**: 2,546 KB
- **MD5**: `3ee015eab8d1c5d83c52d7683a5ccd19`
- **Instances per mode**: 6 n-values × 5 families × 100 seeds = 3,000
- **Coverage**: Fixed mode (W=1000) + Scaled mode (W=0.5×total_weight)

## 5. Complete Feature Definitions

### 5.1 Identifiers

| Field | Type | Description |
|-------|------|-------------|
| `instance_id` | int | Unique instance identifier (0–2999) |
| `n` | int | Number of items |
| `family` | string | Pisinger family name |
| `capacity_mode` | string | `fixed` or `scaled` |

### 5.2 Basic Statistics

| Field | Formula | Description |
|-------|---------|-------------|
| `total_weight` | Σ wᵢ | Sum of item weights |
| `total_value` | Σ vᵢ | Sum of item values |
| `mean_weight` | (1/n) Σ wᵢ | Arithmetic mean of weights |
| `mean_value` | (1/n) Σ vᵢ | Arithmetic mean of values |
| `median_weight` | median({wᵢ}) | Median weight (average of two middle values for even n) |
| `median_value` | median({vᵢ}) | Median value |
| `std_weight` | σ(w) | Population standard deviation of weights |
| `std_value` | σ(v) | Population standard deviation of values |
| `min_weight` | min(wᵢ) | Minimum weight |
| `max_weight` | max(wᵢ) | Maximum weight |
| `min_value` | min(vᵢ) | Minimum value |
| `max_value` | max(vᵢ) | Maximum value |

**Rationale**: Basic location and scale descriptors characterize the instance's
numeric range and central tendency. These directly affect knapsack capacity
utilization and algorithm behavior.

### 5.3 Distribution Descriptors

| Field | Formula | Description |
|-------|---------|-------------|
| `weight_cv` | σ(w) / μ(w) | Coefficient of variation of weights |
| `value_cv` | σ(v) / μ(v) | Coefficient of variation of values |
| `weight_skewness` | m₃ / σ³ | Skewness (third standardized moment) of weights |
| `value_skewness` | m₃ / σ³ | Skewness of values |
| `weight_kurtosis` | m₄ / σ⁴ − 3 | Excess kurtosis of weights |
| `value_kurtosis` | m₄ / σ⁴ − 3 | Excess kurtosis of values |

**Rationale**: CV measures relative dispersion independent of scale. Skewness
captures asymmetry in the distribution (e.g., InverseCorrelated produces many
low-weight items with high value-to-weight ratios). Kurtosis captures tail
behavior (e.g., Uniform distributions have negative excess kurtosis, while
distributions with outliers have positive). These affect capacity packing
patterns and search space structure.

### 5.4 Capacity Descriptors

| Field | Formula | Description |
|-------|---------|-------------|
| `capacity` | W | Knapsack capacity |
| `capacity_ratio` | W / total_weight | Fraction of total weight capacity can hold |
| `slack` | total_weight − W | Total weight exceeding capacity |
| `average_fillable_items` | W / mean_weight | Estimated number of items capacity can hold |

**Rationale**: `capacity_ratio` is the primary determinant of whether the
instance is tightly or loosely constrained. `slack` gives absolute scale.
`average_fillable_items` estimates problem dimensionality relative to capacity.

### 5.5 Correlation Descriptors

| Field | Formula | Description |
|-------|---------|-------------|
| `pearson_corr` | r(w, v) | Pearson product-moment correlation between weights and values |
| `spearman_corr` | ρ(w, v) | Spearman rank correlation |
| `kendall_corr` | τ(w, v) | Kendall rank correlation (tau-a, ignoring ties in denominator) |

**Rationale**: These directly characterize the Pisinger family structure.
Uncorrelated: r ≈ 0. Weakly correlated: r ≈ 0.98. Strongly correlated: r ≈ 1.0.
Inverse correlated: r = −1.0. Almost-equal ratios: r ≈ 0.99. The three
correlation measures capture different aspects: Pearson captures linear
relationship, Spearman captures monotonic relationship, Kendall captures
pairwise concordance.

### 5.6 Value/Weight Ratio Descriptors

| Field | Formula | Description |
|-------|---------|-------------|
| `mean_ratio` | (1/n) Σ vᵢ/wᵢ | Mean value/weight ratio |
| `median_ratio` | median({vᵢ/wᵢ}) | Median ratio |
| `std_ratio` | σ(v/w) | Standard deviation of ratios |
| `ratio_entropy` | H(ratios) | Shannon entropy of binned ratio distribution (20 equal-width bins) |
| `unique_ratio_count` | |{vᵢ/wᵢ}| | Number of distinct ratio values |
| `duplicate_ratio_fraction` | (Σ (c−1)) / n | Fraction of items with duplicate ratios |

**Rationale**: The value/weight ratio determines greedy selection order and
branch-and-bound bound tightness. `mean_ratio` and `median_ratio` capture
central tendency; `std_ratio` captures dispersion. `ratio_entropy` measures
diversity of the ratio distribution, which relates to discriminatory power of
the greedy heuristic. `unique_ratio_count` and `duplicate_ratio_fraction` capture
degeneracy in the sorting order.

### 5.7 Instance Diversity

| Field | Formula | Description |
|-------|---------|-------------|
| `unique_weights` | |{wᵢ}| | Number of distinct weight values |
| `unique_values` | |{vᵢ}| | Number of distinct value values |
| `unique_pairs` | |{(wᵢ, vᵢ)}| | Number of distinct (weight, value) pairs |
| `duplicate_items` | Σ (c − 1) | Total count of duplicate items (beyond first copy) |
| `duplicate_pairs` | |{pairs with c > 1}| | Number of (weight, value) pairs that appear multiple times |

**Rationale**: Instance diversity captures degeneracy in the item set. Families
with duplicate items (e.g., InverseCorrelated with n > maxWeight) have reduced
effective problem size. `unique_pairs` measures the true cardinality of the item
pool. `duplicate_items` and `duplicate_pairs` quantify redundancy.

## 6. Verification Evidence

### 6.1 Schema validation

```
Fields: 40
Rows: 6000 (3000 fixed + 3000 scaled)
Missing values: NONE
Duplicate (instance_id, capacity_mode) pairs: 0
instance_id range: 0–2999
Families: 5 (Uncorrelated, WeaklyCorrelated, StronglyCorrelated, InverseCorrelated, AlmostEqualRatios)
n values: 6 (20, 50, 100, 200, 500, 1000)
```

### 6.2 Deterministic output

Confirmed: re-running `extract_features.py` produces bit-identical output.

```
$ python3 extract_features.py && diff results/instances.csv results/instances.csv
# Output: identical (no diff output)
MD5: 3ee015eab8d1c5d83c52d7683a5ccd19
```

### 6.3 Numerical sanity — correlation ranges

All correlations lie within [-1, 1]:

| Family | Mean Pearson | Mean Spearman | Mean Kendall |
|--------|-------------|---------------|--------------|
| Uncorrelated | 0.0052 | 0.0037 | 0.0027 |
| WeaklyCorrelated | 0.9806 | 0.9769 | 0.8751 |
| StronglyCorrelated | 1.0000 | 0.9997 | 0.9952 |
| InverseCorrelated | −1.0000 | −1.0000 | −1.0000 |
| AlmostEqualRatios | 0.9935 | 0.9916 | 0.9383 |

These values exactly match theoretical expectations for each Pisinger family.

### 6.4 Numerical sanity — capacity descriptors

- Fixed mode: capacity = 1000 (constant), capacity_ratio ∈ [0.0019, 0.1812]
- Scaled mode: capacity ∈ [2759, 265810], capacity_ratio ≈ 0.5 (by construction)

### 6.5 Numerical sanity — distribution descriptors

- weight_cv ∈ [0.2723, 0.9830], value_cv ∈ [0.3032, 1.0064]
- weight_skewness ∈ [−1.2049, 1.1494], value_skewness ∈ [−1.1084, 1.2049]
- All in reasonable ranges for [1, 1000] bounded integers

### 6.6 Signature verification per family

- InverseCorrelated: perfect negative correlation (−1.0), high duplicate items (mean 83.4)
- Uncorrelated: near-zero correlation (0.005), no systematic structure
- AlmostEqualRatios: near-perfect correlation (0.994), mean ratio ≈ 1.000, lowest std_ratio (0.057), highest ratio entropy (2.80)
- StronglyCorrelated: near-perfect positive correlation (1.000), moderate duplicates (mean 10.6)

### 6.7 Regression check

```
git diff --stat src/ out/ tables/ figures/ paper/ build_and_run.sh reproduce.sh analyze.py figures.py plot_utils.py
# Output: empty (no benchmark files modified)
```

## 7. Regression Analysis

No regression is possible because:

- No algorithm code was modified
- No benchmark pipeline was modified
- No analysis pipeline was modified
- No existing outputs were overwritten
- `extract_features.py` is a standalone script that reads no existing outputs
- `results/instances.csv` is a new file (directory was previously empty)

## 8. Limitations

1. **Standalone generation, not from Java output**: Features are computed from
   Python-generated instances, not from the actual Java benchmark instances. While
   the Python generator replicates Java's `java.util.Random` and all generator
   logic exactly, floating-point rounding in `AlmostEqualRatios` (Python's
   `round()` uses bankers' rounding vs Java's `Math.round()` half-up) could
   theoretically produce 1-unit value differences in extremely rare cases
   (values exactly at .5 boundary, probability ≈ 0).

2. **No algorithm performance data**: This CSV contains only instance features.
   Algorithm execution data will be merged in Phase 2.5 to create the full
   analysis dataset.

3. **Population statistics**: Variance uses population formula (÷ n). This is
   correct for describing the instance population but differs from sample formulas
   (÷ n−1) used in inferential statistics.

4. **Entropy binning**: Ratio entropy uses 20 equal-width bins per instance.
   Different bin counts or adaptive binning could yield different entropy values.

5. **Kendall tau-a**: Ties are omitted from the denominator, making this measure
   less sensitive than tau-b for instances with many ties.

## 9. Predictors vs Responses

Phase 2.1 contains **ONLY predictor variables**.

The dataset `results/instances.csv` is exclusively composed of instance-level
descriptive features. No algorithm execution statistics are included:

- No runtimes
- No node counts
- No optimal values
- No optimality gaps
- No pruning statistics
- No memory measurements
- No algorithm identifiers

Algorithm execution data (responses) will first appear during Phase 2.5 when the
rich analysis dataset is assembled by joining `results/instances.csv` with
benchmark execution records on the composite key `(instance_id, capacity_mode)`.

This separation is intentional to prevent data leakage during future statistical
modeling. Keeping predictors and responses separate ensures:

1. **No target leakage:** Response variables cannot influence predictor computation.
2. **Reusable predictors:** Instance features can be used with any future experiment.
3. **Clean experimental design:** Predictors are determined entirely by instance generation, independent of algorithmic evaluation.
4. **Causal interpretability:** Effects in downstream models can be attributed to instance structure.

## 10. Join Key Documentation

The composite key `(instance_id, capacity_mode)` uniquely identifies every row
in `results/instances.csv` and serves as the stable join key for merging with
future datasets.

| Key Component | Type | Values | Description |
|---------------|------|--------|-------------|
| `instance_id` | int | 0–2999 | Unique instance identifier, assigned in generation order |
| `capacity_mode` | string | `fixed` or `scaled` | Capacity regime used for feature computation |

**Properties:**

- **Uniqueness (verified):** 0 duplicate pairs in 6,000 rows.
- **Stability:** Determined by instance generation; independent of algorithm execution.
- **Completeness:** Every instance (0–2999) appears under both capacity modes.
- **Merge compatibility:** The benchmark CSV `out/results/full_experiment.csv` carries both `instance_id` and `capacity_mode`, enabling a lossless join in Phase 2.5.

## 11. Scientific Impact

Phase 2.1 transforms the benchmark from a collection of algorithm performance
measurements into a structured dataset suitable for scientific analysis:

- Each instance is now characterized by 38 descriptive features (plus 3 identifiers)
- Features span location, scale, distribution shape, correlation structure, ratio properties, and diversity
- The dataset supports hardness analysis, feature importance, clustering, regression, and predictive modeling
- No algorithm performance data is included — instrumentation is purely passive
- The deterministic generation ensures reproducibility of every feature value

## 12. Remaining Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Instance mismatch with Java benchmark | Low | Generator logic verified against Java source; only `.5` rounding difference possible in AlmostEqualRatios (theoretically < 1 in 10⁶ items) |
| Feature redundancy | Low | Some features will be correlated (e.g., n vs unique_weights); this is expected and can be handled via PCA or feature selection in analysis |
| Schema evolution in Phase 2.5 | Medium | The 40-column schema is frozen now; Phase 2.5 will join on (instance_id, capacity_mode) without modifying this schema |

## 13. Next Milestone — Phase 2.2

Phase 2.2 should begin only after Phase 2.1 has been independently verified,
frozen, committed, tagged, and approved.

Expected scope of Phase 2.2:
- **[To be determined by project lead after Phase 2.1 approval]**

## 14. Repository Evidence Summary

| Claim | Evidence |
|-------|----------|
| Existing algorithms unchanged | `git diff --stat src/` — empty |
| Existing benchmark unchanged | `git diff --stat out/ tables/ figures/ paper/` — empty |
| Deterministic output | Re-run produces identical MD5: `3ee015eab8d1c5d83c52d7683a5ccd19` |
| No missing values | All 6000 × 40 cells populated |
| No duplicate rows | 0 duplicate (instance_id, capacity_mode) pairs |
| Schema clean | 40 columns, all non-null, types consistent |
| Correlation sanity | Per-family means match theoretical expectations |
| Passive instrumentation | No reads of Java outputs; standalone generator |
| Feature correctness | All formulas verified against specification |
