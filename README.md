# Knapsack Optimization: Empirical Comparison

An experimental study comparing three classical 0/1 knapsack algorithms across five instance families, with analysis of how instance correlation structure affects practical performance.

## Motivation

The 0/1 Knapsack Problem is a foundational problem in combinatorial optimization. While the theoretical complexity of standard algorithms is well understood, their *practical* behavior under different instance characteristics is less systematically documented. This study fills that gap with a controlled, reproducible empirical comparison.

## Algorithms

| Algorithm | Time Complexity | Space | Optimal? |
|-----------|----------------|-------|----------|
| **Greedy** (value/weight ratio) | O(n log n) | O(n) | No |
| **Dynamic Programming** | O(nW) | O(W) | Yes |
| **Branch & Bound** | Exponential (worst) | O(n) | Yes |

## Instance Families

Following Pisinger (2005), five correlation structures:

| Family | Construction | Character |
|--------|-------------|-----------|
| Uncorrelated | `w ~ U(1,1000)`, `v ~ U(1,1000)` | No structure |
| Weakly Correlated | `w ~ U(1,1000)`, `v = w + U(-100,100)` | Mild correlation |
| Strongly Correlated | `w ~ U(1,1000)`, `v = w + U(1,10)` | Values close to weights |
| Inverse Correlated | `w ~ U(1,1000)`, `v = 1001 - w` | Heavy items have low value |
| Almost Equal Ratios | `w ~ U(1,1000)`, `v ~ w * 1.0 * (1 + U(-0.1,0.1))` | Near-identical ratios |

Parameters: n in {20, 50, 100, 200, 500}, W = 1000, 30 random seeds per (n, family).
Total: 750 instances, 2,250 algorithm runs.

## Repository Structure

```
.
├── src/main/java/          # Java source code
│   ├── Main.java           # Experiment entry point
│   ├── algorithms/         # Greedy, DynamicProgramming, BranchAndBound
│   ├── dataset/            # Five instance generators (Pisinger families)
│   ├── benchmark/          # BenchmarkRunner, ResultsExporter
│   └── model/              # Item, KnapsackInstance, Result
├── paper/draft.md          # Research paper (Markdown)
├── tables/                 # Generated LaTeX tables (do not edit manually)
├── figures/                # Generated figures (PDF, PNG, SVG)
├── out/results/            # Canonical experimental data (full_experiment.csv)
├── analyze.py              # Analysis pipeline (Python stdlib only)
├── figures.py              # Publication figure generation
├── plot_utils.py           # Shared plotting utilities
├── build_and_run.sh        # Build and run experiment
├── reproduce.sh            # Full reproduction pipeline
├── pom.xml                 # Maven build configuration
└── lib/                    # commons-csv dependency (auto-downloaded)
```

## Prerequisites

- **Java 17+** (OpenJDK or Oracle JDK)
- **Python 3.8+** (standard library only; no pip packages required)

## Quick Start

```bash
# Full reproduction: experiment + analysis (~2 minutes)
./reproduce.sh
```

This runs the complete pipeline and produces all outputs listed below.

## Reproducing Step by Step

```bash
# 1. Build and run the experiment (generates 2,250 rows)
./build_and_run.sh 20,50,100,200,500 1000 30 42

# 2. Generate LaTeX tables and publication figures
python3 analyze.py out/results/full_experiment.csv
```

### Custom Parameters

```bash
# Smaller run for testing (~10 seconds)
./build_and_run.sh 20,50 1000 5 42

# Different capacity and seed
./build_and_run.sh 20,50,100 2000 10 99
```

## Generated Outputs

| File | Description |
|------|-------------|
| `out/results/full_experiment.csv` | Raw data (2,250 rows: algorithm, family, n, time, memory, solution, nodes) |
| `tables/table_time_n500.tex` | Mean execution time at n=500 with 95% bootstrap CI |
| `tables/table_greedy_gap.tex` | Greedy optimality gap statistics |
| `tables/table_bb_nodes.tex` | Branch & Bound nodes explored |
| `tables/table_bb_time_n500.tex` | B&B runtime at n=500 with outlier analysis |
| `tables/table_dp_scaling.tex` | DP runtime scaling with n |
| `tables/table_full_summary.csv` | Complete summary (all n, algorithms, families) |
| `figures/runtime_vs_n.pdf` | Runtime vs. problem size by algorithm |
| `figures/greedy_gap_boxplot.pdf` | Greedy optimality gap distribution |
| `figures/bb_nodes_boxplot.pdf` | B&B search effort distribution |
| `figures/bb_runtime_distribution.pdf` | B&B runtime at n=500 |
| `figures/runtime_comparison_n500.pdf` | Side-by-side runtime comparison |
| `figures/dp_scaling.pdf` | DP runtime scaling with confidence intervals |

All figures are also available in PNG (600 DPI) and SVG formats.

## Reproducibility

Every table and figure in this paper is generated automatically from the canonical experiment pipeline:

1. `build_and_run.sh` produces `out/results/full_experiment.csv` from deterministic, seeded random instances.
2. `analyze.py` reads the CSV and writes `tables/*.tex` and triggers `figures.py` for figures.
3. The paper references these generated tables directly.

No figures or statistics are edited manually. Running `./reproduce.sh` reproduces the complete experimental results from scratch.

## Paper

The research paper is at `paper/draft.md`. LaTeX tables in `tables/` are designed to be included directly via `\input{tables/table_*}`.

## Key Findings

- **Greedy is provably optimal** on Inverse Correlated instances (where `v + w = constant`) and achieves <1% median gap on Uncorrelated/Weakly Correlated instances.
- **DP runtime is nearly independent** of instance family, scaling linearly with n at fixed capacity.
- **B&B search effort** varies dramatically by family: fast on Uncorrelated/Weakly Correlated, but exponential blowup on Inverse Correlated (median 46K nodes at n=500, max 25M).

## Citation

```bibtex
@article{knapsack2026,
  title={Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics},
  year={2026}
}
```

## License

MIT
