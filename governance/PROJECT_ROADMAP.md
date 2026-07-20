# Project Roadmap — Knapsack Empirical Comparison

## Overview

Canonical project roadmap. This document defines all planned phases and tracks
completion status. Each phase is gated — the next phase begins only after the
previous phase is independently verified, frozen, committed, tagged, and approved.

---

## Phase 0 — Benchmark Foundation ✅

**Status:** Complete

Implementation of the three knapsack algorithms (Greedy, Dynamic Programming,
Branch & Bound), five Pisinger instance generators, the benchmark harness, and
the reproducible experiment pipeline.

**Deliverables:**
- `src/main/java/algorithms/` — Greedy, DP, B&B implementations
- `src/main/java/dataset/` — Five Pisinger instance generators
- `src/main/java/benchmark/` — BenchmarkRunner, ResultsExporter
- `build_and_run.sh` — Build and run wrapper
- `reproduce.sh` — Full reproduction pipeline
- `out/results/full_experiment.csv` — Canonical experiment output (18,000 rows)

---

## Phase 1 — Benchmark Paper ✅

**Status:** Complete

Analysis, visualization, and manuscript generation from benchmark data. Includes
LaTeX tables with bootstrap confidence intervals, publication-quality figures,
and the research paper draft.

**Deliverables:**
- `analyze.py` — Statistical analysis and LaTeX table generation
- `figures.py` — Publication-quality figure generation
- `plot_utils.py` — Shared plotting utilities
- `tables/*.tex` — LaTeX tables for manuscript inclusion
- `figures/fixed/*`, `figures/scaled/*` — PDF, PNG, SVG figures
- `paper/draft.md` — Research paper manuscript

---

## Phase 2 — Rich Analysis Dataset

### Phase 2.1 — Instance Characterization ✅

**Status:** Complete

Treat every generated knapsack instance as a measurable object. Compute 36
descriptive features characterizing each instance independent of any algorithm.

**Deliverables:**
- `extract_features.py` — Deterministic instance feature extraction
- `results/instances.csv` — 6,000 rows × 40 columns (v1.0, MD5: `3ee015ea`)
- `docs/INSTANCE_FEATURES.md` — Canonical feature specification
- `governance/PHASE_2_1_REPORT.md` — Governance report

### Phase 2.2 — B&B Instrumentation ⬜

**Status:** Pending

Instrument the Branch & Bound algorithm to record per-instance execution traces
without modifying search logic, pruning decisions, or correctness.

### Phase 2.3 — DP Instrumentation ⬜

**Status:** Pending

Instrument the Dynamic Programming algorithm to record per-instance execution
traces without modifying the DP recurrence or correctness.

### Phase 2.4 — Greedy Instrumentation ⬜

**Status:** Pending

Instrument the Greedy algorithm to record per-instance execution traces without
modifying the greedy selection logic or correctness.

### Phase 2.5 — Dataset Assembly ⬜

**Status:** Pending

Merge instance characterization features (Phase 2.1) with algorithm execution
statistics (Phases 2.2–2.4) to produce the complete rich analysis dataset.

**Key join:** `(instance_id, capacity_mode)` between `results/instances.csv`
and algorithm instrumentation outputs.

### Phase 2.6 — Dataset Validation ⬜

**Status:** Pending

Validate the assembled dataset for completeness, consistency, missing values,
outliers, and scientific plausibility before releasing for analysis.

---

## Phase 3 — Empirical Analysis ⬜

**Status:** Pending

Statistical analysis of the rich analysis dataset. Exploratory data analysis,
feature distributions, correlations between instance properties and algorithm
performance, hardness analysis.

---

## Phase 4 — Research Questions ⬜

**Status:** Pending

Targeted investigation of specific research questions using the analysis
dataset. Hypothesis testing, predictive modeling, feature importance, clustering.

---

## Phase 5 — Novel Research Paper ⬜

**Status:** Pending

Synthesis of findings into a novel research paper with new scientific insights
beyond the initial benchmark comparison paper (Phase 1).

---

## Completion Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete — verified, frozen, committed, tagged |
| ⬜ | Pending — not yet started |
| 🔄 | In progress |
| ⏸️ | Blocked or deferred |
