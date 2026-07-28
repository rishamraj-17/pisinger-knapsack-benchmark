# Phase 4 Redundancy Report

## Identified Redundancies

1. **Coefficient Tables**
   - `full_sample_coefs_*_M2.csv` vs `std_beta_*_M2.csv`.
   - *Recommendation:* Use `std_beta_*_M2.csv` as the canonical source for Feature Importance, as unstandardized coefficients are difficult to compare across scales. 

2. **Cross-Validation Metrics**
   - `cv5_folds_*.csv` and `lofo_folds_*.csv` contain fold-level details, but `ols_metrics_aggregated.csv` aggregates them.
   - *Recommendation:* Use aggregated CSVs as the canonical source for the main text tables. Reserve fold-level CSVs for supplementary variance reporting.

3. **Inference vs Metrics**
   - `ols_inference_aggregated.csv` contains p-values and SEs, while `ols_metrics_aggregated.csv` contains R^2/RMSE.
   - *Recommendation:* Keep separate; use metrics for Section 2 (Performance) and inference for Supplementary Tables.

4. **Assumption Summaries vs Separate CSVs**
   - `max_vif` is reported in `assumption_summary_*.txt`, but we also have full `vif_*.csv` tables.
   - *Recommendation:* Use `vif_thinned_delta_r2_comparison.csv` for the main text, keep `vif_*.csv` as supplementary.
