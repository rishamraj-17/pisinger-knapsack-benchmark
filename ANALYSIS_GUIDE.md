# Analysis Guide for Knapsack Empirical Comparison

## Key Graphs for Your Paper

### 1. **Runtime vs n (log scale) — Figure 1**
- **X**: n ∈ {20, 50, 100, 200, 500}
- **Y**: mean time (ms), log scale, error bars = std over 30 seeds
- **Lines**: 3 algorithms × 4 dataset families = 12 lines per subplot (or 4 subplots, one per family)
- **Expected**: Greedy flat (O(n log n)), DP linear in n (O(nW)), B&B varies by family

### 2. **Greedy Optimality Gap by Family — Figure 2**
- **Box plot** of `(opt - greedy) / opt` per dataset family
- **Expected**: 
  - Uncorrelated: ~5-15% gap
  - WeaklyCorrelated: ~10-20% gap
  - StronglyCorrelated: ~0-5% gap (greedy nearly optimal)
  - InverseCorrelated: ~20-50% gap (greedy terrible)
  - AlmostEqualRatios: high variance, depends on tie-breaking

### 3. **B&B Nodes Explored — Figure 3**
- **Box plot** (log Y) of `nodes_explored` per family
- **Expected**: 
  - StronglyCorrelated: few nodes (bound tight)
  - InverseCorrelated: few nodes (bound tight)
  - Uncorrelated: many nodes
  - AlmostEqualRatios: many nodes (weak bounds)

### 4. **DP Time vs Capacity — Figure 4**
- Scatter plot: capacity (W) vs DP time (log-log)
- **Slope ≈ 1** confirms O(nW) pseudo-polynomial
- Color by family

### 5. **Tables for Paper**
| Algorithm | Uncorrelated | WeaklyCorr | StronglyCorr | InverseCorr | EqualRatios |
|-----------|-------------|------------|--------------|-------------|-------------|
| Greedy time (ms) | | | | | |
| DP time (ms) | | | | | |
| B&B time (ms) | | | | | |
| Greedy gap (%) | | | | | |
| B&B nodes | | | | | |

---

## Statistical Rigor
- **30 seeds per (n, W, family)** → report mean ± std
- **Timeout handling**: Exclude timed-out runs or cap at timeout
- **Warmup**: 3 runs discarded before measurement (JIT)
- **Memory**: Report peak RSS (MB), not just heap

---

## Expected Findings (Hypotheses to Test)
1. **Greedy fails on InverseCorrelated** — value inversely related to weight
2. **Greedy near-optimal on StronglyCorrelated** — v ≈ w + small noise
3. **DP scales with W, not n** — pseudo-polynomial confirmed
4. **B&B fast on correlated** — fractional bound tight when v/w varies
5. **B&B struggles on EqualRatios** — bound weak when ratios identical

---

## Running Analysis
```bash
cd /home/risham-raj-byahut/IdeaProjects/Emperical_Comparision
pip install pandas matplotlib seaborn
python3 scripts/analyze.py out/results/benchmark_*.csv
```

---

## Phase 8: Paper Structure (ACM sigconf)

### 1. Abstract (150 words)
Problem, methods, key finding, implication.

### 2. Introduction
- 0/1 Knapsack: fundamental combinatorial optimization
- Three classical algorithms with different complexity profiles
- Research question: *How do instance characteristics affect practical performance?*
- Contributions: (1) systematic empirical study across 4 families, (2) runtime/gap/space tradeoffs quantified, (3) practical guidance for algorithm selection

### 3. Related Work
- Pisinger (2005) "Where are the hard knapsack problems?"
- Martello & Toth (1990) — classic textbook
- Recent empirical studies (cite 2-3)

### 4. Algorithms
- **Greedy**: pseudocode, O(n log n), optimality gap discussion
- **DP**: recurrence `dp[w] = max(dp[w], dp[w-w_i] + v_i)`, O(nW) time/space, pseudo-polynomial
- **Branch & Bound**: search tree, fractional upper bound, best-first with priority queue, pruning rule

### 5. Experimental Design
- Instance families (definitions with formulas)
- Parameters: n, W/Σw ratio, 30 seeds each
- Metrics: time, memory, gap, nodes
- Environment: Java 21, warmup, timeout

### 6. Results
- Figures 1-4 with analysis
- Tables
- Statistical significance notes

### 7. Discussion
- Why greedy fails on inverse correlated
- Why B&B explores fewer nodes on correlated
- Practical recommendations: "Use Greedy for StronglyCorrelated, DP for small W, B&B for medium n/correlated"

### 8. Conclusion + Future Work
- Summary
- Limitations (Java overhead, single-threaded)
- Extensions: FPTAS, parallel B&B, larger n

---

## LaTeX Template (sigconf)
```latex
\documentclass[sigconf]{acmart}
\usepackage{booktabs,pgfplots,subcaption}
\begin{document}
\title{Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics}
\author{Your Name}
\affiliation{\institution{Your University}}
\begin{abstract}...\end{abstract}
\keywords{knapsack, empirical analysis, greedy, dynamic programming, branch and bound}
\maketitle
...
\bibliographystyle{ACM-Reference-Format}
\bibliography{references}
\end{document}
```

---

## Next Steps
1. Run full benchmark: `./build_and_run.sh 20 1000 30 42` then `50`, `100`, `200`, `500`
2. Run analysis script
3. Write paper using structure above