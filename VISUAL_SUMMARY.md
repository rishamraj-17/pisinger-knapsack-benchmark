# Quick Visual Summary (ASCII Dashboard)

## Execution Time at n=500 (ms)

```
Algorithm          Uncorr    WeakCorr  StrongCorr InverseCorr EqualRatio
Greedy             ████ 0.12 ████ 0.24 ████ 0.26  ████ 0.23  ████ 0.20
DP                 ██████ 0.35 ██████ 0.33 ██████ 0.36 ██████ 0.29 ██████ 0.34
B&B                ████ 0.10 ████ 0.12 ██████ 0.45 ████████████████ 3.41 ████ 0.14
```

## Greedy Optimality Gap (%) - Median

```
Uncorrelated      ████████████████████████████████████████  58.6%
WeaklyCorrelated  ██████████████████████████████           27.1%
StronglyCorrelated ██████████████████                       12.8%
InverseCorrelated █████████████████████████████████████████ 60.8%
AlmostEqualRatios █████                                    5.3%
```

## B&B Nodes Explored (log scale, median)

```
Uncorrelated      ████  34
WeaklyCorrelated  ██████  87
StronglyCorrelated ████████████████████████████████████████████ 376
InverseCorrelated ████  31
AlmostEqualRatios ████████ 100
```

## Key Takeaways

| Situation | Best Algorithm | Why |
|-----------|---------------|-----|
| Need exact, W small | **DP** | Predictable, always optimal |
| Strongly Correlated (v≈w) | **Greedy** | Near-optimal, instant |
| Uncorrelated/Weak | **B&B** | Fast, exact, few nodes |
| Inverse Correlated | **Avoid Greedy** | Gap > 60% |
| Large n, approximate OK | **Greedy** (not Inverse) | O(n log n) |

## Paper-Ready Tables

Run when you have Python packages:
```bash
python3 visualize.py out/results/full_experiment_*.csv
```

Creates:
- `figures/time_vs_n.png` - 5 panel log-log plot
- `figures/greedy_gap.png` - Gap boxplot by family
- `figures/bb_nodes.png` - B&B nodes boxplot (log)
- `figures/time_n500.png` - Grouped bar chart at n=500
- `figures/gap_vs_n.png` - Gap vs n lines by family
- `figures/memory_n500.png` - Memory grouped bars
- `tables/*.tex` - LaTeX tables for paper