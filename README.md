# Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics

A reproducible empirical study comparing three classical 0/1 knapsack algorithms (Greedy, Dynamic Programming, Branch & Bound) across five Pisinger instance families. The study analyzes how instance correlation structure and capacity scaling affect practical algorithm performance.

## Research Workflow

```
Java Benchmark ──► Canonical Dataset ──► Analysis ──► Paper
                                            │
                                     Statistical Modeling ──► Feature Importance + Diagnostics
```

The [`docs/guides/reproduction_pipeline.md`](docs/guides/reproduction_pipeline.md) file describes the reproduction workflow in detail. For an intuitive introduction to the codebase, start with the [`docs/guides/professors_guide.md`](docs/guides/professors_guide.md).

## Repository Structure

The repository is organized into five strictly separated domain contexts:

| Directory | Purpose | Status |
|-----------|---------|--------|
| `src/` | Java benchmark source code, instance generators, and solvers (`main/` and `test/`) | **Active** |
| `data/` | Canonical experiment output (`data/raw/full_experiment.csv`) and execution traces (`data/instrumentation/`) | **Generated** |
| `python/` | Statistical modeling pipeline (`python/modeling/`) and analysis utilities (`python/scripts/`) | **Active** |
| `outputs/` | Publication figures, LaTeX tables, and EDA charts generated from experiment data | **Generated** |
| `manuscript/` | Final manuscript LaTeX source (`main.tex`) and compiled PDF (`main.pdf`) | **Frozen** |
| `docs/` | Core guides (`docs/guides/`) and archived project management audits (`docs/historical/`) | **Historical** |

> **Active** = current development source code.
> **Frozen** = immutable artifacts supporting the paper; do not modify.
> **Historical** = records of completed phases; preserved for provenance.
> **Generated** = pipeline output; regenerable on demand via `reproduce.sh`.

## Phase 3.3 — Statistical Modeling

The `python/modeling/` directory contains the statistical modeling pipeline that investigates which internal algorithm execution metrics best explain runtime and solution quality. It consists of:

- `config.py` — Central configuration (model specifications, predictors, exclusions)
- `scripts/` — Pipeline stages: `1_prepare_data.py` → `2a_fit_ols.py`, `2b_fit_fractional_logit.py`, `2c_fit_elasticnet.py`, `2d_fit_hurdle.py` → `3_compute_importance.py` → `4_diagnostics.py`
- `utils/` — Shared modules: `models.py`, `importance.py`, `diagnostics.py`, `metrics.py`, `cv.py`, `preprocessing.py`, `data.py`, `fractional_models.py`
- `output/` — Generated results, cross-validation folds, diagnostics, feature importance rankings, and figures

## Quick Start

```bash
# Full reproduction: 18,000 algorithm runs, all tables and figures
./reproduce.sh
```

```bash
# Smaller test run (~10 seconds)
./build_and_run.sh 20,50 1000 5 42

# Generate analysis tables and figures
python3 python/scripts/analyze.py data/raw/full_experiment.csv
```

See `docs/guides/reproduction_pipeline.md` for the complete provenance chain and parameter reference.

## Prerequisites

- **Java 17+** (OpenJDK or Oracle JDK)
- **Python 3.8+** with NumPy and Matplotlib
- Phase 3.3 modeling requires additional packages (see `python/venv/`)

## Reproducibility

Every numerical value in the paper traces to `data/raw/full_experiment.csv` through `python/scripts/analyze.py`. No figures or statistics are edited manually. 

## Paper

The final submitted manuscript and its LaTeX source are located in the [`manuscript/`](manuscript/) folder. All numerical claims within it are pulled automatically from the `outputs/` directory.

## Citation

```bibtex
@software{knapsack2026,
  author       = {Risham Raj Byahut},
  title        = {Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics},
  year         = {2026},
  url          = {https://github.com/rishamraj-17/knapsack-benchmark},
  license      = {MIT}
}
```

See [`CITATION.cff`](CITATION.cff) for machine-readable metadata.

## License

[MIT](LICENSE)
