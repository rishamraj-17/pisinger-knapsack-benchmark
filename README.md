# From Static Features to Live Trajectory: Predictive Information Accumulation and Generalization Boundaries in Knapsack Solvers

> An empirical study separating **static instance features** from **dynamic execution metrics** to predict algorithm performance across five Pisinger structural families, demonstrating severe generalization boundaries and rapid online information accumulation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Java](https://img.shields.io/badge/Java-17%2B-orange.svg)](https://openjdk.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)

**Key finding:** Models trained to predict Branch & Bound complexity appear near-perfect in-sample ($R^2 \approx 0.98$) but collapse out-of-distribution via Leave-One-Family-Out (LOFO) evaluation. However, observing just the first 1% of the search tree execution dramatically rescues predictive performance, enabling near-perfect online difficulty prediction.

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Reproducing the Paper](#reproducing-the-paper)
- [Features & Tech Stack](#features--tech-stack)
- [Citation](#citation)
- [License](#license)

---

## Overview

This repository contains the full reproducible pipeline for the paper:

> **"From Static Features to Live Trajectory: Predictive Information Accumulation and Generalization Boundaries in Knapsack Solvers"**  
> Byahut et al. · Kathmandu University · 2026

The study benchmarks three classical 0/1 knapsack algorithms — **Greedy**, **Dynamic Programming**, and **Branch & Bound** — across 6,000 instances from five Pisinger structural families. The core research question is:

*How does predictive information about algorithmic difficulty accumulate as a solver executes, and can internal execution metrics rescue models from severe structural generalization boundaries?*

---

## Repository Structure

```
.
├── src/                   # Java benchmark — instance generators and solvers
│   └── main/java/
│       ├── algorithms/    # Greedy, DP, BranchAndBound (instrumented for early prediction)
│       ├── benchmark/     # Runners (BbInstrumentationRunner, BbSnapshotRunner, etc.)
│       └── dataset/       # Pisinger instance family generators
│
├── data/                  # Experiment data (generated)
│   └── instrumentation/   # CSV traces (instances.csv, bb_instrumentation.csv, bb_snapshots.csv)
│
├── python/                # Python analysis pipeline
│   ├── scripts/           # Standalone analysis scripts (PCA, early prediction, portfolio simulation)
│   └── modeling/          # Statistical modeling pipeline
│       ├── scripts/       # 1_prepare_data, 2_fit_models, 3_compute_importance
│       └── utils/         # Random Forest, Gradient Boosting, OLS (HC3 standard errors)
│
├── results/               # Generated figures and LaTeX tables
│   ├── revision-2/        # New plots for early prediction, generalization PCA, and portfolio regret
│   └── tables/            # Auto-generated .tex tables (input by manuscript)
│
├── manuscript/            # Paper
│   ├── main.tex           # LaTeX source
│   └── references.bib     # Bibliography
│
└── docs/guides/           # Human-readable guides
    └── dataset_features.md# 500+ line dictionary defining every statistical feature
```

---

## Reproducing the Paper

The pipeline runs in three ordered phases.

### Phase 1: Data Generation (Java)
Run the instrumented solvers to generate the base dataset and execution snapshots (1%, 5%, 10%, 25%, 50%, 100%).
```bash
./build_and_run.sh
# Note: You can run specific runners manually, e.g.,
# java -cp "target/classes:lib/commons-csv-1.10.0.jar" benchmark.BbSnapshotRunner
```

### Phase 2: Statistical Modeling (Python)
Fit OLS (with robust standard errors) and Random Forest models using a strict hierarchical cross-validation protocol, including Leave-One-Family-Out (LOFO) evaluation.
```bash
python3 python/modeling/scripts/1_prepare_data.py
python3 python/modeling/scripts/2_fit_models.py
python3 python/modeling/scripts/3_compute_importance.py
```

### Phase 3: Final Analysis & Plots (Python)
Generate the figures supporting the core reframing: algorithmic portfolio simulation, generalization space PCA, and early prediction information accumulation curves.
```bash
python3 python/scripts/simulate_algorithm_selection.py
python3 python/scripts/plot_generalization_space.py
python3 python/scripts/plot_early_prediction.py
```

### Phase 4: Compilation (LaTeX)
Recompile the manuscript to include the new tables and figures.
```bash
cd manuscript && tectonic main.tex
```

---

## Features & Tech Stack

**Research Pipeline**
- Deep instrumentation of Java solvers capturing internal execution snapshots at 1%, 5%, 10%, 25%, and 50% of the search tree size.
- Formal Breusch-Pagan tests for heteroskedasticity leading to HC3 robust standard error usage.
- Strict evaluation ladders: Random CV vs. Leave-One-Family-Out (LOFO) CV.
- Tree-based predictive models (Random Forest) to handle highly non-linear feature interactions without catastrophic outlier failure.

**Tech Stack**
| Layer | Technology |
|-------|-----------|
| Benchmark | Java 17, Apache Commons CSV |
| Analysis | Python 3, pandas, NumPy, scikit-learn |
| Modeling | statsmodels (OLS with HC3), scikit-learn (RandomForest) |
| Figures | Matplotlib (PDF + PNG + SVG) |
| Manuscript | LaTeX (ACM `sigconf`), Tectonic compiler |

---

## Citation

```bibtex
@article{byahut2026knapsack,
  author    = {Byahut, Risham Raj and Neupane, Saimon and Sen, Parikchit
               and Sharma, Keshav and Sharma, Prabesh},
  title     = {From Static Features to Live Trajectory: Predictive Information
               Accumulation and Generalization Boundaries in Knapsack Solvers},
  year      = {2026},
  institution = {Kathmandu University},
  url       = {https://github.com/rishamraj-17/pisinger-knapsack-benchmark}
}
```

---

## License

[MIT](LICENSE) © 2026 Risham Raj Byahut et al.
