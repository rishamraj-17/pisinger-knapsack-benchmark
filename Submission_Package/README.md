# Submission Package — README

## Overview

This package contains the complete submission materials for:

**Title:** The Predictive Value of Internal Execution Metrics in the Multidimensional Knapsack Problem

---

## Package Contents

```
Submission_Package/
├── manuscript.tex        # Main LaTeX manuscript (Sections 1-7 + front matter)
├── references.bib        # BibTeX bibliography (6 entries)
├── assemble_latex.py     # Script that generated manuscript.tex from section fragments
├── build_tables.py       # Script that generated tables from frozen evidence CSVs
├── figures/
│   ├── Figure_1.png      # Feature Importance Profile (B&B log_nodes_explored)
│   ├── Figure_2.png      # Elastic-Net Regularization Paths across LOFO folds
│   └── Figure_3.png      # Assumption Checks: Residuals vs. Fitted (B&B log_time)
├── tables/
│   ├── Table_1.tex       # Execution predictor counts by algorithm
│   ├── Table_2.tex       # OLS M1/M2 full-sample R² values
│   ├── Table_3.tex       # Fractional Logit pseudo-R² values
│   └── Table_4.tex       # Top-10 standardized β coefficients (B&B nodes)
└── supplementary/
    ├── ols_metrics_aggregated.csv           # Primary OLS evidence source
    ├── flogit_metrics_aggregated.csv        # Primary Fractional Logit evidence
    ├── vif_thinned_delta_r2_comparison.csv  # VIF robustness audit (D01/D02)
    ├── std_beta_BandB_log_nodes_explored_M2.csv  # Standardized β evidence (F01)
    ├── Phase4_Claim_Inventory.md            # Frozen claim registry
    └── Paper_Blueprint.md                   # Blueprint v8.1 governance document
```

---

## How to Build

### 1. Prerequisites

- LaTeX distribution (TeX Live or MiKTeX) with `booktabs`, `natbib`, `hyperref` packages
- Python 3.x with `pandas`

### 2. Regenerate Tables (if needed)

```bash
python3 build_tables.py
```

This reads the frozen evidence CSVs in `supplementary/` and regenerates `tables/Table_*.tex`.

### 3. Assemble the Manuscript (if needed)

```bash
python3 assemble_latex.py
```

This reads the validated manuscript sections and produces `manuscript.tex`.

### 4. Compile the Manuscript

```bash
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

---

## Reproducibility Notes

All figures, tables, and statistics in the manuscript trace directly to the
frozen evidence CSVs in the `supplementary/` directory. The benchmark dataset
was generated with `random_seed = 42` using the Pisinger (2005) methodology
for 6,000 knapsack instances across 6 structural families. Software versions
and hardware configurations are documented in the Reproducibility Appendix
(Section A of the manuscript).

## Evidence Traceability

| Manuscript Claim         | Evidence Artifact                                    |
|--------------------------|------------------------------------------------------|
| R² (M1, M2) values       | `ols_metrics_aggregated.csv` (full_sample rows)     |
| Pseudo-R² values         | `flogit_metrics_aggregated.csv` (full_sample rows)  |
| ΔR² VIF robustness       | `vif_thinned_delta_r2_comparison.csv`               |
| Standardized β rankings  | `std_beta_BandB_log_nodes_explored_M2.csv`          |
| Claim definitions        | `Phase4_Claim_Inventory.md`                         |
| Blueprint compliance     | `Paper_Blueprint.md`                                |
