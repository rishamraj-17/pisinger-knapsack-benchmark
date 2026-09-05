# Phase 4, Step 3 — Target Repository Structure

## Principle

The repository should reflect the research workflow, not the development chronology. Every directory name should make its purpose obvious to a new reader.

## Current (Abridged)

```
root/
├── src/main/java/         # Active Java source
├── CompareBound.java      # Orphan utility
├── Test*.java (6 files)   # Tests at root
├── *.class (7 files)      # Build artifacts
├── *.py (6 files)         # Analysis scripts
├── governance/ (19 files) # Mixed historical + active
├── Phase_3_3_Modeling/
│   ├── Phase3_Archive/    # Contains Phase4 docs (misnamed)
│   ├── Phase3_Freeze/     # Frozen Phase 3 output
│   └── Phase4_Freeze/     # Duplicates Phase3_Archive docs
├── PIPELINE.md            # Triplicated
├── README.md              # Triplicated
├── CONTINUE_FROM_HERE.md  # Triplicated
└── Submission_Package/    # Frozen
```

## Target

```
repository/
├── benchmark/                   # Java benchmark (moved from root)
│   ├── src/main/java/           # Java source
│   ├── src/test/java/           # Test files (moved from root)
│   ├── pom.xml
│   ├── build_and_run.sh
│   ├── reproduce.sh
│   ├── lib/
│   └── out/                     # Compiled classes + results
├── dataset/                     # Canonical data (moved from root)
│   ├── canonical_dataset.csv    # Moved from out/results/
│   └── results/                 # Instrumentation CSVs (moved from results/)
├── analysis/                    # Phase 1 analysis (moved from root)
│   ├── analyze.py
│   ├── figures.py
│   ├── plot_utils.py
│   ├── eda_phase3_1.py
│   ├── extract_features.py
│   ├── update_draft.py
│   ├── eda_output/
│   ├── tables/
│   └── figures/
├── modeling/                    # Phase 3.3 modeling (renamed from Phase_3_3_Modeling)
│   ├── config.py
│   ├── scripts/
│   ├── utils/
│   ├── output/
│   └── freeze/                  # Frozen snapshots (consolidated from Phase3_Freeze + Phase4_Freeze)
├── paper/                       # Manuscript
│   └── draft.md
├── submission/                  # Frozen submission (renamed from Submission_Package)
├── docs/                        # Consolidated documentation
│   ├── INSTANCE_FEATURES.md
│   ├── PIPELINE.md
│   └── ARCHITECTURE_CONFORMANCE_REPORT.md
├── historical/                  # Archived phase documentation
│   ├── governance/              # All phase reports and audits
│   ├── plans/                   # Implementation plans
│   └── Phase3_Archive/          # Archived snapshot
├── CITATION.cff
├── LICENSE
└── README.md
```

## Rationale Per Change

| Change | Rationale |
|--------|-----------|
| `src/` stays, tests move to `src/test/java/` | Standard Maven convention; discoverability |
| `*.class` files removed | Build artifacts in VCS violates reproducibility (should be regenerable) |
| Root `.py` files → `analysis/` | Logical grouping by pipeline stage; discoverability |
| `results/` + `out/results/` → `dataset/` | All raw data in one place; dependency reduction |
| `Phase_3_3_Modeling/` → `modeling/` | Shorter, clearer name; remove phase numbering from directory name |
| `Submission_Package/` → `submission/` | Simpler name; underscore unnecessary |
| `governance/` → `historical/governance/` | All completed phases; no active governance needed |
| `Phase3_Archive/` → `historical/Phase3_Archive/` | Archive belongs with other historical material |
| `Phase3_Freeze/` + `Phase4_Freeze/` → `modeling/freeze/` | Consolidated frozen outputs |
| Duplicated docs → single canonical copies | Eliminate ambiguity about which is authoritative |
| `Phase4_*.md` documents → `historical/` | These were pre-freeze audit artifacts; superseded by this report |

## NOT Changing

- `paper/draft.md` — active manuscript
- `modeling/output/` — generated modeling outputs (too many internal references)
- `lib/` — dependency JARs
- `CITATION.cff`, `LICENSE` — metadata
- `vendor/` or `venv/` — environments (kept where they are)
