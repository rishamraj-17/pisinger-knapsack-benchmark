# Continue From Here

**Generated:** 2026-07-25  
**Phase:** 3.3.3 completed — Phase 3.3.4 is next

---

## Current State

- **Phase 3.3.3 (Fractional Logit) is DONE.** Memory leak is fixed with `gc.collect()` in `_fast_pseudo_r2()` (`utils/models.py:177-191`) and in the LOFO loop (`scripts/2b_fit_fractional_logit.py`). Validated across 3 runs: RSS bounded at ~1.5GB peak, outputs bit-for-bit identical.
- **Phase 3.3.1 (Foundation)** and **Phase 3.3.2 (OLS)** are also complete.
- **Phases 3.3.4–3.3.8 are not started.** Files for `2c`, `2d`, `3`, `4`, `5`, `6` scripts and `importance.py`, `diagnostics.py` utils do not exist yet.

---

## To Continue (in order)

### 1. Phase 3.3.4 — Elastic-Net & Hurdle Models
Create two new scripts and extend `utils/models.py`:

**Files to create:**
- `scripts/2c_fit_elasticnet.py` — B&B `optimal` response, elastic-net logistic, exploratory
- `scripts/2d_fit_hurdle.py` — B&B `solution_gap`, two-part hurdle, supplementary

**Files to modify:**
- `utils/models.py` — Add `fit_elasticnet()` (sklearn `LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5)` with `GridSearchCV` for C tuning, nested within LOFO) and `fit_hurdle()` (two-part: logistic + fractional logit)

**Key constraints:**
- Nested CV: LOFO outer (5 families) → 5-fold internal CV for λ selection → 1-SE rule
- Zero-event families: `Uncorrelated` may have 0 incomplete runs → Brier score only, no AUC
- `config.py` already has MODEL_SPECS entries for both models; reuse `build_feature_matrices()` from `preprocessing.py`
- sklearn does NOT want a `const` column (unlike statsmodels). Check `build_feature_matrices` handles this or add a flag.

### 2. Phase 3.3.5 — Feature Importance
- Create `utils/importance.py` with: `permutation_importance()`, `delta_r2_partitioning()`, `elasticnet_nonzero_coefs()`
- Create `scripts/3_compute_importance.py`
- Standardized β already computed in `2a`/`2b` (outputs in `output/diagnostics/std_beta_*.csv`)

### 3. Phase 3.3.6 — Diagnostics
- Create `utils/diagnostics.py` with: `vif()`, `link_test()`, `partial_residual_plot()`, `qq_plot()`, `cooks_distance()`, `calibration_curve()`
- Create `scripts/4_diagnostics.py`

### 4. Phase 3.3.7 — Sensitivity
- Create `scripts/5_sensitivity.py` for capacity-mode stratified, B&B complete-only, family-level breakdowns

### 5. Phase 3.3.8 — Summarization
- Create `scripts/6_summarize.py` for BH adjustment, LaTeX tables, `master_results.csv`

---

## Useful Commands

```bash
# Activate environment
source Phase_3_3_Modeling/.venv/bin/activate

# Run Phase 3.3.4 (once written)
python Phase_3_3_Modeling/scripts/2c_fit_elasticnet.py

# Verify existing outputs
ls Phase_3_3_Modeling/output/results/
ls Phase_3_3_Modeling/output/cross_validation/
```

## Key Configuration
- All column lists, exclusions, model specs: `Phase_3_3_Modeling/config.py`
- Design document: `governance/PHASE_3_3_IMPLEMENTATION_PLAN.md`
- Frozen statistical design: `governance/PHASE_3_2_DESIGN.md`
- Detailed project state: `governance/PROJECT_STATE_REPORT.md`
