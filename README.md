# Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics

A reproducible empirical study comparing three classical 0/1 knapsack algorithms (Greedy, Dynamic Programming, Branch & Bound) across five Pisinger instance families, analyzing how instance correlation structure and capacity scaling affects practical performance.

## Prerequisites

- **Java 17+** (OpenJDK or Oracle JDK)
- **Python 3.8+** with [NumPy](https://numpy.org/) and [Matplotlib](https://matplotlib.org/)

## Quick Start

```bash
# Full reproduction: experiment + analysis (~2 minutes)
./reproduce.sh
```

This runs 18,000 algorithm runs (3,000 instances x 3 algorithms x 2 capacity modes) and generates all tables and figures.

### Step by Step

```bash
# 1. Build and run the experiment
./build_and_run.sh 20,50,100,200,500 1000 30 42

# 2. Generate LaTeX tables and publication figures
python3 analyze.py out/results/full_experiment.csv
```

### Custom Parameters

```bash
# Smaller run for testing (~10 seconds)
./build_and_run.sh 20,50 1000 5 42
```

## Generated Outputs

| File | Description |
|------|-------------|
| `out/results/full_experiment.csv` | Raw data (18,000 rows) |
| `tables/table_*.tex` | LaTeX tables for direct inclusion |
| `figures/fixed/pdf/*.pdf`, `figures/scaled/pdf/*.pdf` | Publication figures (vector) |
| `figures/fixed/png/*.png`, `figures/scaled/png/*.png` | Publication figures (600 DPI) |
| `figures/fixed/svg/*.svg`, `figures/scaled/svg/*.svg` | Publication figures (editable) |

## Repository Structure

```
├── src/main/java/          # Java source code
│   ├── Main.java           # Entry point
│   ├── algorithms/         # Greedy, DP, BranchAndBound
│   ├── dataset/            # Pisinger instance generators
│   ├── benchmark/          # BenchmarkRunner, ResultsExporter
│   └── model/              # Item, KnapsackInstance, Result
├── paper/draft.md          # Research paper (Markdown)
├── tables/                 # Generated LaTeX tables
├── figures/                # Generated figures (fixed/{pdf,png,svg}, scaled/{pdf,png,svg})
├── out/results/            # Canonical data (full_experiment.csv)
├── analyze.py              # Analysis pipeline
├── figures.py              # Figure generation
├── plot_utils.py           # Shared plotting utilities
├── build_and_run.sh        # Build and run experiment
├── reproduce.sh            # Full reproduction pipeline
└── pom.xml                 # Maven build configuration
```

## Reproducibility

Every table and figure in the paper is generated automatically:

1. `build_and_run.sh` produces `out/results/full_experiment.csv` from deterministic, seeded instances
2. `analyze.py` reads the CSV and writes `tables/*.tex` and triggers `figures.py` (generating both fixed and scaled capacity results)

No figures or statistics are edited manually. See `PIPELINE.md` for the full provenance chain.

## Paper

The research paper is at [`paper/draft.md`](paper/draft.md). LaTeX tables in `tables/` are designed for `\input{tables/table_*}` inclusion.

## Citation

```bibtex
@software{knapsack2026,
  author       = {Risham Raj},
  title        = {Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics},
  year         = {2026},
  url          = {https://github.com/rishamraj-17/knapsack-benchmark},
  license      = {MIT}
}
```

See [`CITATION.cff`](CITATION.cff) for a machine-readable citation.

## License

[MIT](LICENSE)
