# Independent Adversarial Repository Inspection Report

**Repository:** Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics
**Date:** 2026-07-28
**Inspector:** Independent external reviewer (no prior knowledge of this repository)

---

## 1. Reproducibility

### Finding 1.1 — The submitted manuscript cannot be reproduced from the repository (CRITICAL RELEASE BLOCKER)

**Evidence:** `Submission_Package/assemble_latex.py:3` contains:
```python
ARTIFACT_DIR = "/home/risham-raj-byahut/.gemini/antigravity/brain/cbb6daa1-05c2-4856-99ca-e19d4507cba1"
```
This is a hardcoded absolute path to a Google Gemini AI artifact directory outside the repository. The script reads seven section files (`paper_draft_pass2_section1.md` through `section7.md`) from this external location. On a fresh clone, this path does not exist and the manuscript cannot be assembled. The section fragment files are not present anywhere in the repository. An external researcher cannot regenerate `manuscript.tex` from repository contents.

### Finding 1.2 — `build_tables.py` uses a path deleted by the latest commit (CRITICAL RELEASE BLOCKER)

**Evidence:** `Submission_Package/build_tables.py:6`:
```python
ARCHIVE = "/home/risham-raj-byahut/IdeaProjects/Emperical_Comparision/Phase_3_3_Modeling/Phase3_Archive/output"
```
Commit `8f526ec` ("Phase 4: Repository engineering") deleted the entire `Phase3_Archive/` directory from git tracking:
```
D	Phase_3_3_Modeling/Phase3_Archive/CONTINUE_FROM_HERE.md
D	Phase_3_3_Modeling/Phase3_Archive/PIPELINE.md
D	Phase_3_3_Modeling/Phase3_Archive/README.md
[...13 more deletions in Phase3_Archive]
```
On a fresh clone, `Phase3_Archive/` does not exist. `build_tables.py` will fail with `FileNotFoundError`. The tables in `Submission_Package/tables/` exist as pre-generated artifacts, but the script that generated them is broken.

### Finding 1.3 — `build_tables.py` also uses a hardcoded absolute path (MEDIUM)

**Evidence:** `Submission_Package/build_tables.py:4`:
```python
OUT_DIR = "/home/risham-raj-byahut/IdeaProjects/Emperical_Comparision/Submission_Package/tables"
```
This is a hardcoded absolute path. The script works on the author's machine but will fail on any other machine without modification.

### Finding 1.4 — Phase_3_3_Modeling pipeline dependencies are undocumented (HIGH)

**Evidence:** The modeling scripts import `statsmodels` (`2b_fit_fractional_logit.py:292`, `4_diagnostics.py:8`), `scipy` (`2a_fit_ols.py:9`, `2b_fit_fractional_logit.py:13`), `sklearn` (`2c_fit_elasticnet.py:14`, `2d_fit_hurdle.py:13`), `pandas`, and `numpy`. There is no `requirements.txt`, `pyproject.toml`, `setup.py`, or any dependency file for Python packages. The README says "see `Phase_3_3_Modeling/.venv/`" but a virtual environment is not a dependency specification — it is a local, non-portable directory (`lib/python3.14/site-packages/`). An external researcher cannot determine which package versions are required.

### Finding 1.5 — `reproduce.sh` does not cover the full pipeline (HIGH)

**Evidence:** `reproduce.sh` runs the Java benchmark and `analyze.py`, producing tables and figures for the benchmark comparison. It does **not** execute the Phase_3_3_Modeling statistical pipeline (scripts `1_prepare_data.py` through `4_diagnostics.py`), does **not** run `DatasetIntegrationRunner.java` to produce `canonical_dataset.csv`, and does **not** run `Submission_Package/build_tables.py` or `Submission_Package/assemble_latex.py`. A researcher running `./reproduce.sh` gets only part of the repository's output.

### Finding 1.6 — `full_experiment.csv` seed column is misleading (DOCUMENTATION IMPROVEMENT)

**Evidence:** `PIPELINE.md:145` states "Seeds per (n, family): 100". However, `full_experiment.csv` has only one unique seed value (`42`) across all 18,000 rows. The data does contain 100 instances per (n, family) combination, but they are distinguished by `instance_id` (0-99), not by seed. A researcher expecting 100 distinct seeds would be confused.

---

## 2. Repository Consistency

### Finding 2.1 — Two different papers exist in the repository (CRITICAL RELEASE BLOCKER)

**Evidence:** `paper/draft.md` is titled **"Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics"** and describes a benchmark comparison of Greedy, DP, and B&B across Pisinger families. The submitted manuscript at `Submission_Package/manuscript.pdf` and `Submission_Package/manuscript.tex` is titled **"The Predictive Value of Internal Execution Metrics in the Multidimensional Knapsack Problem"** and describes a statistical modeling study of internal execution metrics using OLS, fractional logit, elastic-net, and hurdle models. These are different research papers with different research questions, different methodologies, and different scopes. The term "multidimensional knapsack" appears 0 times in `paper/draft.md` but appears throughout the submission manuscript. An external researcher cannot determine which paper this repository supports.

### Finding 2.2 — `Phase3_Archive` was git-deleted but the directory persists on disk (ENGINEERING IMPROVEMENT)

**Evidence:** Commit `8f526ec` deleted `Phase3_Archive/` from git. The directory still exists on disk because it was not physically removed. A fresh clone will not have this directory. `build_tables.py` (Finding 1.2) and possibly other scripts reference this path.

### Finding 2.3 — Commit history shows non-reproducible development practices (HISTORICAL ARTIFACT)

**Evidence:** Git log contains commits titled `"feat : Completed intended workflow"`, `"Merge pull request #2 from rishamraj-17/yolo-branch"`, `"Cleanup after opencode keeps crashing due to memoy exhaust"` (note typo), `"Fixed reference issues : ft. antigravity"`, and phase numbering that cycles (Phase 7 → Phase 6 → Phase 5 → Phase 2 → Phase 3 → Phase 2). This indicates an AI-assisted development process where the repository was built through iterative agent prompts rather than conventional software engineering. While not a release blocker per se, it undermines confidence in the provenance of scientific outputs.

---

## 3. Documentation Quality

### Finding 3.1 — The submission manuscript title does not match any documentation (CRITICAL RELEASE BLOCKER)

**Evidence:** The README, PIPELINE.md, CITATION.cff, and the architecture review all use the title **"Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics"**. The submission manuscript uses **"The Predictive Value of Internal Execution Metrics in the Multidimensional Knapsack Problem"**. No documentation explains this discrepancy. There is no document describing how these two papers relate.

### Finding 3.2 — Phase_3_3_Modeling pipeline has no top-level documentation (HIGH)

**Evidence:** The README mentions the Phase_3_3 directory but does not explain how to execute its pipeline, what the execution order is (1→2a,2b,2c,2d→3→4), what the prerequisites are beyond "see .venv/", or how its outputs connect to the paper. The scripts themselves have minimal docstrings but no top-level orchestration.

### Finding 3.3 — `canonical_dataset.csv` vs `full_experiment.csv` confusion (DOCUMENTATION IMPROVEMENT)

**Evidence:** `PIPELINE.md` describes `full_experiment.csv` as the canonical output (18 columns). `Phase_3_3_Modeling/scripts/1_prepare_data.py:51` expects `canonical_dataset.csv` (110 columns) and validates `expected_cols == 110`. `docs/INSTANCE_FEATURES.md` documents 40 feature columns. The relationship between these files is documented in historical governance documents but not in any active README or PIPELINE.md.

---

## 4. Build and Execution

### Finding 4.1 — `DatasetIntegrationRunner.java` is never executed by any script (HIGH)

**Evidence:** `reproduce.sh` and `build_and_run.sh` do not run `DatasetIntegrationRunner`. The `canonical_dataset.csv` (110 columns, 39 MB) was generated at some point but the pipeline to regenerate it from the component CSVs requires a separate manual step not documented in any active README or execution script.

### Finding 4.2 — Shell scripts use `set -e` but have no error diagnostics (LOW)

**Evidence:** `reproduce.sh` and `build_and_run.sh` use `set -e` which is good practice. However, `build_and_run.sh` does not verify compilation success before running, and `reproduce.sh` does not verify each step before proceeding.

### Finding 4.3 — `build_and_run.sh` requires `curl` but does not check for it (LOW)

**Evidence:** `build_and_run.sh:23` uses `curl` to download `commons-csv` if missing. There is no check that `curl` is installed.

---

## 5. Codebase Integrity

### Finding 5.1 — `CompareBound.java` and `TestIsolate.java` were dead code, now deleted (VERIFIED STRENGTH)

**Evidence:** Commit `8f526ec` deleted `CompareBound.java` and `TestIsolate.java`, both of which were empty `main` methods. This was a correct cleanup action. Confirmed by git history.

### Finding 5.2 — Root-level validation Java files are acknowledged dead weight (ACCEPTABLE DESIGN DECISION)

**Evidence:** `README.md:64-66` explicitly documents five root-level `Test*.java` files as "manual development-time tools" with "no dependencies from any automated pipeline." This is acceptable — they are acknowledged, not hidden. However, they could be moved to `src/test/` or `tools/`.

### Finding 5.3 — `analyze_canonical.py` never committed as active (HISTORICAL ARTIFACT)

**Evidence:** Git log shows `analyze_canonical.py` was added in early commits and later replaced by `analyze.py`. Only `analyze.py` is current. No dead reference to `analyze_canonical.py` exists in active scripts.

### Finding 5.4 — Frozen output data is duplicated across Phase3_Freeze and Phase4_Freeze (MEDIUM)

**Evidence:** Both `Phase_3_3_Modeling/Phase3_Freeze/output/` and `Phase_3_3_Modeling/Phase4_Freeze/output/` contain identical-prepared pickle files (BandB.pkl, DP.pkl, Greedy.pkl) and similar diagnostic outputs. Commit `a06ba74` added Phase4_Freeze as a "frozen snapshot" duplicating most of Phase3_Freeze. This doubles the repository size with no documented reason for the duplication. The `.pkl` files alone are ~4.7 MB each × 3 × 2 copies = ~28 MB of duplicated binary data.

---

## 6. Scientific Integrity

### Finding 6.1 — The submission manuscript references a different problem domain than the repository (CRITICAL RELEASE BLOCKER)

**Evidence:** The submitted manuscript at `Submission_Package/manuscript.pdf` and `Submission_Package/manuscript.tex` studies **"The Predictive Value of Internal Execution Metrics in the Multidimensional Knapsack Problem"**. The repository generates data for the **0/1 knapsack problem** (single constraint), not the multidimensional knapsack problem (multiple constraints). The algorithm implementations (`BranchAndBound.java`, `DynamicProgramming.java`, `Greedy.java`) all solve the standard 0/1 knapsack. If the submission manuscript claims to study the multidimensional knapsack, it is making a false claim about the experimental setup. If it studies the 0/1 knapsack, its title is incorrect. Either way, this is a fundamental integrity issue.

### Finding 6.2 — Evidence traceability for submission manuscript is plausible but not independently verifiable (MEDIUM)

**Evidence:** The `Submission_Package/supplementary/` CSVs appear to have been generated by the Phase_3_3_Modeling pipeline. For example, `ols_metrics_aggregated.csv` corresponds to `Phase_3_3_Modeling/output/results/ols_metrics_aggregated.csv`. The frozen supplemental files in the submission package have matching structure. However, because the Phase_3_3 pipeline cannot be executed on a fresh clone (Finding 1.4) and `canonical_dataset.csv` generation is not scripted (Finding 4.1), an external researcher cannot independently verify that these numbers were produced by the repository code.

### Finding 6.3 — Frozen artifacts in Submission_Package/ show signs of manual curation (LOW)

**Evidence:** `Submission_Package/tables/Table_1.tex` has hardcoded numbers (5, 10, 24 predictors) rather than being generated from data. `build_tables.py` does regenerate Tables 2-4 from CSVs but Table 1 is handwritten. This is acceptable for a frozen submission but means Table 1 cannot be independently verified.

---

## 7. Release Readiness

### Finding 7.1 — A first-time visitor would be confused by the paper duality (CRITICAL RELEASE BLOCKER)

**Evidence:** The README says the paper is at `paper/draft.md` about knapsack algorithm comparison. The `Submission_Package/manuscript.pdf` is about statistical modeling of execution metrics. A visitor clicking the submission package README expecting to find the paper described in the top-level README will find a different paper. There is no document explaining that the repository evolved from a benchmark study into a statistical modeling paper, or that the submission package represents a different publication.

### Finding 7.2 — Repository has no `requirements.txt`, `Makefile`, Docker, or CI configuration (MEDIUM)

**Evidence:** There is no `requirements.txt` for Python, no `Makefile`, no Dockerfile, no `.travis.yml`, no `.github/workflows/`. The Python dependencies are only discoverable by reading import statements. A researcher must manually install packages.

### Finding 7.3 — Phase_3_3_Modeling .venv/ is committed/present but should not be in release (ENGINEERING IMPROVEMENT)

**Evidence:** The `.venv/` directory contains a full Python virtual environment with `lib/python3.14/site-packages/`. This is platform-specific binary content. It should be replaced by a `requirements.txt` and excluded from any release.

---

## Summary of Classified Findings

| # | Finding | Classification |
|---|---------|---------------|
| 1.1 | `assemble_latex.py` hardcoded Gemini artifact path — manuscript cannot be regenerated | **Critical Release Blocker** |
| 1.2 | `build_tables.py` references `Phase3_Archive/` deleted from git — tables cannot be regenerated | **Critical Release Blocker** |
| 2.1 / 6.1 | Two different papers with different titles and research questions exist | **Critical Release Blocker** |
| 1.4 | Modeling pipeline dependencies undocumented (statsmodels, sklearn, scipy, etc.) | **High Priority Issue** |
| 1.5 | `reproduce.sh` does not cover full pipeline | **High Priority Issue** |
| 3.2 | Phase_3_3_Modeling execution workflow undocumented | **High Priority Issue** |
| 4.1 | `DatasetIntegrationRunner` never executed by any script | **High Priority Issue** |
| 1.3 | `build_tables.py` hardcoded absolute path | **Medium Priority Issue** |
| 5.4 | Duplicated frozen binary data (~28 MB) across Phase3_Freeze/Phase4_Freeze | **Medium Priority Issue** |
| 7.2 | No dependency specification or CI configuration | **Medium Priority Issue** |
| 1.6 | Seed column documentation mismatch | **Documentation Improvement** |
| 3.3 | canonical_dataset vs full_experiment.csv relationship undocumented | **Documentation Improvement** |
| 5.2 | Root-level Test*.java files acknowledged but unorganized | **Acceptable Design Decision** |
| 5.1 | Dead code cleanup (CompareBound, TestIsolate deletion) | **Verified Strength** |

---

## Release Decision

# REJECT FOR PUBLIC RELEASE

**Rationale:** Three Critical Release Blockers independently justify rejection:

1. **Irreproducible submission manuscript.** The LaTeX manuscript is assembled from AI-generated fragments stored outside the repository at a hardcoded absolute path (`/home/risham-raj-byahut/.gemini/antigravity/brain/...`). An external researcher cannot regenerate `manuscript.tex` from repository contents alone. Additionally, the submission tables are generated via a script referencing a git-deleted directory (`Phase3_Archive/`).

2. **Two conflicting papers.** The repository simultaneously claims to support a benchmark comparison paper (`paper/draft.md`: "Knapsack Optimization: An Experimental Study...") and a statistical modeling paper (`Submission_Package/manuscript.tex`: "The Predictive Value of Internal Execution Metrics in the Multidimensional Knapsack Problem"). These are different research artifacts with different titles, different research questions, and different claims. The submission manuscript further claims to study the "Multidimensional Knapsack Problem" while the repository implements only the single-constraint 0/1 knapsack. An external reviewer would conclude the repository lacks a coherent narrative.

3. **No path to verification.** The three critical issues (unreproducible manuscript, unreproducible tables, paper identity confusion) mean that even after fixing minor issues, the scientific integrity of the repository's outputs cannot be independently verified. The inspection cannot determine whether the submission manuscript's numerical results were actually produced by the code in this repository, because the regeneration pathway is broken.

**Required actions before release are possible:**
- Remove or replace `assemble_latex.py` and `build_tables.py` with scripts that work from repository contents
- Resolve the paper identity: either remove the submission package and document it as a separate project, or align all documentation and the submission package under one coherent title
- Document and script the full pipeline from benchmark generation through statistical modeling through manuscript assembly
- Add `requirements.txt` for Python dependencies
- Remove or document the Phase3_Freeze/Phase4_Freeze duplication

No optional improvements are listed above. Only the issues that genuinely block release are enumerated.