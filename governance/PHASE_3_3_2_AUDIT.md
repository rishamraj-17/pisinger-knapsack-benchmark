# Phase 3.3.2 — OLS Models: Independent Audit

**Audit Date:** 2026-07-23
**Audited Files:**
- `utils/models.py` (146 lines)
- `scripts/2a_fit_ols.py` (555 lines)
- Supporting: `config.py`, `utils/metrics.py`, `utils/cv.py`, `utils/preprocessing.py`

---

## 1. Executive Summary

Phase 3.3.2 fits M1 and M2 for all 5 OLS responses across 3 algorithms using statsmodels OLS, with LOFO CV, 5-fold CV, full-sample inference, bootstrap ΔR² CI, and back-transformed RMSE. The implementation is substantially correct and follows the frozen design documents faithfully.

**Verdict: PASS — Proceed to Phase 3.3.3**

No critical or major issues found. Minor findings documented below.

---

## 2. Methodology Compliance

| Design Requirement | Status | Evidence |
|---|---|---|
| statsmodels OLS used | ✅ | `utils/models.py:12-13` — `sm.OLS(y, X).fit()` |
| Intercept added | ✅ | `sm.add_constant(..., has_constant='add')` |
| **LOFO CV** — 5 folds, one family held out | ✅ | `utils/cv.py:16-31` — iterates over `FAMILIES`, holds out one per fold |
| **5-fold CV** — stratified by family×cap_mode | ✅ | `utils/cv.py:37-65` — `StratifiedKFold` on `family_capacity_mode` composite |
| **Unscaled predictors in CV** | ✅ | `build_feature_matrices` returns unscaled data; no scaler applied before `fit_ols` in CV loops |
| **Standardised β via separate scaled pipeline** | ✅ | `utils/models.py:82-100` — separate function, scales data independently, never leaks into CV |
| **Cluster-robust SEs by instance_id** | ✅ | `utils/models.py:54-61` — `get_robustcov_results(cov_type='cluster', groups=instance_id)` |
| **Incremental F-test** | ✅ | `utils/models.py:64-79` — formula matches §7.6: F = [(RSS₁−RSS₂)/(p₂−p₁)] / [RSS₂/(n−p₂)] |
| **Cohen's f²** | ✅ | `utils/metrics.py:62-66` — formula matches: (R²₂−R²₁)/(1−R²₂) |
| **Bootstrap ΔR²** — 1999 resamples, stratified by family | ✅ | `utils/models.py:110-146` — stratified by family, fits M1+M2 per resample, percentile CI |
| **Duan's smearing** — pooled + family-specific | ✅ | `utils/metrics.py:69-85` — computes both; pooled used for back-transformed RMSE |
| **Back-transformed RMSE** | ✅ | `utils/metrics.py:88-97` — formula matches: √(Σ(exp(yᵢ)−exp(ŷᵢ)·φ)²/n) |
| **All outputs saved per plan** | ✅ | 12 metrics CSV, 10 CV fold CSV, 10 coefficient CSV, 5 std-beta CSV, 2 aggregated CSV |
| **95% CI using t₄ for LOFO** | ✅ | `_aggregate_cv_metrics` uses `t.ppf(0.975, df=n_folds-1)` with df=4 |

### Predictor Exclusions Verified

All model-specific exclusions from §4.6 of the design document are correctly enforced:

| Model | Forbidden Predictors | Status |
|---|---|---|
| DP `log_memory_mb` | `cells_allocated`, `nonzero_value_states`, `zero_value_states` | ✅ Absent from M2 |
| DP `fill_rate` (not OLS) | `fill_rate`, `cells_allocated`, `nonzero_value_states` | ✅ N/A (Phase 3.3.3) |
| B&B `log_time_millis` | `mean_bound`, `max_bound`, `min_bound` | ✅ Absent from M2 |
| B&B `log_nodes_explored` | `nodes_generated`, `internal_nodes`, `mean_bound`, `max_bound`, `min_bound` | ✅ Absent from M2 |

Correlation block pre-filter (design §6.3) applied in Phase 3.3.1: `cells_allocated`, `nonzero_value_states`, `capacity_density`, `solution_density`, `cell_value_variance`, `include_count` dropped from all algorithm subsets.

---

## 3. Statistical Correctness

### 3.1 Parameter Counts

| Model | M1 (expected) | M2 (expected) | M2 (actual) | Match |
|---|---|---|---|---|
| Greedy `log_time_millis` | 42 (35 + 7 design) | 47 (42 + 5 Greedy metrics) | 47 | ✅ |
| DP `log_time_millis` | 42 | 52 (42 + 10 DP metrics after block filter) | 52 | ✅ |
| DP `log_memory_mb` | 42 | 51 (42 + 9 DP metrics after block filter + exclusions) | 51 | ✅ |
| B&B `log_time_millis` | 42 | 66 (42 + 24 BB metrics after exclusions) | 66 | ✅ |
| B&B `log_nodes_explored` | 42 | 64 (42 + 22 BB metrics after exclusions) | 64 | ✅ |

All M2 counts match expectations after accounting for global exclusions (9 dropped from B&B, 5 from DP, 1 from Greedy) and block-4 exclusions (3 from B&B).

### 3.2 Spot Check — PASS

**Greedy `log_time_millis` M1 full-sample R² = 0.857 > 0.8** ✅

### 3.3 Nested F-test Verification

The F-statistic formula was verified against design §7.6:
- Formula: F = [(RSS₁−RSS₂)/(p₂−p₁)] / [RSS₂/(n−p₂)]
- Implementation: `((ssr_reduced - ssr_full) / delta_df) / (ssr_full / df_resid_full)` where `delta_df = df_resid_reduced - df_resid_full = p₂−p₁` ✅
- p-values use `scipy.stats.f.cdf` ✅

### 3.4 Duan's Smearing Verification

The implementation matches §11.4:
- φ = (1/n) Σ exp(eᵢ) where eᵢ are log-scale residuals ✅
- Back-transformed RMSE = √(Σ(exp(yᵢ) − exp(ŷᵢ)·φ)² / n) ✅
- Both pooled and family-specific φ computed ✅

---

## 4. Code Quality

| Category | Finding | Severity |
|---|---|---|
| Dead code | `run_ols_pipeline` assigns `cr_coefs_m2 = full["coefs_m2"]` correctly but also had `model_m2_obj = full["model_m2"]` that was removed; no dead code remains | ✅ None |
| Exception handling | Descriptive error messages when prepared data not found, when columns missing from df in `build_feature_matrices` | ✅ Good |
| Reproducibility | `RNG = np.random.default_rng(RANDOM_SEED)` (seed=42) used for bootstrap; `StratifiedKFold` uses `random_state=RANDOM_SEED` | ✅ |
| NaN handling | Log-scale `y` may have NaN if `raw_response` contains NaN; the pipeline drops NaN rows with a warning | ✅ Safe |
| Hidden assumptions | `predict_ols` re-adds constant; assumes `has_constant='add'` works (confirmed with explicit parameter) | ✅ Fixed during implementation |
| Cluster-robust SE handling | `get_robustcov_results` in statsmodels 0.14.6 returns ndarray params; `ols_coefficients` correctly handles both Series and ndarray cases | ✅ Robust |

### Known statsmodels Version Behavior

In statsmodels 0.14.6, `get_robustcov_results()` returns all attributes (`params`, `bse`, `tvalues`, `pvalues`, `conf_int()`) as numpy arrays without pandas index names. The `ols_coefficients` function correctly detects this and uses supplied `predictor_names` from the original model. This is **documented** and handled correctly.

---

## 5. Result Validation

### 5.1 Full-sample vs CV R²

| Model | Full R² | 5-fold CV R² | LOFO R² | Notes |
|---|---|---|---|---|
| Greedy `log_time` M1 | 0.857 | 0.855 | -4.657 | LOFO poor on Uncorrelated family (expected per design §8.1) |
| Greedy `log_time` M2 | 0.859 | 0.856 | -5.069 | M2 adds negligible improvement |
| DP `log_time` M1 | 0.978 | 0.977 | 0.631 | |
| DP `log_time` M2 | 0.979 | 0.979 | 0.810 | |
| DP `log_memory` M1 | 0.015 | 0.005 | -107.6 | Very low R²; expected (exploratory) |
| DP `log_memory` M2 | 0.016 | 0.002 | -110.4 | No improvement; bootstrap CI includes zero |
| B&B `log_time` M1 | 0.745 | 0.740 | 0.480 | |
| B&B `log_time` M2 | 0.961 | 0.340* | -0.174 | ⚠ **See §5.1.1** |
| B&B `log_nodes` M1 | 0.736 | 0.732 | 0.391 | |
| B&B `log_nodes` M2 | 0.980 | 0.978 | -0.440 | |

**§5.1.1 B&B `log_time` M2 5-fold CV anomaly:** The reported mean R² of 0.340 is driven by a single catastrophic fold (fold 1: R² = -2.12). The median across 5 folds is 0.952. Fold-level inspection reveals no data error — this is a genuine manifestation of B&B's sensitivity to the specific train/test split. The LOFO CV (structurally harder) shows mean R² = -0.174 with median 0.795. When reported, both mean and median should be presented.

### 5.2 Negative LOFO R² — Expected

Several models show negative LOFO R². This is a **feature, not a bug** per design §8.1:
> "LOFO may understate predictive performance for families with similar structure... This is a feature, not a bug — it provides a conservative generalization estimate."

The Uncorrelated family is particularly hard for Greedy (R² = -26.2), and AlmostEqualRatios is hard for B&B (R² = -4.1 for M2).

### 5.3 No Singular Matrices or Convergence Errors

All 5 models converged without warnings. All coefficient estimates are finite. No VIF-related warnings were raised (VIF diagnostic not implemented in this phase — planned for Phase 3.3.5).

### 5.4 No NaN/Inf in Meaningful Metrics

The NaN values in the CSV output are a structural artifact: CV rows have `_mean`/`_sd` columns NaN, and full-sample rows have individual `r_squared` columns NaN. No meaningful metric is NaN.

---

## 6. Minor Findings

### 6.1 Output CSV Schema Ambiguity

The metrics CSV files combine CV means/SD/CIs and full-sample metrics in a single table with disjoint columns (CV rows have NaN for full-sample columns and vice versa). This is functional but could be clearer as separate tables. **Action:** Consider splitting into separate CV-only and full-sample-only CSV files in a future revision. No change required for Phase 3.3.3.

### 6.2 B&B 5-fold CV Mean Misleading

The B&B `log_time_millis` M2 5-fold CV R² mean (0.340) is misleading due to one catastrophic fold. The median (0.952) better represents typical performance. **Action:** Report median alongside mean in Phase 3.3.6 (reporting stage). Not a code defect.

### 6.3 Back-transformed RMSE Notes

For B&B `log_nodes_explored`, the back-transformed RMSE values are very large (15M–72M nodes). This is expected given:
- Nodes range from 1 to 50M (6+ orders of magnitude)
- Log-transformation compresses this range; back-transformation re-expands it
- A small log-scale RMSE (e.g., 2.0 on log-scale) becomes a large RMSE on the original scale
- The smearing factor φ = 7.7–8.8 further inflates the back-transformed values

This is mathematically correct behavior.

### 6.4 Small ΔR² for Greedy and DP `log_time`

Both Greedy and DP show very small ΔR²_adj (0.001) from adding execution metrics. While statistically significant (F-test p < 0.001), the effect sizes (Cohen's f² = 0.01–0.06) are small. This is a genuine finding consistent with the design expectation that instance characteristics dominate.

---

## 7. Verification Evidence

All verification tests passed:
1. ✅ LOFO uses exactly 5 family folds (verified across all 5 models)
2. ✅ 5-fold CV uses stratified family×cap_mode folds
3. ✅ Forbidden predictors absent from all M2 specifications
4. ✅ Greedy M1 R² > 0.8 (spot check: 0.857)
5. ✅ 1999 bootstrap resamples completed for all models
6. ✅ All 5 OLS models converge without warnings
7. ✅ Standardised β computed on scaled data, separate from CV
8. ✅ Cluster-robust SEs grouped by instance_id
9. ✅ All 10 required output CSV files exist per model
10. ✅ No code exceptions during execution

---

## 8. Recommended Actions Before Phase 3.3.3

1. **None required.** Phase 3.3.2 is frozen and approved.

---

## 9. Conclusion

**Phase 3.3.2 is approved and frozen.**

All completion criteria from the implementation plan are satisfied:
- [x] All 5 OLS models complete without convergence errors
- [x] LOFO and 5-fold CV metrics are available per fold
- [x] Full-sample coefficients with cluster-robust SEs are saved
- [x] Incremental F-test p-values are computed for each pair
- [x] Bootstrap ΔR² CI computed: 1999 resamples, stratified by family, percentile CI reported
- [x] Standardised β computed from separate scaled-only pipeline
- [x] Back-transformed RMSE with Duan's smearing reported
- [x] Spot-check: Greedy `log_time_millis` M1 R² = 0.857 > 0.8

**Recommendation: Proceed to Phase 3.3.3 (Fractional Logit Models).**
