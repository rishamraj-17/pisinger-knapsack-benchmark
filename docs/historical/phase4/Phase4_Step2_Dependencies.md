# Phase 4, Step 2 — Dependency Mapping

## Critical Dependency: `build_tables.py` hardcoded path

`Submission_Package/build_tables.py:6` contains an absolute path to `Phase_3_3_Modeling/Phase3_Archive/output/`. This is the only external reference from the frozen submission package back into the active repo. Any restructuring of Phase3_Archive must update this reference.

## Two Independent Pipelines

**Pipeline A (Phase 0/1 — Benchmark → Paper):**
`src/main/java/` → `build_and_run.sh` → `out/results/full_experiment.csv` → `analyze.py` → `tables/*.tex` + `figures/*` → `paper/draft.md`

**Pipeline B (Phase 3.3 — Statistical Modeling):**
`out/results/canonical_dataset.csv` → `Phase_3_3_Modeling/scripts/1_prepare_data.py` → `2*_fit_*.py` → `3*_importance.py` → `4*_diagnostics.py`

**Only crossover:** `eda_phase3_1.py` imports `plot_utils` from root.

## Documentation Triplication

`PIPELINE.md`, `README.md`, `CONTINUE_FROM_HERE.md` exist in **3 locations**: root, `Phase_3_3_Modeling/Phase3_Archive/`, `Phase_3_3_Modeling/Phase4_Freeze/`.

## Phase3_Archive / Phase4_Freeze Duplication

Both contain identical sets of 13 `Phase4_*.md` documents. One is redundant.

## Archive-to-Freeze Dependency

`Submission_Package/build_tables.py` reads from `Phase_3_3_Modeling/Phase3_Archive/output/results/`. If Phase3_Archive is restructured, this path must be updated.
