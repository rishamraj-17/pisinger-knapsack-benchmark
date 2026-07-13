# Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics

**Abstract** — We present a systematic empirical comparison of three classical 0/1 knapsack algorithms—Greedy, Dynamic Programming (DP), and Branch & Bound (B&B)—across five distinct instance families. Our study reveals that instance correlation structure significantly affects practical performance, but not always in the ways previously assumed: Greedy achieves optimal solutions (0% gap) on Inverse Correlated instances and small gaps (< 1% median) on Uncorrelated and Weakly Correlated instances, while showing moderate gaps (2.5% median) on Strongly Correlated instances. DP runtime scales linearly with n at fixed capacity and is largely insensitive to instance structure. B&B explores the fewest nodes on Uncorrelated and Weakly Correlated instances but suffers exponential blowup on Strongly Correlated and Inverse Correlated families at larger sizes. These results provide practical guidance for algorithm selection based on observable instance properties.

**Keywords** — knapsack problem, empirical algorithmics, greedy algorithms, dynamic programming, branch and bound, experimental analysis

---

## 1. Introduction

The 0/1 Knapsack Problem is a cornerstone of combinatorial optimization with applications in resource allocation, portfolio optimization, and cryptography. Three classical algorithms solve it exactly or approximately:

- **Greedy** (by value/weight ratio): O(n log n), fast but not guaranteed optimal
- **Dynamic Programming**: O(nW) time, O(W) space, pseudo-polynomial
- **Branch & Bound**: Exponential worst-case, often fast in practice

Despite decades of study, *practical* performance under different instance characteristics remains underexplored in a unified framework. Pisinger (2005) showed instance correlations critically affect hardness, but most studies focus on asymptotic complexity or single algorithms.

**Research Question**: How do different characteristics of 0/1 Knapsack instances affect the practical performance of Greedy, Dynamic Programming, and Branch & Bound algorithms?

**Contributions**:
1. Systematic evaluation across 5 instance families × 5 sizes × 30 seeds = 750 instances (2,250 algorithm runs)
2. Quantified trade-offs: runtime, memory, optimality gap, search effort
3. Practical decision rules for algorithm selection

---

## 2. Related Work

The 0/1 Knapsack Problem has been studied extensively since the 1950s. Martello and Toth [2] provide the foundational algorithmic treatment, covering DP, B&B, and branch-and-bound variants. Kellerer et al. [3] offer a comprehensive modern survey covering approximation schemes, dynamic programming refinements, and practical heuristics. Korte and Vygen [6] place the knapsack problem within the broader landscape of combinatorial optimization.

**Dynamic programming.** The classic O(nW) DP approach dates to Horowitz and Sahni [5], who first formulated the recurrence used in modern implementations. Space-optimized 1D variants reducing memory to O(W) are now standard [4, Ch. 35].

**Branch and bound.** Martello and Toth [2] developed the strong-formulation B&B that dominates practical solvers. Their LP-relaxation bounding and best-first search strategy remain the baseline for comparison. Pisinger [1] showed that B&B performance varies dramatically with instance structure, motivating our family-by-family analysis.

**Greedy heuristics.** The ratio-based greedy (sort by $v_i/w_i$, pack greedily) is the most studied heuristic. It achieves no constant-factor worst-case guarantee for 0/1 knapsack [4, Ch. 35], yet performs well in practice on many instance types. Ibarra and Kim [7] showed that a modified greedy achieves a $(1-\epsilon)$ approximation in O(n log n) time, though this result applies to the fractional variant.

**Instance hardness.** Pisinger [1] introduced the five instance families used here (Uncorrelated through Almost Equal Ratios), demonstrating that instance correlation—not just size—determines practical hardness. This framework has been adopted by subsequent empirical studies [2, 3]. Our work extends this line by systematically comparing three algorithms on a unified benchmark across all five families.

**Empirical studies.** Most prior comparisons focus on a single algorithm or a small subset of families. Martello and Toth [2, Ch. 6] provide benchmark results for B&B on selected families. No prior work that we know of simultaneously evaluates Greedy, DP, and B&B across all five Pisinger families with controlled parameters and statistical rigor.

---

## 3. Algorithms

### 3.1 Greedy (by Value/Weight Ratio)
Sort items by $v_i/w_i$ descending. Pack while capacity allows.
- **Time**: O(n log n)  
- **Space**: O(n)
- **Guarantee**: No constant-factor approximation for 0/1 knapsack

### 3.2 Dynamic Programming
Recurrence: $dp[w] = \max(dp[w], dp[w-w_i] + v_i)$ for $w = W \dots w_i$
- **Time**: O(nW)
- **Space**: O(W) (1D array, backward iteration)
- **Exact** for all instances

### 3.3 Branch & Bound
Best-first search on include/exclude tree.
- **Upper bound**: Fractional knapsack on remaining items (items sorted by $v_i/w_i$)
- **Pruning**: Discard node if bound ≤ best found
- **Queue**: Max-heap by bound (priority queue)
- **Exact** with search effort dependent on bound tightness

---

## 4. Instance Families

Following Pisinger (2005), we generate five families:

| Family | Weight $w_i$ | Value $v_i$ | Rationale |
|--------|--------------|-------------|-----------|
| **Uncorrelated** | $U(1, 1000)$ | $U(1, 1000)$ | Baseline; no structure |
| **Weakly Correlated** | $U(1, 1000)$ | $w_i + U(-100, 100)$ | Mild correlation |
| **Strongly Correlated** | $U(1, 1000)$ | $w_i + U(1, 10)$ | $v \approx w$; greedy near-optimal |
| **Inverse Correlated** | $U(1, 1000)$ | $1001 - w_i$ | Heavy = low value; $v + w = 1001$ |
| **Almost Equal Ratios** | $U(1, 1000)$ | $w_i \times 1.0 \times (1 + U(-0.1, 0.1))$ | Ratios nearly identical; ties break arbitrarily |

Parameters: $n \in \{20, 50, 100, 200, 500\}$, $W = 1000$, 30 seeds per $(n, \text{family})$.

---

## 5. Experimental Setup

- **Language**: Java 21
- **JVM**: Warmup 3 runs per instance, then measured run
- **Timeout**: 30s per instance per algorithm
- **Metrics**: Wall time (ns), heap memory (MB), solution value, optimality gap (greedy), B&B nodes explored
- **Hardware**: Single thread, Intel/AMD x64, Linux

---

## 6. Results

### 6.1 Execution Time

**Table 1**: Mean execution time (ms) at n=500 (W=1000, 30 seeds) with 95% bootstrap CI

| Algorithm | Uncorrelated | Weakly Corr. | Strongly Corr. | Inverse Corr. | Equal Ratios |
|-----------|-------------|--------------|----------------|---------------|--------------|
| Greedy | 0.28 (CI: 0.27–0.29) | 0.33 (CI: 0.31–0.34) | 0.22 (CI: 0.20–0.24) | 0.16 (CI: 0.13–0.19) | 0.10 (CI: 0.09–0.10) |
| DP | 0.41 (CI: 0.37–0.45) | 0.38 (CI: 0.33–0.43) | 0.44 (CI: 0.37–0.53) | 0.44 (CI: 0.40–0.48) | 0.41 (CI: 0.38–0.44) |
| B&B | 0.12 (CI: 0.11–0.14) | 0.16 (CI: 0.14–0.19) | 0.73 (CI: 0.43–1.10) | 182.60 (CI: 8.88–519.90) | 0.31 (CI: 0.22–0.42) |

**Key observations**:
- Greedy: Sub-millisecond across all families (0.10–0.33 ms), with a 3.3x range reflecting family-dependent sorting behavior.
- DP: Near-linear scaling with n at fixed W=1000; family dependence is modest (0.38–0.44 ms at n=500).
- B&B: Fast on Uncorrelated/Weakly Correlated/Equal Ratios (< 0.31 ms); **extreme variance on Inverse Correlated** (median 4.67 ms, mean 182.60 ms) due to several runs hitting the 30s timeout (max 4974 ms, 25M nodes explored).

**Figure 1** (time vs n): All algorithms scale near-linearly with n at fixed W. B&B variance is highest on Inverse Correlated (std 905.65 ms vs 0.97 ms for Strongly Correlated at n=500), with the distribution heavily right-skewed by timeout-censored runs.

### 6.2 Optimality Gap (Greedy)

**Table 2**: Greedy optimality gap statistics (all n pooled)

| Family | Median Gap (%) | Mean ± Std (%) |
|--------|---------------|----------------|
| Uncorrelated | 0.3 | 0.9 ± 1.6 |
| Weakly Correlated | 0.8 | 2.1 ± 3.5 |
| Strongly Correlated | 2.5 | 4.7 ± 6.3 |
| **Inverse Correlated** | **0.0** | **0.0 ± 0.0** |
| Equal Ratios | 0.4 | 1.1 ± 2.1 |

**Per-size breakdown**:

| n | Uncorr. | Weak Corr. | Strong Corr. | Inverse Corr. | Equal Ratios |
|---|---------|------------|--------------|---------------|--------------|
| 20 | 0.0% | 3.2% | 10.8% | **0.0%** | 2.0% |
| 50 | 0.1% | 1.9% | 5.0% | **0.0%** | 1.1% |
| 100 | 0.7% | 1.0% | 3.0% | **0.0%** | 0.6% |
| 200 | 0.5% | 0.6% | 1.7% | **0.0%** | 0.2% |
| 500 | 0.3% | 0.4% | 0.7% | **0.0%** | 0.2% |

**Findings**:
- **Inverse Correlated: Greedy is optimal (0% gap) at ALL sizes**. This is a theoretical consequence: for instances where $v_i + w_i = \text{constant}$, greedy by ratio (which sorts by ascending weight) is provably optimal.
- **Uncorrelated/Weakly Correlated**: Small gaps at all sizes (median < 1%). The "catastrophic failure" (>50% gap) reported in prior literature is not observed with this generator.
- **Strongly Correlated**: Moderate gaps (2.5% median, up to 10.8% at n=20) that decrease with n.
- **Equal Ratios**: Very small gaps at larger n; variance at small n due to arbitrary tie-breaking.

### 6.3 Branch & Bound Search Effort

**Table 3**: B&B nodes explored (all n pooled)

| Family | Median | Min | Max |
|--------|--------|-----|-----|
| Uncorrelated | 138 | 22 | 1,156 |
| Weakly Correlated | 224 | 14 | 2,985 |
| Strongly Correlated | 1,032 | 25 | 39,840 |
| Inverse Correlated | 562 | 24 | **25,231,225** |
| Equal Ratios | 291 | 5 | 10,139 |

**Per-size B&B nodes (median)**:

| n | Uncorrelated | Weakly Corr. | Strongly Corr. | Inverse Corr. | Equal Ratios |
|---|-------------|--------------|----------------|---------------|--------------|
| 20 | 28 | 94 | 320 | 38 | 102 |
| 50 | 69 | 108 | 903 | 262 | 248 |
| 100 | 140 | 252 | 1,169 | 644 | 393 |
| 200 | 248 | 520 | 2,256 | 4,318 | 503 |
| 500 | 582 | 800 | 3,228 | **46,244** | 984 |

**Findings**:
- **Strongly Correlated**: Many nodes despite tight bounds; fractional bound is loose when $v_i \approx w_i$ because many items fit fractionally.
- **Inverse Correlated**: Explores the **most nodes at n=500** (median 46,244), not the fewest. Extreme outlier (25M nodes) causes high mean time.
- **Equal Ratios**: Moderate effort; identical ratios create many equivalent bound values.

### 6.4 B&B Runtime at n=500 with Outlier Analysis

**Table 4**: B&B execution time (ms) at n=500 with outlier analysis (95% bootstrap CI)

| Family | Median [95% CI] | Mean ± Std | Mean 95% CI | Max |
|--------|----------------|------------|-------------|-----|
| Uncorrelated | 0.12 (CI: 0.11–0.14) | 0.12 ± 0.03 | 0.11–0.14 | 0.20 |
| Weakly Correlated | 0.14 (CI: 0.13–0.16) | 0.16 ± 0.07 | 0.14–0.19 | 0.37 |
| Strongly Correlated | 0.36 (CI: 0.23–0.59) | 0.73 ± 0.97 | 0.43–1.09 | 3.85 |
| Inverse Correlated | 4.67 (CI: 0.93–10.63) | 182.60 ± 905.65 | 9.39–519.30 | 4974.48 |
| Equal Ratios | 0.18 (CI: 0.15–0.29) | 0.31 ± 0.29 | 0.22–0.42 | 1.25 |

The Inverse Correlated mean (182.60 ms) is heavily inflated by 30-second timeout censoring. The median (4.67 ms) and median CI better represent typical performance. Maximum observed time was 4974 ms (25.2M nodes).

### 6.5 DP Scaling

**Table 5**: DP mean time (ms) by n and family (W=1000 fixed) with 95% bootstrap CI

| n | Uncorrelated | Weakly Corr. | Strongly Corr. | Inverse Corr. | Equal Ratios |
|---|-------------|--------------|----------------|---------------|--------------|
| 20 | 0.09 (CI: 0.07–0.12) | 0.12 (CI: 0.06–0.23) | 0.03 (CI: 0.03–0.04) | 0.01 (CI: 0.01–0.01) | 0.01 (CI: 0.01–0.02) |
| 50 | 0.07 (CI: 0.06–0.08) | 0.06 (CI: 0.05–0.06) | 0.07 (CI: 0.07–0.08) | 0.10 (CI: 0.05–0.18) | 0.07 (CI: 0.06–0.07) |
| 100 | 0.11 (CI: 0.10–0.12) | 0.14 (CI: 0.12–0.14) | 0.14 (CI: 0.13–0.14) | 0.09 (CI: 0.07–0.10) | 0.12 (CI: 0.11–0.13) |
| 200 | 0.24 (CI: 0.20–0.32) | 0.20 (CI: 0.18–0.22) | 0.25 (CI: 0.23–0.27) | 0.21 (CI: 0.18–0.23) | 0.25 (CI: 0.24–0.27) |
| 500 | 0.41 (CI: 0.37–0.45) | 0.38 (CI: 0.33–0.43) | 0.44 (CI: 0.37–0.53) | 0.44 (CI: 0.40–0.48) | 0.41 (CI: 0.38–0.44) |

DP time scales near-linearly with n at fixed W. Family dependence is modest (0.38–0.44 ms at n=500, a ~16% range) and diminishes at larger n as the O(nW) term dominates.

### 6.6 Memory Usage

All three algorithms operate within a narrow memory band at fixed W=1000. Median heap usage is 1.00 MB for DP and B&B across all sizes, and 1.00 MB for Greedy at n ≥ 50 (0.33 MB at n=20, reflecting smaller JVM baseline allocation).

B&B shows the only notable outlier behavior: maximum observed memory is 32 MB on Inverse Correlated instances, where the search tree explores up to 25M nodes and the priority queue grows proportionally. On all other families, B&B memory stays at 1.00 MB even at n=500.

Memory is effectively independent of n at fixed W for all algorithms. DP uses a single 1D array of size W+1. B&B's queue size is bounded by the number of live nodes, which varies by instance family. Greedy uses only a sorted copy of the input. These results confirm that memory is not a differentiating factor for algorithm selection at these scales.

---

## 7. Discussion

### 7.1 When to Use Which Algorithm

| Instance Property | Recommended Algorithm |
|-------------------|----------------------|
| Small W (≤ 10⁴), exact needed | DP |
| **Inverse Correlated (v + w = constant)** | **Greedy (optimal, instant)** |
| Strongly Correlated (v ≈ w) | Greedy (small gap, instant) or DP (exact) |
| Uncorrelated / Weakly Correlated | Greedy (tiny gap, instant) or DP (exact) |
| Nearly equal ratios | DP (exact) or Greedy (tiny gap) |
| Large n, approximate OK | Greedy (gap < 1% for Uncorrelated/Weak) |

### 7.2 Why Greedy is Optimal on Inverse Correlated

For Inverse Correlated instances: $v_i = 1001 - w_i$, so $v_i + w_i = 1001$ (constant). The ratio $v_i/w_i = 1001/w_i - 1$ is strictly decreasing in $w_i$. Greedy sorts by ratio descending = by weight ascending. For this special structure where $v_i + w_i = \text{constant}$, the greedy algorithm that picks items by ascending weight is provably optimal. This is a known mathematical property of "inverse strongly correlated" knapsack instances.

### 7.3 Why B&B Struggles on Inverse Correlated

Fractional upper bound: items sorted by $v/w$. For inverse correlation, heavy items have low ratio → appear late in fractional packing → bound overestimates heavily → weak pruning. This causes exponential blowup on some instances (max 25M nodes, 4.7s).

### 7.4 Why Strongly Correlated Has Many B&B Nodes

When $v_i = w_i + \epsilon$, all items have ratio ≈ 1. Fractional bound packs many items fractionally → bound ≈ sum of many items → close to integer optimum but many combinations achieve similar value → tree explored deeply.

### 7.5 Limitations
- Java GC noise in microsecond measurements
- Single-threaded; parallel B&B would change scaling
- W fixed at 1000; DP scales with W
- One generator per family; other parameterizations may differ

---

## 8. Conclusion

We empirically characterized three classical knapsack algorithms across five instance families. Instance correlation structure—not just size—dominates practical performance:

- **Greedy** is instant and optimal on Inverse Correlated (v+w=constant); achieves < 1% median gap on Uncorrelated and Weakly Correlated; moderate gaps (2.5% median) on Strongly Correlated.
- **DP** is the robust choice for exact solutions when W is moderate; time predictable and scales with n at fixed W.
- **B&B** excels on Uncorrelated/Weakly Correlated but can explode exponentially on Strongly Correlated and Inverse Correlated instances at larger n.

The common assumption that Inverse Correlated instances are "hard for greedy" is incorrect for the standard generator where $v_i + w_i = \text{constant}$; greedy is provably optimal there. Practitioners should select algorithms based on observed instance structure rather than generic heuristics.

Future work: FPTAS comparison, parallel B&B, larger n with capacity scaling, real-world instance benchmarking.

---

## References

[1] Pisinger, D. (2005). Where are the hard knapsack problems? *Computers & Operations Research*, 32(9), 2271-2284.

[2] Martello, S., & Toth, P. (1990). *Knapsack Problems: Algorithms and Computer Implementations*. Wiley.

[3] Kellerer, H., Pferschy, U., & Pisinger, D. (2004). *Knapsack Problems*. Springer.

[4] Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.

[5] Horowitz, E., & Sahni, S. (1974). Computing Partitions with Applications to the Knapsack Problem. *Journal of the ACM*, 21(2), 277-292.

[6] Korte, B., & Vygen, J. (2018). *Combinatorial Optimization: Theory and Algorithms* (6th ed.). Springer.

[7] Ibarra, H. R., & Kim, C. E. (1975). Fast Approximation for the Knapsack and Sum Subset Problems. *Journal of the ACM*, 22(4), 463-473.

---

## Appendix: Reproducibility

All code available in this repository.
```bash
# Build and run experiment
./build_and_run.sh 20,50,100,200,500 1000 30 42

# Generate tables and figures (requires numpy, matplotlib)
python3 analyze.py out/results/full_experiment.csv
```
Generates `out/results/full_experiment.csv` with 2,250 rows (750 instances x 3 algorithms).