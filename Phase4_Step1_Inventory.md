# Phase 4, Step 1 — Complete Repository Inventory

**Date:** 2026-07-28
**Method:** Full directory traversal, file inspection, git tracking verification

---

## Classification Legend

| Category | Meaning |
|----------|---------|
| **Active** | Source code, config, or active documentation that is part of the current workflow |
| **Frozen** | Immutable artifact supporting the paper; do not modify |
| **Generated** | Output produced by a pipeline step; regenerable on demand |
| **Historical** | Phase completion report or audit from a completed phase; preserved for reference |
| **Archived** | Superseded or snapshot documentation; kept for provenance but not actively maintained |

---

## 1. Root Directory

| Path | Type | Purpose | Classification | Notes |
|------|------|---------|----------------|-------|
| `src/` | Dir | Java source tree (algorithms, benchmark, dataset, model, Main.java) | **Active** | Primary development source |
| `pom.xml` | File | Maven build descriptor | **Active** | Build configuration |
| `build_and_run.sh` | File | Build + run wrapper for Java | **Active** | Full pipeline entry point |
| `reproduce.sh` | File | Full reproduction script | **Active** | CI/release reproduction |
| `lib/` | Dir | External JAR dependencies | **Active** | Contains commons-csv-1.10.0.jar |
| `target/` | Dir | Maven build output | **Generated** | Compiled classes; gitignored |
| `out/` | Dir | Java runtime output (compiled classes + results) | **Generated** | Only full_experiment.csv tracked |
| `results/` | Dir | Instrumentation CSVs (bb, dp, greed, instances) | **Generated** | Output of instrumentation runners |
| `Phase_3_3_Modeling/` | Dir | Statistical modeling subproject (Python) | **Active** | Phase 3.3 pipeline (7 scripts, 9 utils) |
| `analyze.py` | File | Statistical analysis of experiment results | **Active** | Phase 1 analysis |
| `figures.py` | File | Publication figure generation | **Active** | Phase 1 figures |
| `plot_utils.py` | File | Shared plotting utilities | **Active** | Imported by figures.py, analyze.py, eda_phase3_1.py |
| `extract_features.py` | File | Instance feature extraction | **Active** | Phase 2.1 feature extraction |
| `eda_phase3_1.py` | File | Exploratory data analysis | **Active** | Phase 3.1 EDA |
| `update_draft.py` | File | Draft manuscript updater | **Active** | Links results to paper draft |
| `paper/` | Dir | Manuscript draft (draft.md) | **Active** | Current manuscript working copy |
| `tables/` | Dir | LaTeX tables (fixed + scaled) | **Generated** | Output of Phase 1 analysis |
| `figures/` | Dir | Generated figures (fixed + scaled) | **Generated** | 36 files across 3 formats |
| `docs/` | Dir | Documentation (INSTANCE_FEATURES.md) | **Active** | Supplementary documentation |
| `governance/` | Dir | Phase reports, audits, design docs | **Historical** | 19 files; completed phases |
| `Submission_Package/` | Dir | Frozen manuscript + supplementary materials | **Frozen** | DO NOT MODIFY |
| `eda_output/` | Dir | Phase 3.1 EDA outputs | **Generated** | Boxplots, histograms, CSVs |
| `ARCHITECTURE_CONFORMANCE_REPORT.md` | File | Architecture audit report | **Active** | Phase 4 deliverable |
| `CITATION.cff` | File | Citation metadata | **Active** | For GitHub/Zenodo |
| `LICENSE` | File | Project license | **Active** | |
| `README.md` | File | Top-level project description | **Active** | Repository entry point |
| `PIPELINE.md` | File | Pipeline workflow documentation | **Active** | Also duplicated in Phase3_Archive, Phase4_Freeze |
| `CONTINUE_FROM_HERE.md` | File | Development handoff notes | **Historical** | Also duplicated in Phase3_Archive, Phase4_Freeze |
| `CompareBound.java` | File | Standalone Java utility | **Active** | Should be in `src/main/java/` |
| `TestBound.java` | File | JUnit test | **Active** | Should move under `src/test/java/` |
| `TestFloat.java` | File | JUnit test | **Active** | Same |
| `TestIsolate.java` | File | JUnit test | **Active** | Same |
| `TestNodeCount.java` | File | JUnit test | **Active** | Same |
| `TestPQ.java` | File | JUnit test | **Active** | Same |
| `TestRandom.java` | File | JUnit test | **Active** | Same |
| `venv/` | Dir | Python virtual environment | **Active** | Root-level venv for Phase 1 |
| `.gitignore` | File | Git ignore rules | **Active** | |
| `.idea/` | Dir | IntelliJ IDE config | **Active** | Developer-local |
| `__pycache__/` | Dir | Python bytecode cache | **Generated** | Safe to ignore |

---

## 2. `src/` (Java Source Tree)

| Path | Classification | Notes |
|------|----------------|-------|
| `src/main/java/Main.java` | **Active** | Entry point |
| `src/main/java/TimeoutValidation.java` | **Active** | Utility |
| `src/main/java/algorithms/` (8 files) | **Active** | Algorithm + instrumentation |
| `src/main/java/benchmark/` (6 files) | **Active** | Runners, exporters |
| `src/main/java/dataset/` (7 source files) | **Active** | + stale `.class` files |
| `src/main/java/model/` (3 source files) | **Active** | + stale `.class` files |

**Issue:** Stale `.class` files inside `src/main/java/dataset/` and `src/main/java/model/` — build artifacts committed to source tree.

---

## 3. `Phase_3_3_Modeling/`

| Path | Classification | Notes |
|------|----------------|-------|
| `config.py` | **Active** | Single source of truth for model config |
| `scripts/` (7 scripts) | **Active** | Pipeline stages 1-4 |
| `utils/` (8 modules) | **Active** | Shared utilities |
| `output/` | **Generated** | All modeling outputs (results, CV, diagnostics, importance, figures) |
| `Phase3_Archive/` | **Archived** | Duplicates Phase4_Freeze content; contains Phase4 documents |
| `Phase3_Freeze/` | **Frozen** | Frozen Phase 3 output snapshot |
| `Phase4_Freeze/` | **Frozen** | Frozen Phase 4 output + documents |
| `.venv/` | **Active** | Project-local Python venv |

**Issues:**
- `Phase3_Archive/` and `Phase4_Freeze/` contain **nearly identical** content (both have all 13 Phase4_*.md docs + PIPELINE.md + README.md + CONTINUE_FROM_HERE.md). One should be canonical.
- `output/tables/` is empty.
- `Phase3_Archive/` is misnamed — it contains Phase 4 documents, not Phase 3 content.

---

## 4. `governance/`

| File | Classification | Notes |
|------|----------------|-------|
| PHASE_2_1_REPORT.md through PHASE_2_5_REPORT.md | **Historical** | Phase 2 completion reports |
| PHASE_2_5_AUDIT.md | **Historical** | Phase 2 audit |
| PHASE_3_1_REPORT.md through PHASE_3_1_AUDIT.md | **Historical** | Phase 3.1 |
| PHASE_3_2_DESIGN.md, PHASE_3_2_AUDIT.md, PHASE_3_2_AUDIT_2.md, PHASE_3_2_REVISION_CHANGELOG.md | **Historical** | Phase 3.2 design + audits |
| PHASE_3_3_IMPLEMENTATION_PLAN.md | **Historical** | Phase 3.3 plan (completed) |
| PHASE_3_3_2_AUDIT.md | **Historical** | Phase 3.3.2 audit (completed) |
| PROJECT_ARCHITECTURE_REVIEW.md | **Historical** | Architecture review (superseded by ARCHITECTURE_CONFORMANCE_REPORT.md) |
| PROJECT_ROADMAP.md | **Historical** | Roadmap (completed phases) |
| PROJECT_STATE_REPORT.md | **Historical** | State report (superseded) |
| FINAL_HARDENING_LEDGER.md | **Historical** | Final hardening audit |
| peer_review_knapsack_paper.md | **Historical** | Peer review notes |

**All 19 governance files are Historical.** Every phase they document is complete. The active documents are now:
- Root-level `ARCHITECTURE_CONFORMANCE_REPORT.md`
- Root-level `README.md` (needs updating)

---

## 5. Documentation Duplication

The following documents exist in **3 locations** each:

| Document | Root | Phase3_Archive/ | Phase4_Freeze/ |
|----------|------|-----------------|----------------|
| `PIPELINE.md` | ✅ | ✅ | ✅ |
| `CONTINUE_FROM_HERE.md` | ✅ | ✅ | ✅ |
| `README.md` | ✅ | ✅ | ✅ |

The 13 `Phase4_*.md` documents (claim inventory, evidence audit, manuscript readiness, etc.) exist in **both** `Phase3_Archive/` and `Phase4_Freeze/`.

---

## 6. Summary Statistics

| Classification | Count (top-level items) |
|----------------|------------------------|
| **Active** | ~30 |
| **Frozen** | ~15 (Submission_Package/, Phase3_Freeze/, Phase4_Freeze/) |
| **Generated** | ~500+ (out/, results/, tables/, figures/, eda_output/, Phase_3_3_Modeling/output/) |
| **Historical** | ~19 (governance/) |
| **Archived** | ~15 (Phase3_Archive/) |

---

## 7. Immediate Issues Identified

1. **Phase3_Archive/ duplicates Phase4_Freeze/** — same Phase4 documents in both
2. **PIPELINE.md, README.md, CONTINUE_FROM_HERE.md** — triplicated (root + archive + freeze)
3. **Root-level `.java` test files** — should live under `src/test/java/`
4. **Root-level `CompareBound.java`** — standalone utility, no obvious home
5. **Stale `.class` files** in `src/main/java/dataset/` and `src/main/java/model/`
6. **Root-level `.class` files** — build artifacts checked into version control
7. **`governance/`** — all Historical; should be archived to a `historical/` directory
8. **`output/tables/`** — empty directory
