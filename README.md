# Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics

A reproducible empirical study comparing three classical 0/1 knapsack algorithms (Greedy, Dynamic Programming, Branch & Bound) across five Pisinger instance families. The study analyzes how instance correlation structure and capacity scaling affect practical algorithm performance.

## Research Workflow

```
Java Benchmark ──► Canonical Dataset ──► Analysis ──► Paper
                                            │
                                     Statistical Modeling ──► Feature Importance + Diagnostics
```

The `PIPELINE.md` file describes the reproduction workflow in detail.

## Repository Structure

| Directory | Purpose | Status |
|-----------|---------|--------|
| `src/main/java/` | Algorithm implementations, benchmark harness, instance generators, dataset integration | **Active** |
| `out/results/` | Canonical experiment output (`full_experiment.csv`, 18,000 runs) | **Generated** |
| `results/` | Instrumentation CSVs (algorithm execution traces) | **Generated** |
| `analysis/` scripts | `analyze.py`, `figures.py`, `plot_utils.py`, `eda_phase3_1.py`, `extract_features.py`, `update_draft.py` | **Active** |
| `tables/` | LaTeX tables generated from experiment data | **Generated** |
| `figures/` | Publication figures (PDF, PNG, SVG — fixed and scaled capacity modes) | **Generated** |
| `Phase_3_3_Modeling/` | Statistical modeling pipeline (see below) | **Active** |
| `Submission_Package/` | Frozen manuscript LaTeX, tables, figures, and supplementary materials | **Frozen** |
| `paper/` | Manuscript draft (`draft.md`) | **Active** |
| `docs/` | Supplementary documentation (`INSTANCE_FEATURES.md`) | **Active** |
| `governance/` | Phase reports, design documents, and audits from completed phases | **Historical** |

> **Active** = current development source / documentation.
> **Frozen** = immutable artifacts supporting the paper; do not modify.
> **Historical** = records of completed phases; preserved for provenance.
> **Generated** = pipeline output; regenerable on demand.

## Phase 3.3 — Statistical Modeling

The `Phase_3_3_Modeling/` directory contains the statistical modeling pipeline that investigates which internal algorithm execution metrics best explain runtime and solution quality. It consists of:

- `config.py` — Central configuration (model specifications, predictors, exclusions)
- `scripts/` — Pipeline stages: `1_prepare_data.py` → `2a_fit_ols.py`, `2b_fit_fractional_logit.py`, `2c_fit_elasticnet.py`, `2d_fit_hurdle.py` → `3_compute_importance.py` → `4_diagnostics.py`
- `utils/` — Shared modules: `models.py`, `importance.py`, `diagnostics.py`, `metrics.py`, `cv.py`, `preprocessing.py`, `data.py`, `fractional_models.py`
- `output/` — Generated results, cross-validation folds, diagnostics, feature importance rankings, and figures

Frozen snapshots of modeling outputs are preserved in `Phase_3_3_Modeling/Phase3_Freeze/` and `Phase_3_3_Modeling/Phase4_Freeze/`.

## Quick Start

```bash
# Full reproduction: 18,000 algorithm runs, all tables and figures
./reproduce.sh
```

```bash
# Smaller test run (~10 seconds)
./build_and_run.sh 20,50 1000 5 42

# Generate analysis tables and figures
python3 analyze.py out/results/full_experiment.csv
```

See `PIPELINE.md` for the complete provenance chain and parameter reference.

## Root Java Files

Several Java validation utilities (`TestBound.java`, `TestFloat.java`, `TestNodeCount.java`, `TestPQ.java`, `TestRandom.java`) reside at the repository root. These are manual development-time tools used during algorithm implementation. They have no dependencies from any automated pipeline, shell script, or documentation, and intentionally remain at the root for straightforward compilation and execution without IDE configuration.

## Prerequisites

- **Java 17+** (OpenJDK or Oracle JDK)
- **Python 3.8+** with NumPy and Matplotlib
- Phase 3.3 modeling requires additional packages (see `Phase_3_3_Modeling/.venv/`)

## Reproducibility

Every numerical value in the paper traces to `out/results/full_experiment.csv` through `analyze.py`. No figures or statistics are edited manually. See `PIPELINE.md` for the full provenance chain.

## Paper

The research paper is at [`paper/draft.md`](paper/draft.md). LaTeX tables in `tables/` are designed for `\input{tables/*_table_*}` inclusion. The submitted manuscript is at [`Submission_Package/manuscript.pdf`](Submission_Package/manuscript.pdf).

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
