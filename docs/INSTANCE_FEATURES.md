# Instance Feature Specification

## Canonical reference for `results/instances.csv`

**Dataset Version:** 1.0
**Phase:** 2.1
**Status:** Frozen
**File:** `results/instances.csv`
**Rows:** 6,000
**Feature columns:** 36
**Identifier columns:** 4
**Total columns:** 40
**Primary key:** `(instance_id, capacity_mode)`

---

## Feature Provenance Classification

Every feature column (excluding identifiers) is classified as exactly one of:

| Class | Definition |
|-------|------------|
| **Intrinsic instance property** | Directly observable from the raw item set. Involves only counting, summing, or range identification — no distributional or statistical transformation. |
| **Derived statistical property** | Computed from item data using formulas from probability and statistics (moments, correlations, information entropy). These transform the raw item set into summary quantities. |
| **Capacity-derived property** | Depends on the knapsack capacity value, which varies between `fixed` (W = 1000) and `scaled` (W = 0.5 × total_weight) modes. These properties characterize the instance-capacity interaction. |

---

## Section 1: Identifiers

Four columns identify each row uniquely in the dataset. The composite key `(instance_id, capacity_mode)` forms the stable join key for merging with algorithm execution data in Phase 2.5.

| # | Name | Type | Units | Provenance |
|---|------|------|-------|------------|
| 1 | `instance_id` | int | — | Identifier |
| 2 | `n` | int | items | Identifier |
| 3 | `family` | string | — | Identifier |
| 4 | `capacity_mode` | string | — | Identifier |

### `instance_id`

- **Data type:** Integer
- **Range:** 0–2999 (inclusive)
- **Description:** Unique identifier assigned sequentially during instance generation. Order: n-values ascending (20, 50, 100, 200, 500, 1000); within each n, families in fixed order (Uncorrelated, WeaklyCorrelated, StronglyCorrelated, InverseCorrelated, AlmostEqualRatios); within each family, 100 instances.
- **Interpretation:** Stable reference for merging with algorithm performance data.

### `n`

- **Data type:** Integer
- **Units:** Items
- **Range:** {20, 50, 100, 200, 500, 1000}
- **Description:** Number of items in the knapsack instance.
- **Interpretation:** Primary measure of problem size. Algorithm runtime, memory, and search space size scale with n.

### `family`

- **Data type:** String
- **Values:** `Uncorrelated`, `WeaklyCorrelated`, `StronglyCorrelated`, `InverseCorrelated`, `AlmostEqualRatios`
- **Description:** Pisinger (2005) instance family name. Determines the generative relationship between item weights and values.
- **Interpretation:** The primary categorical factor in the experimental design. Each family produces a distinct correlation structure between weight and value, directly affecting algorithm behavior.

### `capacity_mode`

- **Data type:** String
- **Values:** `fixed`, `scaled`
- **Description:** Indicates which capacity regime was used for feature computation.
- **Fixed:** W = 1000 (constant across all instances).
- **Scaled:** W = floor(0.5 × total_weight) (varies per instance).
- **Interpretation:** This column, combined with `instance_id`, forms the join key for merging with algorithm execution data. It distinguishes between the two experimental conditions.

---

## Section 2: Basic Statistics

| # | Name | Type | Units | Provenance |
|---|------|------|-------|------------|
| 5 | `total_weight` | float | weight units | Intrinsic instance property |
| 6 | `total_value` | float | value units | Intrinsic instance property |
| 7 | `mean_weight` | float | weight units | Derived statistical property |
| 8 | `mean_value` | float | value units | Derived statistical property |
| 9 | `median_weight` | float | weight units | Derived statistical property |
| 10 | `median_value` | float | value units | Derived statistical property |
| 11 | `std_weight` | float | weight units | Derived statistical property |
| 12 | `std_value` | float | value units | Derived statistical property |
| 13 | `min_weight` | float | weight units | Intrinsic instance property |
| 14 | `max_weight` | float | weight units | Intrinsic instance property |
| 15 | `min_value` | float | value units | Intrinsic instance property |
| 16 | `max_value` | float | value units | Intrinsic instance property |

### `total_weight`

- **Mathematical definition:** Σᵢ wᵢ
- **Formula:** `sum(weights)`
- **Expected range (this dataset):** [5,519, 531,621]
- **Description:** Sum of all item weights in the instance. For mode `fixed`, this is the total weight of all items. For mode `scaled`, capacity depends on this value.
- **Why it matters:** Total weight relative to capacity determines constraint tightness. Instances with total_weight ≫ W are capacity-constrained; instances with total_weight ≤ W are trivially solvable.

### `total_value`

- **Mathematical definition:** Σᵢ vᵢ
- **Formula:** `sum(values)`
- **Expected range (this dataset):** [5,509, 530,460]
- **Description:** Sum of all item values.
- **Why it matters:** Upper bound on achievable solution value. Together with total_weight, defines the average value density of the instance.

### `mean_weight`

- **Mathematical definition:** (1/n) Σᵢ wᵢ
- **Formula:** `mean_weight = total_weight / n`
- **Expected range (this dataset):** [276, 716]
- **Description:** Arithmetic mean of item weights.
- **Why it matters:** Determines the average item size. Influences the number of items that can fit in the knapsack (`average_fillable_items`).

### `mean_value`

- **Mathematical definition:** (1/n) Σᵢ vᵢ
- **Formula:** `mean_value = total_value / n`
- **Expected range (this dataset):** [276, 716]
- **Description:** Arithmetic mean of item values.
- **Why it matters:** Together with mean_weight, characterizes average value density.

### `median_weight`

- **Mathematical definition:** median({wᵢ})
- **Implementation:** For even n, average of the two middle values of the sorted weight array.
- **Expected range (this dataset):** Approximately [276, 716]
- **Description:** Median item weight. More robust to outliers than mean_weight.
- **Why it matters:** For families with skewed weight distributions (e.g., InverseCorrelated), the median provides a better central-tendency descriptor than the mean.

### `median_value`

- **Mathematical definition:** median({vᵢ})
- **Implementation:** Same as median_weight but computed on values.
- **Expected range (this dataset):** Approximately [276, 716]
- **Description:** Median item value.
- **Why it matters:** Robust central tendency measure for value distributions.

### `std_weight`

- **Mathematical definition:** σ_w = √((1/n) Σᵢ (wᵢ − μ_w)²)
- **Implementation:** `statistics.pstdev(weights)` (population standard deviation, denominator n)
- **Expected range (this dataset):** [146, 295]
- **Description:** Population standard deviation of item weights. Measures absolute dispersion of the weight distribution.
- **Why it matters:** High weight dispersion means items vary widely in size, which affects capacity packing efficiency and the difficulty of selection decisions.

### `std_value`

- **Mathematical definition:** σ_v = √((1/n) Σᵢ (vᵢ − μ_v)²)
- **Implementation:** `statistics.pstdev(values)` (population standard deviation, denominator n)
- **Expected range (this dataset):** [146, 295]
- **Description:** Population standard deviation of item values.
- **Why it matters:** High value dispersion means some items are much more valuable than others, which can guide heuristic selection.

### `min_weight`

- **Mathematical definition:** min({wᵢ})
- **Expected range:** [1, 1000]
- **Description:** Minimum item weight in the instance.
- **Why it matters:** The smallest item determines the granularity of capacity utilization. Very small items allow fine-grained packing.

### `max_weight`

- **Mathematical definition:** max({wᵢ})
- **Expected range:** [1, 1000]
- **Description:** Maximum item weight in the instance.
- **Why it matters:** Large items may exceed capacity individually, reducing the effective item count.

### `min_value`

- **Mathematical definition:** min({vᵢ})
- **Expected range:** [1, 1000]
- **Description:** Minimum item value.
- **Why it matters:** Lower bound on per-item contribution.

### `max_value`

- **Mathematical definition:** max({vᵢ})
- **Expected range:** [1, 1000]
- **Description:** Maximum item value.
- **Why it matters:** Upper bound on per-item contribution.

---

## Section 3: Distribution Descriptors

| # | Name | Type | Units | Provenance |
|---|------|------|-------|------------|
| 17 | `weight_cv` | float | dimensionless | Derived statistical property |
| 18 | `value_cv` | float | dimensionless | Derived statistical property |
| 19 | `weight_skewness` | float | dimensionless | Derived statistical property |
| 20 | `value_skewness` | float | dimensionless | Derived statistical property |
| 21 | `weight_kurtosis` | float | dimensionless | Derived statistical property |
| 22 | `value_kurtosis` | float | dimensionless | Derived statistical property |

### `weight_cv`

- **Mathematical definition:** CV_w = σ_w / μ_w
- **Formula:** `std_weight / mean_weight` (0.0 if mean_weight = 0)
- **Expected range (this dataset):** [0.27, 0.98]
- **Description:** Coefficient of variation of item weights. Measures relative dispersion normalized by the mean.
- **Interpretation:** CV = 0 means all weights are identical. Higher CV indicates greater relative spread. Uniform[1, 1000] has CV ≈ 0.58.
- **Why it matters:** Relative weight dispersion affects whether average-based capacity estimates (e.g., `average_fillable_items`) are reliable. High CV means individual items deviate substantially from the average.

### `value_cv`

- **Mathematical definition:** CV_v = σ_v / μ_v
- **Formula:** `std_value / mean_value` (0.0 if mean_value = 0)
- **Expected range (this dataset):** [0.30, 1.01]
- **Description:** Coefficient of variation of item values.
- **Interpretation:** Analogous to weight_cv but for the value distribution.
- **Why it matters:** High value CV indicates that item values span multiple orders of magnitude relative to the mean, which can make greedy selection more effective.

### `weight_skewness`

- **Mathematical definition:** γ₁_w = m₃ / σ_w³ where m₃ = (1/n) Σᵢ (wᵢ − μ_w)³
- **Formula:** `sum((w - mu)^3) / n / sigma^3` (0.0 if sigma = 0)
- **Expected range (this dataset):** [−1.20, 1.15]
- **Description:** Third standardized moment of the weight distribution. Measures asymmetry.
- **Interpretation:** Positive skewness means a long right tail (few heavy items, many light items). Negative skewness means a long left tail (few light items, many heavy items). Zero indicates symmetry.
- **Why it matters:** Skewed weight distributions concentrate mass at one end of the range, affecting how capacity is utilized. InverseCorrelated instances, for example, tend to have many low-weight items (positive skew).

### `value_skewness`

- **Mathematical definition:** γ₁_v = m₃ / σ_v³
- **Formula:** Same as weight_skewness but on values.
- **Expected range (this dataset):** [−1.11, 1.20]
- **Description:** Third standardized moment of the value distribution.
- **Interpretation:** Analogous to weight_skewness but for values.
- **Why it matters:** Skewed value distributions concentrate algorithmic search on high-value items.

### `weight_kurtosis`

- **Mathematical definition:** γ₂_w = m₄ / σ_w⁴ − 3 where m₄ = (1/n) Σᵢ (wᵢ − μ_w)⁴
- **Formula:** `sum((w - mu)^4) / n / sigma^4 - 3` (0.0 if sigma = 0)
- **Expected range (this dataset):** Approximately [−1.5, 0.0] for bounded uniform-like distributions
- **Description:** Excess kurtosis (fourth standardized moment minus 3) of the weight distribution. Measures tail heaviness relative to a normal distribution.
- **Interpretation:** Positive excess kurtosis indicates heavy tails or peakedness. Negative excess kurtosis indicates light tails (platykurtic). The uniform distribution has excess kurtosis −1.2. Normal distribution has excess kurtosis 0.
- **Why it matters:** Kurtosis affects the frequency of extreme weight values, which in turn affects the likelihood of encountering items that are much heavier or lighter than average.

### `value_kurtosis`

- **Mathematical definition:** γ₂_v = m₄ / σ_v⁴ − 3
- **Formula:** Same as weight_kurtosis but on values.
- **Expected range (this dataset):** Approximately [−1.5, 0.0]
- **Description:** Excess kurtosis of the value distribution.
- **Interpretation:** Analogous to weight_kurtosis but for values.
- **Why it matters:** High value kurtosis means occasional very high or very low value items that could significantly affect the optimal solution.

---

## Section 4: Capacity Descriptors

| # | Name | Type | Units | Provenance |
|---|------|------|-------|------------|
| 23 | `capacity` | int | weight units | Capacity-derived property |
| 24 | `capacity_ratio` | float | dimensionless | Capacity-derived property |
| 25 | `slack` | float | weight units | Capacity-derived property |
| 26 | `average_fillable_items` | float | items | Capacity-derived property |

### `capacity`

- **Mathematical definition:** W
- **Data type:** Integer
- **Units:** Weight units
- **Expected range (this dataset):** Fixed mode: 1000 (constant). Scaled mode: [2,759, 265,810].
- **Description:** Knapsack capacity. For fixed mode, W = 1000. For scaled mode, W = floor(0.5 × total_weight).
- **Interpretation:** The fundamental constraint parameter. W determines which subsets of items are feasible.
- **Why it matters:** Capacity is the primary algorithmic parameter. DP runtime scales as O(nW). B&B search tree size depends critically on capacity. Greedy heuristic quality varies with capacity regime.

### `capacity_ratio`

- **Mathematical definition:** W / total_weight
- **Formula:** `capacity / total_weight` (0.0 if total_weight = 0)
- **Expected range (this dataset):** Fixed mode: [0.0019, 0.1812]. Scaled mode: ≈ 0.5.
- **Description:** Fraction of total item weight that the knapsack can hold.
- **Interpretation:** Values near 0 mean the instance is extremely capacity-constrained (only a tiny fraction of items fit). Values near 1 mean nearly all items fit. For scaled mode, capacity_ratio ≈ 0.5 by construction.
- **Why it matters:** capacity_ratio is one of the strongest known predictors of knapsack problem difficulty (Pisinger 2005). Very low ratios produce few-item feasible subsets; very high ratios (near 1) make the problem nearly trivial. Intermediate ratios produce the richest combinatorial structure.

### `slack`

- **Mathematical definition:** total_weight − W
- **Formula:** `total_weight - capacity`
- **Expected range (this dataset):** Fixed mode: [4,519, 530,621]. Scaled mode: ≈ 0.5 × total_weight.
- **Description:** Total weight that exceeds the knapsack capacity. Always non-negative for this dataset.
- **Interpretation:** Slack represents the total weight that must be excluded from any feasible solution. High slack means many items must be left out.
- **Why it matters:** Slack (equivalently, total_weight minus capacity) is the complement of capacity_ratio. It provides an absolute measure of how much must be excluded, while capacity_ratio provides a relative measure.

### `average_fillable_items`

- **Mathematical definition:** W / μ_w
- **Formula:** `capacity / mean_weight` (0.0 if mean_weight = 0)
- **Expected range (this dataset):** Fixed mode: [1.4, 3.6]. Scaled mode: approximately [0.7 × n, 1.8 × n].
- **Description:** Estimated number of items that can fit in the knapsack, assuming items of average weight.
- **Interpretation:** Estimates the effective dimensionality of the packing problem. Low values (e.g., < 5) mean very few items fit, producing a small search space. High values (e.g., > 100) mean many items fit, producing a large combinatorial space.
- **Why it matters:** Together with n, this estimates the effective combinatorial complexity of the instance. When average_fillable_items is small relative to n, the search is constrained to small subsets.

---

## Section 5: Correlation Descriptors

| # | Name | Type | Units | Provenance |
|---|------|------|-------|------------|
| 27 | `pearson_corr` | float | dimensionless | Derived statistical property |
| 28 | `spearman_corr` | float | dimensionless | Derived statistical property |
| 29 | `kendall_corr` | float | dimensionless | Derived statistical property |

### `pearson_corr`

- **Mathematical definition:** r = Σᵢ (wᵢ − μ_w)(vᵢ − μ_v) / √(Σᵢ (wᵢ − μ_w)² · Σᵢ (vᵢ − μ_v)²)
- **Formula:** population Pearson correlation coefficient
- **Range:** [−1, 1]
- **Description:** Linear correlation between item weights and values.
- **Interpretation per family (observed means):**
  - Uncorrelated: 0.005 (no linear relationship)
  - WeaklyCorrelated: 0.981 (strong positive, v ≈ w + noise)
  - StronglyCorrelated: 1.000 (near-perfect positive, v = w + offset)
  - InverseCorrelated: −1.000 (perfect negative, v = 1001 − w)
  - AlmostEqualRatios: 0.994 (near-perfect, ratio ≈ 1.0)
- **Why it matters:** Weight-value correlation determines whether greedy selection by ratio is effective. For strongly correlated instances, any selection by weight or value alone works well. For uncorrelated instances, ratio-based selection is essential.

### `spearman_corr`

- **Mathematical definition:** ρ = r(rank(w), rank(v)), where ranks are average ranks with ties.
- **Formula:** Pearson correlation computed on rank-transformed weights and values.
- **Range:** [−1, 1]
- **Description:** Monotonic correlation between weights and values. Captures non-linear monotonic relationships that Pearson may miss.
- **Interpretation per family (observed means):**
  - Uncorrelated: 0.004
  - WeaklyCorrelated: 0.977
  - StronglyCorrelated: 0.997
  - InverseCorrelated: −1.000
  - AlmostEqualRatios: 0.992
- **Why it matters:** Spearman detects whether larger weights consistently correspond to larger values (or vice versa), even if the relationship is not linear. This affects the ordering of items by greedy and B&B bounds.

### `kendall_corr`

- **Mathematical definition:** τ = (C − D) / (C + D), where C = concordant pairs and D = discordant pairs. Ties are ignored (not counted in denominator).
- **Formula:** tau-a variant
- **Range:** [−1, 1]
- **Description:** Pairwise concordance between weight and value rankings.
- **Interpretation per family (observed means):**
  - Uncorrelated: 0.003
  - WeaklyCorrelated: 0.875
  - StronglyCorrelated: 0.995
  - InverseCorrelated: −1.000
  - AlmostEqualRatios: 0.938
- **Why it matters:** Kendall tau measures the probability that a randomly selected pair of items has concordant weight-value ordering. It is more robust to outliers than Pearson and directly captures pairwise dominance relationships that matter for combinatorial selection.

---

## Section 6: Ratio Descriptors

| # | Name | Type | Units | Provenance |
|---|------|------|-------|------------|
| 30 | `mean_ratio` | float | value/weight | Derived statistical property |
| 31 | `median_ratio` | float | value/weight | Derived statistical property |
| 32 | `std_ratio` | float | value/weight | Derived statistical property |
| 33 | `ratio_entropy` | float | nats | Derived statistical property |
| 34 | `unique_ratio_count` | int | dimensionless | Intrinsic instance property |
| 35 | `duplicate_ratio_fraction` | float | dimensionless | Derived statistical property |

### `mean_ratio`

- **Mathematical definition:** (1/n) Σᵢ vᵢ / wᵢ
- **Formula:** `statistics.mean(ratios)`
- **Description:** Mean value-to-weight ratio across all items.
- **Interpretation:** The average value-per-unit-weight of items in the instance. Higher values indicate more valuable items per unit weight.
- **Why it matters:** Greedy algorithm sorts by decreasing v/w ratio. The mean ratio provides a baseline for evaluating individual item ratios.

### `median_ratio`

- **Mathematical definition:** median({vᵢ/wᵢ})
- **Formula:** Median of the ratios array (average of two middle values for even n).
- **Description:** Median value-to-weight ratio. More robust to extreme ratio values than mean_ratio.
- **Interpretation:** For families with extreme ratio outliers (e.g., InverseCorrelated where a weight-1 item has ratio ~1000), the median provides a more stable central tendency measure.
- **Why it matters:** Robust measure of central ratio tendency.

### `std_ratio`

- **Mathematical definition:** σ(v/w) = √((1/n) Σᵢ (vᵢ/wᵢ − μ_{v/w})²)
- **Formula:** `statistics.pstdev(ratios)`
- **Description:** Population standard deviation of value-to-weight ratios.
- **Interpretation:** Measures how much items differ in their value density. High std_ratio means items span a wide range of efficiency. Low std_ratio means items are similarly efficient.
- **Why it matters:** When std_ratio is very small (AlmostEqualRatios: ~0.057), greedy selection has little discriminatory power because most items have near-identical ratios. This is known to increase the optimality gap for the greedy heuristic.

### `ratio_entropy`

- **Mathematical definition:** H = − Σⱼ pⱼ log(pⱼ), where pⱼ is the fraction of ratios falling in bin j of 20 equal-width bins spanning [min(v/w), max(v/w)].
- **Formula:** Shannon entropy on binned ratio distribution (20 bins).
- **Units:** Nats (natural logarithm)
- **Range:** [0, log(20)] ≈ [0, 2.996]
- **Description:** Entropy of the ratio distribution. Measures how evenly ratios are distributed across 20 bins.
- **Interpretation:** High entropy means ratios are spread across many bins (diverse ratio values). Low entropy means most ratios fall in a few bins (concentrated ratios).
- **Observed per family (mean):**
  - AlmostEqualRatios: 2.80 (highest — ratios cluster near 1.0 with uniform noise filling many bins)
  - WeaklyCorrelated: 1.18 (moderate spread)
  - Uncorrelated: 0.69 (skewed ratio distribution concentrates in low bins)
  - StronglyCorrelated: 0.67 (concentrated near 1.0)
  - InverseCorrelated: 0.56 (concentrated due to deterministic ratio map)
- **Why it matters:** Ratio entropy captures the discriminatory power of the greedy ratio sort. Low entropy means many items compete with similar ratios, increasing the chance that greedy makes suboptimal choices.

### `unique_ratio_count`

- **Mathematical definition:** |{vᵢ/wᵢ : i = 1…n}|
- **Formula:** `len(set(ratios))`
- **Data type:** Integer
- **Range:** [1, n]
- **Description:** Number of distinct value-to-weight ratio values.
- **Interpretation:** When this equals n, every item has a unique ratio (full discriminatory power for greedy sort). When much smaller than n, many items share the same ratio value, creating ties in the greedy ordering.
- **Why it matters:** Ties in ratio ordering reduce the effectiveness of greedy selection. Branch-and-bound bounds also depend on ratio ordering.

### `duplicate_ratio_fraction`

- **Mathematical definition:** (Σ_{c} (c − 1)) / n, where c is the count of each distinct ratio value.
- **Formula:** `sum(c - 1 for c in Counter(ratios).values()) / n`
- **Range:** [0, 1 − 1/n]
- **Description:** Fraction of items that are surplus copies of a ratio value (beyond the first occurrence).
- **Interpretation:** 0 means all ratios are unique. Higher values mean many items share a ratio with other items. Combined with unique_ratio_count, provides a complete picture of ratio degeneracy.
- **Why it matters:** Duplicate ratios reduce the effective granularity of the ratio ordering. For families like InverseCorrelated, many (weight, value) pairs map to the same ratio, increasing duplicates.

---

## Section 7: Diversity Descriptors

| # | Name | Type | Units | Provenance |
|---|------|------|-------|------------|
| 36 | `unique_weights` | int | dimensionless | Intrinsic instance property |
| 37 | `unique_values` | int | dimensionless | Intrinsic instance property |
| 38 | `unique_pairs` | int | dimensionless | Intrinsic instance property |
| 39 | `duplicate_items` | int | items | Intrinsic instance property |
| 40 | `duplicate_pairs` | int | pairs | Intrinsic instance property |

### `unique_weights`

- **Mathematical definition:** |{wᵢ}|
- **Formula:** `len(set(weights))`
- **Data type:** Integer
- **Range:** [1, n]
- **Description:** Number of distinct weight values in the instance.
- **Interpretation:** When n exceeds the maximum possible distinct weight values (which is bounded by the generator's maxWeight parameter = 1000), weights must repeat. Lower values indicate more weight repetition.
- **Why it matters:** Repetition of weight values reduces the effective diversity of items. For DP, repeated weights mean the DP table rows see similar state transitions. For B&B, repeated weights create more ties in bound computation.

### `unique_values`

- **Mathematical definition:** |{vᵢ}|
- **Formula:** `len(set(values))`
- **Data type:** Integer
- **Range:** [1, n]
- **Description:** Number of distinct value values.
- **Interpretation:** Analogous to unique_weights but for values. For InverseCorrelated where value is deterministically derived from weight (v = 1001 − w), unique_values equals unique_weights.
- **Why it matters:** Value repetition reduces the diversity of achievable solution values and affects DP table occupancy.

### `unique_pairs`

- **Mathematical definition:** |{(wᵢ, vᵢ)}|
- **Formula:** `len(set(items))`
- **Data type:** Integer
- **Range:** [1, n]
- **Description:** Number of distinct (weight, value) pairs — the true cardinality of the item pool after removing duplicates.
- **Interpretation:** When an instance has duplicate items (same weight AND same value), unique_pairs < n. This measures the effective item set size.
- **Why it matters:** Duplicate items are redundant — selecting one copy is equivalent to selecting any other. This reduces the true search space size. For InverseCorrelated with n = 1000, approximately 632 unique pairs exist (out of 1000 items), meaning ~368 items are redundant.

### `duplicate_items`

- **Mathematical definition:** Σ_{(w,v)} (c_{(w,v)} − 1), where c is the count of each (weight, value) pair.
- **Formula:** `sum(c - 1 for c in Counter(items).values())`
- **Data type:** Integer
- **Range:** [0, n − unique_pairs]
- **Description:** Total count of surplus copies of duplicate (weight, value) pairs.
- **Interpretation:** Each pair that appears k times contributes k−1 to this count. This measures the total redundancy in the item set.
- **Why it matters:** High duplicate_items (e.g., InverseCorrelated with mean 83.4) means many items are functionally identical, reducing combinatorial complexity.

### `duplicate_pairs`

- **Mathematical definition:** |{(w, v) : c_{(w,v)} > 1}|
- **Formula:** `sum(1 for c in Counter(items).values() if c > 1)`
- **Data type:** Integer
- **Range:** [0, floor(n/2)]
- **Description:** Number of distinct (weight, value) pairs that have at least one duplicate copy.
- **Interpretation:** Measures how many distinct item types have redundancy. Differs from duplicate_items in that it counts the number of duplicated pair types, not the total number of surplus copies.
- **Why it matters:** This captures the breadth of redundancy across distinct item types, as opposed to depth.

---

## Predictors vs Responses

### Phase 2.1 contains ONLY predictor variables.

This dataset (`results/instances.csv`) is exclusively composed of instance-level
descriptive features. No algorithm execution statistics are included:

- No runtimes
- No node counts
- No optimal values
- No optimality gaps
- No pruning statistics
- No memory measurements
- No algorithm identifiers

This separation is intentional to prevent data leakage during future statistical
modeling. When algorithm execution data is joined with instance features in
Phase 2.5, the instance features serve as predictors (X) and algorithm performance
metrics serve as responses (Y). Keeping them separate ensures:

1. **No target leakage:** Response variables cannot influence predictor computation.
2. **Reusable predictors:** Instance features can be used with any future algorithm or experiment without recomputation.
3. **Clean experimental design:** Predictors are determined entirely by the instance generation process, independent of any specific algorithmic evaluation.
4. **Causal interpretability:** Effects in downstream models can be attributed to instance structure, not to interactions with the experimental setup.

Algorithm outputs will first appear during Phase 2.5 when the rich analysis
dataset is assembled by joining `results/instances.csv` with benchmark execution
records on the composite key `(instance_id, capacity_mode)`.

---

## Join Key Documentation

The composite key `(instance_id, capacity_mode)` uniquely identifies every row
in `results/instances.csv` and serves as the stable join key for merging with
future datasets.

| Key Component | Type | Values | Description |
|---------------|------|--------|-------------|
| `instance_id` | int | 0–2999 | Unique instance identifier, assigned in generation order |
| `capacity_mode` | string | `fixed` or `scaled` | Capacity regime used for feature computation |

**Properties:**

- **Uniqueness:** Every combination of `(instance_id, capacity_mode)` appears
  exactly once in `results/instances.csv` (verified: 0 duplicate pairs in 6,000 rows).
- **Stability:** The key is determined by the instance generation process and does
  not depend on algorithm execution. It will remain stable across future phases.
- **Completeness:** Every instance (0–2999) appears under both `fixed` and `scaled`
  modes, producing 6,000 unique key values.

**Phase 2.5 join:** Algorithm execution data will be joined with instance features
using this composite key. Each algorithm run in the benchmark CSV
(`out/results/full_experiment.csv`) carries both `instance_id` and `capacity_mode`,
enabling a lossless merge.
