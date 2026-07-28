# Phase 4 — Remaining Proposals: Decision Report

**Date:** 2026-07-28
**Method:** Each proposal analyzed against repository evidence before any modification.

---

## Proposal A — Root-Level Java Files

### Evidence

Seven files at repository root: `CompareBound.java`, `TestBound.java`, `TestFloat.java`, `TestIsolate.java`, `TestNodeCount.java`, `TestPQ.java`, `TestRandom.java`.

### Classification (by reading code, not filenames)

| File | Lines | Actual Purpose | Classification |
|------|-------|----------------|----------------|
| `CompareBound.java` | 18 | Empty `main()` with only comments; never finished | Dead/abandoned experimental program |
| `TestBound.java` | 15 | Prints boolean results of comparing floating-point addition orderings | Debugging/validation tool |
| `TestFloat.java` | 91 | Compares old (linear scan) vs new (binary search + prefix sums) bound calculation. 1000 random instances, exhaustive capacity/value sweep. Bit-exact equality verification | Validation tool (bound correctness) |
| `TestIsolate.java` | 11 | Empty `main()` with only comments; was going to grep CSVs | Dead/abandoned |
| `TestNodeCount.java` | 17 | Imports `dataset.*`, `model.*`, `algorithms.*`. Creates AlmostEqualRatios instance, runs B&B, prints node count | Validation tool (node count) |
| `TestPQ.java` | 87 | Same old-vs-new bound comparison as TestFloat.java, but on single instance only. Reports mismatch count | Validation tool (bound correctness, reduced scope) |
| `TestRandom.java` | 29 | Tests Java `Random` sequence reproducibility with benchmark seed formula | Debugging/validation tool |

### Dependency Analysis

| File | Compiled by build script? | Executed by any script? | Referenced by docs? | Referenced by README? |
|------|--------------------------|------------------------|---------------------|-----------------------|
| All 7 | **No** — `build_and_run.sh` uses `find src/main/java -name "*.java"`, root files excluded | **No** — no script references them | **No** | **No** |
| TestNodeCount, TestPQ | Would need classpath including `out/` and `lib/commons-csv` for their `import dataset.*` statements | Manual only | No | No |

None of these files participate in any automated pipeline. They are manual development-time tools.

### Build System Analysis

Current build: flat `javac` via shell script (`build_and_run.sh`). `pom.xml` exists but is not used for development compilation (the script predates or bypasses Maven).

To move these to `src/test/java/`:
- All files lack `package` declarations. Java default-package classes must reside at the classpath root. Moving to `src/test/java/` would require either: (a) adding package declarations, or (b) adding `src/test/java/` as an additional classpath root.
- `TestNodeCount.java` and `TestPQ.java` import `dataset.*`, `model.*`, `algorithms.*` — these packages are in `src/main/java/`. With no package declaration, cross-package visibility is restricted.
- The files don't use JUnit or any test framework. They are `public static void main` programs.

Adopting `src/test/java/` would be architecturally consistent with Maven/Gradle conventions, but this repository uses flat `javac` for builds, and these files aren't part of any build pipeline anyway. The benefit is purely cosmetic — and implementing it correctly requires more than just moving files (package declarations, import updates, classpath changes).

### Risk Assessment

| Factor | Assessment |
|--------|-----------|
| What breaks if moved? | Nothing — no pipeline depends on them |
| What must change? | Package declarations + imports for TestNodeCount/TestPQ; build_and_run.sh `find` command; compile/test instructions |
| What becomes simpler? | Root directory has fewer files; src/ becomes standard Maven layout |
| What becomes more complicated? | Flat javac build now needs multi-source-root handling; default-package Java files need restructuring |

### Recommendation: **Proceed with modifications**

Specifically:
1. **Delete** `CompareBound.java` and `TestIsolate.java` — dead code, empty main methods, no value
2. **Leave** `TestBound.java`, `TestFloat.java`, `TestNodeCount.java`, `TestPQ.java`, `TestRandom.java` **where they are** — they are manual development tools with no automated dependencies. Moving them to `src/test/java/` requires package declarations and import restructuring for zero automation benefit. A note in the README ("_Development validation tools in root directory_") suffices.

**Rationale:** The effort to restructure default-package Java files into a proper test hierarchy exceeds the benefit for files that no automation depends on. Only dead code should be removed.

---

## Proposal B — `build_tables.py`

### Evidence

File at `Submission_Package/build_tables.py:6`:
```python
ARCHIVE = "/home/risham-raj-byahut/IdeaProjects/Emperical_Comparision/Phase_3_3_Modeling/Phase3_Archive/output"
```

### Governance Analysis

The `Submission_Package/` directory is declared **Frozen**. The user's Phase 4 philosophy states:

> "Treat the following as frozen: ... Submission_Package"
> "Do not regenerate, overwrite, or edit these unless reproducing the entire pipeline intentionally."

`build_tables.py` is a build script inside the frozen package. Its purpose is to regenerate the submission LaTeX tables from the frozen modeling outputs. The absolute path works — `Phase3_Archive/output/` exists and is stable.

### Recommendation: **Reject**

The path works. The script is inside a frozen directory. Any modification violates the frozen boundary. If the `Phase3_Archive/output/` directory ever needs to move, a symlink at the original path is the correct solution — not modifying the frozen script.

---

## Proposal C — `governance/` Relocation

### Evidence

42 cross-references to `governance/` across 15 files:

| Pattern | Count | Files Affected |
|---------|-------|----------------|
| Internal governance/ → governance/ | ~30 | ~12 files in governance/ itself |
| External (CONTINUE_FROM_HERE.md × 3 copies) | 9 | 3 locations × 3 refs each |
| External (my Phase4_Step*.md) | 3 | 3 Phase4 doc files |

All references use `governance/` as a path prefix. Moving to `historical/governance/` requires updating every reference.

### Risk Assessment

| Factor | Assessment |
|--------|-----------|
| Files to update | ~15 files |
| References to change | ~42 |
| Risk of missed reference | Moderate — grep catches all, but some may be embedded in code blocks or inline HTML |
| Maintenance benefit | Low — governance/ is already self-contained and clearly labeled |
| Historical value | Governance documents are valuable, but their current location doesn't impede discoverability |

### Recommendation: **Reject**

The 42-reference update cost does not justify the benefit of a directory rename. Governance documents are self-contained, clearly labeled with phase numbers, and serve no active pipeline role. They should be labeled as "Historical" in documentation (README) but left physically in place. This is consistent with the principle that documentation should describe the repository as it is rather than imposing arbitrary naming conventions.

---

## Proposal D — README Audit

### Current README (`README.md`, 99 lines)

**Obsolete Sections:**

1. **Repository Structure** (lines 48-67): Missing `Phase_3_3_Modeling/`, `docs/`, `governance/`, `Submission_Package/`, `eda_output/`, `results/`, `lib/`, `venv/`. The diagram covers only Phase 0/1 components.

2. **Generated Outputs** (lines 38-46): Only lists Phase 1 outputs (CSV, tables, figures). Missing all Phase 3.3 outputs (modeling results, diagnostics, feature importance, cross-validation).

3. **Quick Start** (lines 10-17): Describes `./reproduce.sh` as the full pipeline, but this only covers Phase 0/1. Phase 3.3 modeling is entirely omitted.

**Missing Sections:**

1. **Phase 3.3 Statistical Modeling**: No mention of the modeling pipeline (1_prepare_data.py → 2*_fit_*.py → 3*_importance.py → 4*_diagnostics.py). This is the largest recent addition to the repository.

2. **Frozen Artifacts**: No mention of `Phase_3_3_Modeling/Phase4_Freeze/`, `Submission_Package/`, or what should not be modified.

3. **Historical Documentation**: No mention of `governance/` for phase reports.

4. **Repository Classification**: No indication of which directories are Active, Generated, Frozen, or Historical.

**Duplicated Information:**

Lines 69-76 (Reproducibility section) largely restates what PIPELINE.md already covers in more detail. Could be condensed to a cross-reference.

**Broken References:**

None currently — all links in README resolve.

**Discoverability Problems:**

A new contributor who clones the repository will see:
```
README.md
PIPELINE.md
Phase_3_3_Modeling/   ← not mentioned anywhere in README
governance/           ← not mentioned
Submission_Package/   ← not mentioned
```

The most substantial body of work (Phase 3.3 modeling) is invisible from the entry-point document.

### Prioritized Issues

| Priority | Issue | Fix |
|----------|-------|-----|
| P1 | Phase_3_3_Modeling/ not mentioned | Add "Statistical Modeling" section to README |
| P2 | Repository structure diagram incomplete | Add modeling, governance, submission, docs directories to diagram |
| P3 | Frozen/historical/active distinction missing | Add classification table or notes |
| P4 | Duplicated reproducibility info | Condense, cross-reference PIPELINE.md |
| P5 | Root test files not explained | Brief note: "manual development validation tools at root" |

### Recommendation: **Proceed** (moderate rewrite)

Update README to cover the full repository scope. Keep it concise — the current 99-line length is good. Add ~30-40 lines for the missing sections. Do not turn it into a full user manual; cross-reference PIPELINE.md and ARCHITECTURE_CONFORMANCE_REPORT.md for details.

---

## Proposal E — Documentation Humanization

### Classification

| Document | AI Pattern Severity | Impact | Recommendation |
|----------|-------------------|--------|----------------|
| `README.md` | Low — acceptable as-is | High (entry point) | **Minor wording improvements** — already mostly natural; just needs structural updates (Proposal D) |
| `PIPELINE.md` | Low — clear, concise | Medium (workflow doc) | **No changes needed** — effective as written |
| `ARCHITECTURE_CONFORMANCE_REPORT.md` | High — very formulaic | Low (internal audit artifact) | **Minor wording improvements** — this is an internal document with limited audience |
| `Phase_3_3_Modeling/Phase4_Freeze/*.md` | Medium | Low (frozen artifacts) | **No changes needed** — frozen, do not modify |
| `governance/*.md` | Medium-High in later phases | Low (historical) | **No changes needed** — historical, not actively read |
| `docs/INSTANCE_FEATURES.md` | Low — technical spec | Low | **No changes needed** |

### Recommendation: **Defer**

The only document with both high impact and need for change is `README.md` — and its primary issue is structural incompleteness (Proposal D), not AI writing patterns. The AI-patterned internal documents (governance, architecture report) have limited audiences. Humanizing them provides low return.

If any document warrants humanization, it is the `ARCHITECTURE_CONFORMANCE_REPORT.md` due to its formulaic structure being most noticeable to reviewers, but this is a Phase 4 audit artifact, not a long-term repository document.

---

## Executive Summary

| Proposal | Recommendation | Rationale |
|----------|---------------|-----------|
| **A** — Move root Java files | **Proceed with modifications** | Delete dead code (CompareBound.java, TestIsolate.java); leave validation tools in place; update README to mention them |
| **B** — Modify build_tables.py | **Reject** | Script is inside frozen Submission_Package; path works; no defect. Do not modify |
| **C** — Relocate governance/ | **Reject** | 42 reference updates for zero automation benefit; documents are self-contained |
| **D** — Update README | **Proceed** | Phase_3_3_Modeling/ completely invisible from entry point; this is a genuine discoverability defect |
| **E** — Humanize documentation | **Defer** | README's issue is structural, not stylistic; AI patterns in internal docs have limited audience |

### Proposed Execution Order (No Changes Yet)

1. **D** — README update (highest impact, closes discoverability gap)
2. **A sub-task** — Delete dead code (CompareBound.java, TestIsolate.java)
3. **A sub-task** — Brief README note about root validation tools
4. **E** — README humanization (incidental to structural update)
