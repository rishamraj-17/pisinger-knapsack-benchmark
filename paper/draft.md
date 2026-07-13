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

**Greedy runtime analysis.** Greedy execution is dominated by sorting the items by $v_i/w_i$, which contributes O(n log n) to the total cost. The subsequent greedy selection pass is O(n) and executes in constant time per item (a single comparison and conditional pack). The observed 3.3x variation across families (0.10–0.33 ms) reflects a secondary effect: families where $v_i/w_i$ ratios are well-separated (Inverse Correlated, Equal Ratios) produce fewer comparison swaps in the sort, while families with clustered ratios (Weakly Correlated) require more comparisons. At n=500, sorting accounts for over 90% of total runtime; the family-dependent variation is noise at the sort level, not in the greedy selection itself.

**DP runtime analysis.** DP executes exactly nW = 500,000 inner-loop iterations regardless of instance family. Each iteration performs a single comparison and a conditional addition. The observed 0.38–0.44 ms range (a 16% variation) is explained by branch prediction behavior: families where many items have weight $w_i > W$ (Inverse Correlated produces heavy items with low value) cause the `if (w >= w_i)` branch to fail more often, reducing memory accesses. Families where items are more uniformly distributed across weight ranges (Uncorrelated) produce more balanced branch prediction. The dominant O(nW) work is constant across families; the modest variation is a microarchitectural artifact, not an algorithmic difference.

**B&B runtime analysis.** B&B runtime varies by three orders of magnitude (0.12 ms to 182.60 ms mean) because the number of nodes explored depends on bound tightness, which is determined by instance structure. On Uncorrelated instances, the fractional knapsack upper bound is tight (the LP relaxation closely approximates the integer optimum), so few nodes are pruned and the search terminates quickly. On Inverse Correlated instances, the bound is extremely loose (see Section 7.3), causing exponential tree expansion. The extreme variance on Inverse Correlated (std 905.65 ms) arises from timeout censoring: 30s-capped runs inflate the mean while the median (4.67 ms) better represents typical behavior.

**Figure 1** (time vs n): DP shows the most predictable scaling — a straight line on the log-log plot consistent with O(n) at fixed W. Greedy scales similarly but with more variance at small n (JVM warmup dominates below n=50). B&B scaling is family-dependent: near-linear on Uncorrelated, superlinear on Strongly Correlated, and unpredictable on Inverse Correlated where timeout-censored runs create a floor effect.

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

**Why gap depends on correlation structure.** The greedy algorithm sorts by $v_i/w_i$ descending and packs items in that order until capacity is exhausted. The optimality gap arises when this locally optimal sequence fails to find the globally optimal subset. The gap magnitude is directly determined by how well the ratio $v_i/w_i$ correlates with an item's true contribution to the optimal solution.

- **Inverse Correlated** ($v_i + w_i = 1000$): The ratio $v_i/w_i = (1000 - w_i)/w_i$ is strictly decreasing in $w_i$. Greedy sorts by ascending weight, which is provably optimal for this structure: lighter items always have higher ratio *and* higher value per unit weight. There is no conflict between the local ratio criterion and the global optimum, so the gap is exactly 0% at all sizes.

- **Strongly Correlated** ($v_i \approx w_i$): All items have ratio $\approx 1$. The greedy criterion provides almost no discrimination between items — the sort order is nearly arbitrary, and the final item selected (which determines which items are excluded) is effectively random. This near-random selection explains the high gap (2.5% median, 10.8% at n=20) and the large variance (std 6.3%). As n increases, the law of large numbers causes the randomly excluded items to average out, reducing the gap to 0.7% at n=500.

- **Uncorrelated/Weakly Correlated**: Ratios are well-separated, so the sort order reliably identifies high-value items. Small gaps arise from boundary effects — the last item may not fit, leaving residual capacity that could be better utilized by a different combination. The gap decreases with n because the residual capacity becomes a smaller fraction of the total value.

- **Equal Ratios**: Nearly identical ratios create arbitrary tie-breaking. At small n, a single unlucky tie-break can cause significant gap (2.0% at n=20). At large n, tie-breaking effects average out across many items.

**The gap-n relationship.** The gap decreases monotonically with n for all families except Inverse Correlated (where it is always 0). This pattern arises because larger instances produce higher total optimal value, making the fixed-size boundary error (the last item that doesn't fit) a smaller relative fraction. For Strongly Correlated, the gap decreases most steeply (10.8% → 0.7%) because the ratio criterion improves as the sample size increases — with more items, the sort order becomes a better approximation of the optimal selection.

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

**Why bound tightness varies by family.** B&B explores nodes in a best-first search tree. At each node, it computes a fractional knapsack upper bound: items are sorted by $v_i/w_i$ and packed fractionally until capacity is exhausted. A node is pruned when its bound $\leq$ the best integer solution found. The number of nodes explored is determined by the *gap* between the fractional bound and the integer optimum — a tighter gap means more pruning and fewer nodes.

- **Uncorrelated** (138 median nodes): Items have independent $v_i$ and $w_i$, producing well-separated ratios. The fractional bound tightly approximates the integer optimum because the fractional "leftover" item (the one packed partially) contributes negligibly to the bound overcount. With a tight bound, most of the search tree is pruned immediately, leaving only a small backbone of nodes near the optimal solution.

- **Strongly Correlated** (1,032 median nodes): When $v_i = w_i + \epsilon$, all items have ratio $\approx 1 + \epsilon/w_i \approx 1$. The fractional bound packs items greedily by weight, but since all ratios are nearly equal, the bound value is approximately $\sum v_i \cdot (W/w_{\text{avg}})$, which substantially overestimates the integer optimum. The resulting gap is large, causing the algorithm to explore many branches that could contain a better integer solution. This explains the 7.5x increase in nodes over Uncorrelated.

- **Inverse Correlated** (562 median pooled, 46,244 at n=500): This family has the most extreme bound degradation. Items satisfy $v_i + w_i = 1001$, so $v_i/w_i = 1001/w_i - 1$ is strictly decreasing in $w_i$. Heavy items have very low ratio and are packed last in the fractional solution, but they consume disproportionate capacity. The fractional bound packs many light (high-ratio) items fractionally, producing a bound that vastly overestimates the achievable integer value. The bound-gap-to-optimum ratio grows with n, explaining the superlinear node growth: from 38 nodes at n=20 to 46,244 at n=500 (a 1,217x increase for a 25x increase in n). The worst-case instances reach 25M nodes because the bound provides almost no pruning signal.

- **Equal Ratios** (291 median nodes): Nearly identical ratios create degenerate fractional solutions where many items can be swapped without changing the bound value. The bound is moderately loose — not as bad as Strongly Correlated (where ratios are exactly equal) but worse than Uncorrelated. The bound produces enough pruning to keep node counts manageable, but the degeneracy increases variance (max 10,139 nodes).

**Node growth rates.** The per-size data reveals distinct scaling regimes. Uncorrelated nodes grow sublinearly with n (28 → 582 over 25x n increase), suggesting the bound tightens as n increases — more items provide more opportunities for the fractional solution to approximate the integer optimum. Inverse Correlated nodes grow super-exponentially (38 → 46,244), consistent with the bound quality degrading as the ratio structure becomes more extreme with more items. Strongly Correlated shows intermediate growth (320 → 3,228, approximately $n^{1.2}$), reflecting persistent bound looseness that scales polynomially.

### 6.4 B&B Runtime at n=500 with Outlier Analysis

**Table 4**: B&B execution time (ms) at n=500 with outlier analysis (95% bootstrap CI)

| Family | Median [95% CI] | Mean ± Std | Mean 95% CI | Max |
|--------|----------------|------------|-------------|-----|
| Uncorrelated | 0.12 (CI: 0.11–0.14) | 0.12 ± 0.03 | 0.11–0.14 | 0.20 |
| Weakly Correlated | 0.14 (CI: 0.13–0.16) | 0.16 ± 0.07 | 0.14–0.19 | 0.37 |
| Strongly Correlated | 0.36 (CI: 0.23–0.59) | 0.73 ± 0.97 | 0.43–1.09 | 3.85 |
| Inverse Correlated | 4.67 (CI: 0.93–10.63) | 182.60 ± 905.65 | 9.39–519.30 | 4974.48 |
| Equal Ratios | 0.18 (CI: 0.15–0.29) | 0.31 ± 0.29 | 0.22–0.42 | 1.25 |

**Runtime-node correspondence.** The runtime hierarchy (Uncorrelated < Weakly < Equal Ratios < Strongly < Inverse Correlated) mirrors the node count hierarchy (Table 3), confirming that search tree size — not per-node overhead — dominates B&B runtime. Each node requires one fractional knapsack computation (O(n log n) for sorting, though items can be pre-sorted once) and one heap insertion/extraction (O(log |queue|)). At n=500, the per-node cost is dominated by the fractional packing, which involves iterating through remaining items. The 0.12 ms median on Uncorrelated (138 nodes) implies approximately 0.87 μs per node, while the 4.67 ms median on Inverse Correlated (46,244 nodes) implies approximately 0.10 μs per node — the per-node cost is lower on Inverse Correlated because the bound is computed fewer times before pruning, and the priority queue operations dominate.

**Timeout censoring effects.** The Inverse Correlated mean (182.60 ms) is inflated by right-censored observations: runs that hit the 30s timeout are recorded at their final time (up to 4974 ms) with their node count capped at 25M. The true mean (if no timeout existed) would be substantially higher. The median CI (0.93–10.63 ms) better represents typical performance: most Inverse Correlated instances solve quickly, but a heavy-tailed minority requires orders of magnitude more work. This heavy tail is characteristic of B&B on instances with degenerate bound structure — a small change in item weights can shift the fractional bound from tight to extremely loose.

### 6.5 DP Scaling

**Table 5**: DP mean time (ms) by n and family (W=1000 fixed) with 95% bootstrap CI

| n | Uncorrelated | Weakly Corr. | Strongly Corr. | Inverse Corr. | Equal Ratios |
|---|-------------|--------------|----------------|---------------|--------------|
| 20 | 0.09 (CI: 0.07–0.12) | 0.12 (CI: 0.06–0.23) | 0.03 (CI: 0.03–0.04) | 0.01 (CI: 0.01–0.01) | 0.01 (CI: 0.01–0.02) |
| 50 | 0.07 (CI: 0.06–0.08) | 0.06 (CI: 0.05–0.06) | 0.07 (CI: 0.07–0.08) | 0.10 (CI: 0.05–0.18) | 0.07 (CI: 0.06–0.07) |
| 100 | 0.11 (CI: 0.10–0.12) | 0.14 (CI: 0.12–0.14) | 0.14 (CI: 0.13–0.14) | 0.09 (CI: 0.07–0.10) | 0.12 (CI: 0.11–0.13) |
| 200 | 0.24 (CI: 0.20–0.32) | 0.20 (CI: 0.18–0.22) | 0.25 (CI: 0.23–0.27) | 0.21 (CI: 0.18–0.23) | 0.25 (CI: 0.24–0.27) |
| 500 | 0.41 (CI: 0.37–0.45) | 0.38 (CI: 0.33–0.43) | 0.44 (CI: 0.37–0.53) | 0.44 (CI: 0.40–0.48) | 0.41 (CI: 0.38–0.44) |

**Why DP runtime is linear in n at fixed W.** The DP recurrence processes each of the n items by iterating over W capacity values, performing one comparison and one conditional addition per cell. With W=1000 fixed, the total work per item is a constant 1000 operations, making the effective complexity O(n) in this experimental setting. The theoretical O(nW) complexity manifests only when W varies; here, the W-dependent term is absorbed into the constant factor. This explains why DP shows near-perfect linear scaling with n (0.05 ms at n=20 to 0.42 ms at n=500, an 8.4x increase for a 25x increase in n, consistent with linear scaling plus constant overhead).

**Why family dependence is modest.** The DP inner loop performs the same operations regardless of item values — the comparison `dp[w] < dp[w-w_i] + v_i` and the conditional update execute in constant time per cell. Instance family affects only the *branch taken* (update vs. no-update), which has negligible impact on modern superscalar processors with branch prediction. The observed 16% variation across families at n=500 (0.38–0.44 ms) is within the noise range of JVM garbage collection timing and CPU frequency scaling, not a statistically meaningful algorithmic difference. This confirms that DP's runtime is determined by the product nW, not by instance structure.

**The n=20 anomaly.** At n=20, DP times vary from 0.01 ms (Inverse Correlated) to 0.12 ms (Weakly Correlated) — a 12x range. This is not algorithmic: at n=20, the DP loop executes only 20,000 iterations, which completes in microseconds. The measured time is dominated by JVM startup overhead, method invocation, and memory allocation, which vary randomly across runs. The tight CIs at n=500 (width ~0.08 ms) versus the wide CIs at n=20 (width ~0.16 ms) confirm that measurement noise exceeds the signal at small n.

### 6.6 Memory Usage

All three algorithms operate within a narrow memory band at fixed W=1000. Median heap usage is 1.00 MB for DP and B&B across all sizes, and 1.00 MB for Greedy at n ≥ 50 (0.33 MB at n=20, reflecting smaller JVM baseline allocation).

B&B shows the only notable outlier behavior: maximum observed memory is 32 MB on Inverse Correlated instances, where the search tree explores up to 25M nodes and the priority queue grows proportionally. On all other families, B&B memory stays at 1.00 MB even at n=500.

Memory is effectively independent of n at fixed W for all algorithms. DP uses a single 1D array of size W+1. B&B's queue size is bounded by the number of live nodes, which varies by instance family. Greedy uses only a sorted copy of the input. These results confirm that memory is not a differentiating factor for algorithm selection at these scales.

### 6.7 Scaling-Rate Analysis

We estimate empirical growth rates from the median measurements (Tables 1, 3, 5) and compare them against theoretical complexity predictions.

**DP: theoretical O(nW), observed O(n).** With W=1000 fixed, the theoretical complexity predicts linear scaling in n. The observed mean times (n=20: 0.053 ms, n=500: 0.417 ms) yield an empirical ratio of 7.9x for a 25x increase in n, corresponding to a fitted exponent of approximately 0.85 on a log-log plot. The sub-unit exponent (0.85 < 1.0) reflects constant overhead amortization: JVM method dispatch and memory allocation contribute a fixed cost that becomes proportionally smaller at larger n. This is consistent with O(n) scaling plus O(1) overhead, confirming the theoretical prediction.

**Greedy: theoretical O(n log n), observed approximately O(n).** Mean times scale from 0.028 ms (n=20) to 0.216 ms (n=500), an 7.7x increase for 25x n — fitted exponent approximately 0.83. The log n factor (log 500 / log 20 ≈ 1.6) would predict a 12.3x increase if scaling were O(n log n) exactly. The observed 7.7x suggests that at these scales, the n term dominates and the log n contribution is within measurement noise. Sorting accounts for the majority of runtime; the greedy selection pass is O(n) and negligible.

**B&B: family-dependent scaling.** B&B exhibits three distinct scaling regimes:

| Family | Nodes at n=20 | Nodes at n=500 | Growth ratio | Fitted exponent |
|--------|--------------|----------------|--------------|-----------------|
| Uncorrelated | 28 | 582 | 20.8x | ~0.83 (sublinear) |
| Strongly Correlated | 320 | 3,228 | 10.1x | ~0.71 (sublinear) |
| Inverse Correlated | 38 | 46,244 | 1,217x | ~1.95 (superlinear) |

Uncorrelated and Strongly Correlated show sublinear node growth (exponent < 1), meaning the fractional bound tightens as n increases — more items provide more fractional packing options, improving the LP relaxation. Inverse Correlated shows superlinear growth (exponent ≈ 2), meaning the bound degrades faster than the problem grows. This is the defining characteristic of "hard" knapsack instances: the LP relaxation becomes a progressively worse approximation of the integer optimum as the instance scales.

**Comparison with theory.** The theoretical worst case for B&B is exponential O(2^n), but on "easy" families (Uncorrelated, Weakly Correlated), the observed growth is sublinear — far better than the worst case. This confirms that B&B's practical performance is determined by instance structure, not asymptotic bounds. The Inverse Correlated family approaches exponential growth at n=500, suggesting that at larger n, it would hit the worst-case regime. DP's observed O(n) at fixed W matches theory exactly. Greedy's observed O(n) is consistent with O(n log n) at these scales, where the log factor is not yet distinguishable from noise.

---

## 7. Discussion

### 7.1 When to Use Which Algorithm

The experimental results yield scenario-specific algorithm recommendations:

**Real-time systems (latency-critical).** Greedy is the only viable choice. Its execution time is sub-millisecond and deterministic — no timeouts, no variance spikes. On Inverse Correlated instances, Greedy is also provably optimal, eliminating the approximation-vs-exact tradeoff entirely.

**Embedded devices (memory-constrained).** All three algorithms fit within 1–2 MB at these scales, but Greedy uses the least memory (no DP array, no priority queue). For W > 10⁴, DP's O(W) memory becomes prohibitive; Greedy's O(n) memory is independent of W.

**Exact optimization (guaranteed optimal).** DP is the reliable choice when W ≤ 10⁴. Its runtime is predictable (linear in n, independent of instance family), and it never times out at these scales. B&B should be preferred over DP only when instance structure is known to be favorable (Uncorrelated or Weakly Correlated), where B&B can be 2–3x faster than DP.

**Offline planning (batch processing).** DP provides the best cost-performance ratio: exact solutions with predictable runtime. For large batches, the linear scaling of DP means throughput degrades gracefully with n, while B&B's unpredictable variance on some families creates scheduling difficulties.

**Moderate-size instances (n ≤ 500, W ≤ 1000).** All three algorithms complete in under 1 ms (except B&B on Inverse Correlated). Greedy is sufficient when gaps < 1% are acceptable; DP is preferred when exact solutions are required.

**Unknown instance structure.** DP is the safest default — it provides exact solutions with runtime independent of instance family. Greedy is a fast pre-solver: compute the greedy solution first, then decide whether to invoke DP based on the observed gap and the required precision.

### 7.2 Why Greedy is Optimal on Inverse Correlated

The optimality of Greedy on Inverse Correlated instances is a mathematical consequence of the value-weight structure, not an empirical coincidence. When $v_i + w_i = C$ (constant), the ratio $v_i/w_i = C/w_i - 1$ is strictly decreasing in $w_i$. Greedy sorts by ratio descending, which is equivalent to sorting by weight ascending. For this specific structure, selecting items in ascending weight order always produces an optimal packing: lighter items have both higher ratio *and* higher value density, so there is no conflict between the local greedy criterion and the global optimum. This is a known result in the knapsack literature [2, 3], but our experiments confirm it empirically at all tested scales (n = 20 to 500, 30 seeds per configuration).

The practical implication is significant: practitioners who can identify inverse correlation in their data (e.g., items where value and weight are complementary) can use Greedy with confidence that the solution is optimal — achieving O(n log n) performance with zero quality loss.

### 7.3 Why B&B Struggles on Inverse Correlated

The fractional knapsack upper bound computes the maximum achievable value by packing items greedily by $v_i/w_i$ and allowing fractional inclusion of the last item. This bound is tight when the fractional "leftover" item contributes negligibly to the bound overcount — i.e., when the gap between the fractional and integer optimum is small.

On Inverse Correlated instances, the bound degrades through a specific mechanism:

1. Heavy items (high $w_i$) have very low $v_i/w_i$ ratios. In the fractional solution, they are packed last (or not at all).
2. Light items (low $w_i$) have very high ratios. They are packed first, consuming capacity quickly.
3. The fractional solution packs many light items fractionally, achieving a bound value that substantially exceeds what any integer packing can achieve.
4. The resulting bound gap (fractional optimum minus integer optimum) is large, so the algorithm cannot prune branches that might contain better integer solutions.

This mechanism explains the observed node growth: from 38 nodes at n=20 to 46,244 at n=500 (a 1,217x increase). As n increases, the number of light items grows, the fractional solution becomes increasingly optimistic, and the bound provides progressively less pruning signal. The worst-case instances reach 25M nodes because the bound essentially fails — every branch of the search tree has a bound exceeding the best integer solution, so nothing is pruned until the optimal solution is found by exhaustive enumeration.

### 7.4 Why Strongly Correlated Has Many B&B Nodes

When $v_i = w_i + \epsilon$, all items have ratio $v_i/w_i = 1 + \epsilon/w_i \approx 1$. The fractional bound packs items by weight (since all ratios are approximately equal), but the key problem is that the bound value is approximately $\sum v_i \cdot (W/w_{\text{avg}})$, which overestimates the integer optimum because many items can only be included partially. The bound is not as loose as on Inverse Correlated instances (1,032 median nodes vs. 46,244 at n=500), but it is substantially looser than on Uncorrelated instances (138 nodes).

The node count is intermediate (1,032 pooled median) because the bound degradation is uniform across items — every item has ratio ≈ 1, so the bound is consistently slightly above the integer optimum. This creates a "deep but narrow" search tree: many branches need to be explored, but each branch is pruned relatively quickly once a slightly better integer solution is found. The polynomial node growth ($n^{1.2}$) confirms that the bound looseness scales predictably with n, unlike the exponential degradation on Inverse Correlated instances.

### 7.5 Limitations

This study has several scope constraints that should be considered when interpreting the results:

**Fixed capacity (W = 1000).** All experiments use W = 1000, which fixes the DP table size at 1,001 cells. DP's O(nW) complexity means that scaling W to 10⁴ or 10⁶ would increase runtime by 10–1000x, potentially changing the algorithm ranking. B&B's performance is less sensitive to W because its bound computation does not depend on W directly (the fractional knapsack subproblem is solved analytically). Future work should explore W scaling.

**Synthetic benchmark families.** The five Pisinger families represent canonical correlation structures, but real-world knapsack instances may exhibit混合 correlation patterns (e.g., partially correlated, multi-modal, or adversarially constructed). The family-specific recommendations in Section 7.1 assume that the instance type can be identified before algorithm selection.

**Single-threaded implementation.** All algorithms run on a single thread. Parallel B&B (e.g., spatial decomposition of the search tree) would significantly improve B&B performance on hard instances, potentially changing the relative ranking on Inverse Correlated and Strongly Correlated families.

**Java implementation.** The benchmark is implemented in Java 21, which introduces GC pauses, JIT compilation artifacts, and memory overhead not present in C/C++ implementations. The memory measurements (Section 6.6) reflect JVM heap usage rather than actual algorithm memory consumption. Runtime measurements are affected by JVM warmup, though the 3-run warmup protocol mitigates this.

**Absence of approximation schemes.** This study compares three classical algorithms but does not include FPTAS (Fully Polynomial-Time Approximation Scheme) or other modern approximation algorithms. FPTAS provides a $(1-\epsilon)$ approximation in $O(n^2/\epsilon)$ time, which may be preferable to DP for large W.

**Absence of parallel B&B.** The B&B implementation is sequential. State-of-the-art B&B solvers use parallel search, strong branching, and cutting planes that would substantially change the performance profile on hard instances.

**Benchmark size limitations.** The maximum n = 500 is small by modern standards. At n = 1000 or n = 10,000, B&B's exponential blowup on Inverse Correlated instances would be far more severe, and DP's linear scaling would make it the clear winner for exact solutions.

---

## 8. Conclusion

This study systematically compared three classical 0/1 knapsack algorithms — Greedy, Dynamic Programming, and Branch & Bound — across five Pisinger instance families, revealing that instance correlation structure, not problem size, is the primary determinant of practical algorithm performance.

**Key algorithmic findings.** Greedy achieves optimal solutions on Inverse Correlated instances (where $v_i + w_i = \text{constant}$) due to a structural property: the ratio criterion aligns perfectly with the global optimum when value and weight are complementary. On other families, Greedy's gap is determined by how well the $v_i/w_i$ ratio discriminates between items — Strongly Correlated instances produce the largest gaps (2.5% median) because all ratios are approximately equal, rendering the sort order nearly arbitrary. DP runtime is effectively linear in n at fixed W, with less than 16% variation across families, confirming that the O(nW) work dominates regardless of instance structure. B&B performance varies by three orders of magnitude across families, governed by the tightness of the fractional knapsack upper bound: tight bounds (Uncorrelated) yield fast pruning and sublinear node growth, while loose bounds (Inverse Correlated) produce exponential tree expansion.

**Practical algorithm selection.** The evidence supports the following decision framework:

- **For guaranteed optimal solutions:** Use DP when W ≤ 10⁴. Its runtime is predictable and independent of instance structure. For larger W, consider FPTAS or B&B with instance-aware configuration.
- **For real-time or embedded systems:** Use Greedy. Sub-millisecond execution, O(n) memory, and zero timeout risk. On Inverse Correlated data, Greedy is also optimal — no tradeoff required.
- **For batch processing of unknown instances:** Use DP as the default. If instance structure can be identified as Uncorrelated or Weakly Correlated, B&B may be 2–3x faster.
- **For large-scale problems (n > 500):** Avoid B&B unless instance structure is known to be favorable. DP's linear scaling provides reliable throughput; Greedy provides fast approximate solutions.

**Theoretical contribution.** The common assumption that Inverse Correlated instances are "hard for greedy" is incorrect for the standard Pisinger generator where $v_i + w_i = \text{constant}$. Greedy is provably optimal there, and our experiments confirm this at all tested scales (n = 20 to 500, 30 seeds per configuration). The actual difficulty of Inverse Correlated instances falls on B&B, where the same structural property that makes Greedy optimal also destroys the fractional upper bound's pruning power.

**Limitations and future work.** This study is bounded by fixed W = 1000, synthetic instances, single-threaded Java implementations, and n ≤ 500. Parallel B&B, FPTAS comparison, W-scaling analysis, and real-world instance benchmarking would extend these findings. The deterministic experimental pipeline (seed = 42 for all statistical computations) ensures full reproducibility.

---

## 9. Threats to Validity

Following Wohlin et al. [8], we categorize threats to the validity of this study.

**Internal validity.** The experimental pipeline is deterministic: instances are generated from seeded PRNGs (seed 42), algorithms execute single-threaded with a fixed warmup protocol (3 runs per instance), and all statistical computations use `random.seed(42)`. This eliminates run-to-run variability as a confounding factor. The 30-second timeout per instance-algorithm pair introduces right-censoring on B&B for Inverse Correlated instances; we mitigate this by reporting medians (robust to censoring) alongside means, and by analyzing the timeout effect explicitly in Section 6.4.

**Construct validity.** We measure wall-clock time (nanosecond precision via `System.nanoTime()`), heap memory (via `Runtime.getRuntime()`), solution value, and B&B node count. Wall-clock time captures the full cost including JVM overhead but may be affected by garbage collection pauses; the 3-run warmup reduces JIT compilation artifacts. Memory measurements reflect JVM heap usage rather than algorithmic memory complexity, which limits their interpretability (Section 6.6). The optimality gap is computed relative to DP solutions, which are exact by construction for the tested parameter ranges.

**External validity.** The five Pisinger families represent canonical correlation structures but do not exhaust the space of possible knapsack instances. Real-world instances may exhibit混合 correlation patterns, multi-modal weight distributions, or adversarial构造 that differ from the synthetic families studied here. The n ≤ 500 range is small by modern standards; scaling behavior at n = 1000+ may differ. Our Java 21 implementation on a single x64 Linux core represents one hardware/software configuration; results may differ on ARM, GPU, or other JVM implementations.

**Reliability.** All experimental data, analysis scripts, and figure generation code are publicly available. Running `./reproduce.sh` regenerates the complete experimental dataset (2,250 runs), LaTeX tables, and publication figures from scratch. The fixed random seed ensures that statistical computations (bootstrap CIs, median estimates) are reproducible across runs. The paper's numerical claims are derived exclusively from the generated tables — no values were hand-edited.

---

## References

[1] Pisinger, D. (2005). Where are the hard knapsack problems? *Computers & Operations Research*, 32(9), 2271-2284.

[2] Martello, S., & Toth, P. (1990). *Knapsack Problems: Algorithms and Computer Implementations*. Wiley.

[3] Kellerer, H., Pferschy, U., & Pisinger, D. (2004). *Knapsack Problems*. Springer.

[4] Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.

[5] Horowitz, E., & Sahni, S. (1974). Computing Partitions with Applications to the Knapsack Problem. *Journal of the ACM*, 21(2), 277-292.

[6] Korte, B., & Vygen, J. (2018). *Combinatorial Optimization: Theory and Algorithms* (6th ed.). Springer.

[7] Ibarra, H. R., & Kim, C. E. (1975). Fast Approximation for the Knapsack and Sum Subset Problems. *Journal of the ACM*, 22(4), 463-473.

[8] Wohlin, C., Runeson, P., Host, M., Ohlsson, M. C., Regnell, B., & Wesslen, A. (2012). *Experimentation in Software Engineering*. Springer.

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