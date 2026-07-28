# Phase 4 Evidence Coverage Audit

## Audited Categories

1. **OLS** (Phase 3.3.2)
   - `ols_metrics_aggregated.csv` -> Mapped (Performance)
   - `cv5_folds_*.csv` -> Mapped (Performance)
2. **Fractional Logit** (Phase 3.3.3)
   - `flogit_metrics_aggregated.csv` -> Mapped (Performance)
3. **Elastic-Net** (Phase 3.3.4)
   - `lofo_folds_elasticnet.csv` -> Mapped (Performance)
4. **Hurdle**
   - Not present (intentionally excluded per governance).
5. **Feature Importance** (Phase 3.3.5)
   - `std_beta_*.csv`, `*_permutation_importance.csv` -> Mapped (Feature Importance)
   - `importance_*.png` -> Mapped (Feature Importance)
6. **Diagnostics** (Phase 3.3.6)
   - `vif_thinned_delta_r2_comparison.csv` -> Mapped (Diagnostics)
   - `smearing_factors.csv` -> Mapped (Diagnostics)
   - `assumption_summary_*.txt` -> Mapped (Diagnostics)
   - `zero_event_families.txt` -> Mapped (Dataset/Methodology)

## Missing/Flagged Elements
- `full_sample_coefs_*.csv` are generated but heavily overlapping with `std_beta_*.csv`. We recommend using `std_beta` for interpretation.
- `se_comparison_*.csv` (cluster-robust vs classical standard errors) is present but currently unmapped to a specific claim. *Recommendation:* Add a claim under Diagnostics regarding Standard Error adjustments.
- `residual_tests_ols.csv` is present but unmapped. *Recommendation:* Map to Diagnostics.
- `correlation_verification_*.csv` is unmapped. *Recommendation:* Map to Methodology/Diagnostics (multicollinearity check).
