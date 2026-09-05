# Phase 3.2 — Second Independent Design Audit

**Audit of:** `governance/PHASE_3_2_DESIGN.md` (Revised, 816 lines)
**Prior Audit:** `governance/PHASE_3_2_AUDIT.md` (441 lines)
**Changelog:** `governance/PHASE_3_2_REVISION_CHANGELOG.md` (71 lines)
**Date:** 2026-07-21
**Role:** Second independent auditor (fresh review of revised document)

---

## Executive Summary

**Verdict: REVISE BEFORE IMPLEMENTATION**

The revision successfully resolves all 4 major issues (M1–M4), all 6 minor issues (m1–m6), and all 10 documentation gaps (d1–d10) from the first audit. The core research architecture is sound, and the revisions to §4.6 (model-specific exclusions), §7.2 (per-model tables), §7.4 (fractional logit rationale), and §7.5 (elastic-net rationale) are thorough and well-justified.

**However, one new critical issue was introduced by the revision itself:** the DP `fill_rate` supplementary response has a near-circular relationship with its own M2 predictors. `cells_allocated` and `nonzero_value_states` (deterministic components of `fill_rate`) are not excluded from the predictor set, and `fill_rate` may be included as a predictor of itself. This is directly analogous to the original M1 issue and makes the `fill_rate` model's ΔR² uninterpretable.

Additionally, 7 minor issues remain — none individually blocking, but collectively requiring attention before implementation.

---

## 1. Verification of Original Audit Findings

### 1.1 Major Issues (M1–M4) — ALL RESOLVED

| ID | Finding | Resolution | Status |
|---|---|---|---|
| **M1** | DP `log_memory_mb` + `cells_allocated` circular | §4.6 excludes `cells_allocated`, `nonzero_value_states`, `zero_value_states` from M2. Model redesignated exploratory. `fill_rate` added as alternative | ✓ |
| **M2** | `solution_value` inconsistency (response vs. not) | §2.1 explicitly states `solution_value` is NOT a response. §6.1/6.3 rewrites Block 4: bound columns excluded from all B&B models due to correlation with `solution_value` (an outcome proxy), not because it is a response. The `bound_variance`/`gap` metrics are retained | ✓ |
| **M3** | OLS for bounded `optimality_gap` | Replaced with **fractional logit** (Papke & Wooldridge, 1996). §7.4 provides detailed comparison table. §11.2 adds dedicated diagnostics. The sqrt transform is removed entirely | ✓ |
| **M4** | B&B logistic EPV ≈ 3 | Replaced with **elastic-net regularized logistic regression** (α = 0.5, nested CV λ tuning). §7.5 provides rationale and comparison. Model redesignated exploratory | ✓ |

**Evidence for M1 resolution:**
- §4.6: Entry for DP `log_memory_mb` excludes `cells_allocated`, `nonzero_value_states`, `zero_value_states` ✓
- §7.2 table: M2 additional predictors = "DP metrics minus cells_allocated, nonzero_value_states, zero_value_states (~11 metrics)" ✓
- §2.2: "Important: This model is designated exploratory because the DP execution metrics cells_allocated, nonzero_value_states, and zero_value_states must be excluded" ✓
- §16.2 (#7): Acknowledged as limitation (conservative test) ✓

**Evidence for M2 resolution:**
- §2.1 note: "solution_value is NOT used as a response variable in this design" ✓
- §6.1 Block 4: "solution_value is NOT a response variable in this design (see §2.1). However, bound metrics are near-perfectly correlated with solution_value... To prevent near-singularity, all three bound columns (mean_bound, max_bound, min_bound) are excluded from all B&B models" ✓
- §6.3 Block 4: "solution_value is not a response but bound columns are near-perfectly correlated with it" ✓
- §7.2 table: Every B&B model row explicitly lists the bound column exclusions ✓

**Evidence for M3 resolution:**
- §2.1: `optimality_gap` (fractional, [0,1]) — no transform listed ✓
- §2.3: `optimality_gap`: "none (fractional logit), logit(μ) = Xβ" ✓
- §7.2 table: Greedy `optimality_gap`: "Fractional logit (binomial, logit)" ✓
- §7.4: Full comparison table vs. beta regression and OLS ✓
- §11.2: Four dedicated diagnostics (link test, boundary sensitivity, robust SE comparison, missing predictors) ✓

**Evidence for M4 resolution:**
- §2.2: "elastic-net regularized logistic regression is used to prevent overfitting" ✓
- §7.2 table: B&B `optimal`: "Elastic-net logistic (binomial, logit)" ✓
- §7.3: "Penalized maximum likelihood; α = 0.5 (equal L1/L2 mixing); λ tuned by CV within each LOFO training fold" ✓
- §7.5: EPV discussion (197 events, ~67 predictors, EPV ≈ 3) ✓
- §8.4: Nested CV λ selection with 1-SE rule ✓
- §9.4: Three elastic-net specific outputs (nonzero count, λ path, coefficient trace) ✓
- §11.3: Four diagnostics (linearity, separation, calibration, λ stability) ✓

### 1.2 Minor Issues (m1–m6) — ALL RESOLVED

| ID | Resolution Location | Status |
|---|---|---|
| **m1** (B&B `log_nodes_explored` circular) | §4.6 excludes `nodes_generated`, `internal_nodes`. Model supplementary | ✓ |
| **m2** (LOFO variance) | §8.1: CI formula (4 df, t₄ = 2.78, half-width ~0.12). §15.3: fold-level values | ✓ |
| **m3** (zero-event AUC) | §8.3: Brier primary metric. AUC only for ≥1 event per family | ✓ |
| **m4** (Fisher z) | §5.2: "arctanh" with explanation. Clip to ±0.9999 | ✓ |
| **m5** (cluster-robust SEs) | §11.1: Default by `instance_id`. Durbin-Watson noted as "not meaningful without natural ordering" | ✓ |
| **m6** (back-transformed RMSE) | §9.1: Added φ = (1/n)Σexp(eᵢ). §11.4: family-specific smearing | ✓ |

### 1.3 Documentation Gaps (d1–d10) — ALL RESOLVED

| ID | Resolution Location | Status |
|---|---|---|
| **d1** (multiplicity) | §9.3: BH adjustment for 4 confirmatory models | ✓ |
| **d2** (log(n) default) | §5.3: Both n and log(n) as default | ✓ |
| **d3** (normality caveat) | §11.1: Visual diagnostics prioritized | ✓ |
| **d4** (LMG infeasibility) | §10.3: Δ-R² restricted to top-10 by permutation importance | ✓ |
| **d5** (per-algorithm correlations) | §3.3: New subsection | ✓ |
| **d6** (DP composition) | §3.4: New subsection | ✓ |
| **d7** (cross-algorithm comparison) | §10.5: Explicit note | ✓ |
| **d8** (requirements.txt) | §13.1: Mentioned | ✓ |
| **d9** (bootstrap method) | §7.6: "pairs bootstrap" | ✓ |
| **d10** (within-instance correlation) | §12.1, §11.1, §16.2 (#11) | ✓ |

**Verdict on original findings:** All 20 items verified as resolved.

---

## 2. New Issues Introduced by the Revision

### 2.1 CRITICAL ISSUE (NEW): DP `fill_rate` response — predictor circularity

**Location:** §2.1, §2.2, §3.2, §7.2 table (DP `fill_rate` row)
**Type:** Newly introduced in revision (response added to address M1)
**Severity:** Critical — blocks implementation

**Issue:**
The DP `fill_rate` supplementary response column is defined as `nonzero_value_states / cells_allocated` (§2.2). In the per-model specification table (§7.2), M2 additional predictors for `fill_rate` are listed as "14 DP metrics" with "None beyond global" as model-specific exclusions.

The 14 DP metrics (§3.2) include `cells_allocated`, `nonzero_value_states`, and `fill_rate` itself (under "Table structure"). This creates two distinct circularity problems:

1. **`fill_rate` predicting itself:** If `fill_rate` (column 99 in the dataset) is included in the M2 predictor set when `fill_rate` is also the response, the model trivially achieves R² ≈ 1.0 regardless of any other predictors.

2. **Components predicting the ratio:** Even if `fill_rate` is excluded from predictors, `cells_allocated` and `nonzero_value_states` are near-perfect predictors of `fill_rate = nonzero / cells_allocated`. A fractional logit model with `log(nonzero)` and `log(cells)` as predictors can approximate `logit(fill_rate) = log(nonzero/(cells−nonzero))` through the log link, producing R² ≈ 1.0. This is directly analogous to the original M1 issue (DP memory + `cells_allocated`).

**Impact:** The ΔR² for M2 over M1 in the `fill_rate` model would be trivially large and uninterpretable as a test of RQ3. The supplementary model does not provide useful evidence for or against the research question.

**Fix (mandatory before implementation):**
Exclude `fill_rate`, `cells_allocated`, and `nonzero_value_states` from M2 predictors when the response is `fill_rate`. Add these exclusions to §4.6 and update the per-model specification in §7.2. This parallels the existing exclusion for the `log_memory_mb` model.

**Evidence:**
- §2.2: "fill_rate = nonzero_value_states / cells_allocated" — establishes the deterministic relationship
- §3.2 DP metrics table: Lists `cells_allocated`, `nonzero_value_states`, `fill_rate` under "Table structure — 3"
- §7.2 table DP `fill_rate` row: "M2 Additional Predictors: 14 DP metrics" and "Excluded from M2: None beyond global"
- §4.6: No mention of `fill_rate` exclusions (only covers DP `log_memory_mb`, B&B `log_nodes_explored`, and all B&B bound metrics)

**Contrast with the memory model:** The design correctly excludes `cells_allocated`, `nonzero_value_states`, and `zero_value_states` from the `log_memory_mb` model (§4.6). The same structural logic applies to `fill_rate`.

---

### 2.2 Minor Issues (New or Residual)

#### 2.2.1 B&B binary M1 — unregularized logistic with EPV ≈ 5.1

**Location:** §7.2 table (B&B `optimal` row), §7.5
**Type:** Residual concern from original M4 fix
**Severity:** Minor

**Issue:** The M1 baseline for the B&B `optimal` model uses standard (unregularized) logistic regression with ~39 predictors and 197 events, yielding EPV ≈ 5.1 — below the Peduzzi et al. (1996) threshold of 10. The design explicitly applies elastic-net regularization only to M2 (§7.5) and states M1 has "no regularization for M1" (§7.2 table). While the model is exploratory and Δ(AUC) is computed via LOFO CV (which provides some robustness), the M1 baseline itself may produce unreliable in-sample coefficient estimates and potentially overfitted LOFO AUC estimates due to insufficient penalization of the ~39-predictor instance-characteristic model.

**Impact:** The M1 baseline's LOFO AUC might be optimistically biased, which would reduce the apparent Δ(AUC) between M1 and M2, making the test more conservative (understating the value of execution metrics). This is less severe than the M2 problem but is a methodological gap.

**Recommendation (optional):** Apply elastic-net regularization to M1 as well. Use the same α = 0.5 but tune λ separately for M1 and M2. This would provide a fair comparison between two regularized models. Alternatively, add a note to §7.5 acknowledging that M1 also has a low EPV and its LOFO AUC should be interpreted cautiously.

#### 2.2.2 M1 parameter count inconsistency

**Location:** §7.2 note: "M1 has ~39 parameters (including intercept)"
**Type:** Numerical inconsistency
**Severity:** Minor

**Issue:** M1 predictors = 35 instance characteristics (§3.1) + `n` + `log(n)` + `capacity_mode` + 4 family dummies (§5.3) = 35 + 1 + 1 + 1 + 4 = 42 predictors. Adding the intercept gives 43 parameters. The design states "~39 parameters," which undercounts by approximately 3–4.

This discrepancy is small and does not affect the analysis, but for a publication-ready design, the count should be precise or the approximation should be explained (e.g., if some of the 35 instance characteristics are expected to be excluded during VIF pre-filtering).

**Recommendation (optional):** Correct to "~42 parameters (including intercept)" or add a note: "Group A contains 35 features; after adding n, log(n), capacity_mode, and 4 family dummies, M1 has approximately 42 predictors including the intercept. Actual count may be lower after VIF pre-filtering."

#### 2.2.3 B&B metric count inconsistency: "~31" vs. actual

**Location:** §3.2 ("~31 usable after global exclusions"), §7.2 table ("~28 B&B metrics")
**Type:** Numerical inconsistency
**Severity:** Minor

**Issue:** The design states "B&B execution metrics (36 defined, ~31 usable after global exclusions)." The global exclusions listed (§3.2) are: `leaf_nodes`, `min_depth`, `skipped_by_cap`, `first_improvement_node`, `explored_generated_ratio`, `depth_histogram`, `queue_histogram`, `improvement_depths`, `improvement_nodes`, `mean_bound` — 10 exclusions from 36 → 26 remaining. The sub-domain counts in the table sum to 2 + 3 + 2 + 3 + 2 + 7 + 4 + 1 = 24 (not 31 or 26).

The per-model table uses "~28 B&B metrics (31 minus 3 bound metrics)" for the `log_time_millis` model, which is also internally inconsistent (31 − 3 = 28, but the correct base should be 26 − 3 = 23 or 24 − 3 = 21).

**Impact:** Low — all counts are labeled "~" (approximate). However, an implementer reading "~31" may design feature matrices with 31 B&B columns, only to find that 5–7 of them are not actually available. This could cause runtime errors.

**Recommendation (well-supported recommendation):** Recompute the B&B metric count from the exclusions. Based on the sub-domain table (which appears to be the most careful accounting): 24 usable metrics after global exclusions. Update "~31" → "~24" in §3.2 and the "~28" → "~21" in §7.2. Alternatively, add a note explaining the discrepancy.

#### 2.2.4 Fractional logit: quasi-likelihood ratio test underspecified

**Location:** §7.6
**Type:** Methodological ambiguity
**Severity:** Minor

**Issue:** §7.6 states "Fractional logit models: Compute quasi-likelihood ratio test (or Δ in Czuprow's pseudo-R²)." For Papke-Wooldridge fractional logit, the quasi-likelihood is not a true likelihood, so the standard likelihood-ratio test (which depends on the likelihood being correctly specified) is not valid. The QLR test adjusts by using a robust covariance matrix, but the design does not specify:
- Whether the QLR statistic is adjusted by a dispersion parameter estimate
- Whether the reference distribution is χ²(p₂ − p₁) or requires a scaling factor
- Which software implementation will be used (statsmodels GLM results for fractional logit may produce a quasi-likelihood that differs from the binomial log-likelihood used for standard logistic regression)

**Impact:** An implementer may compute a naive likelihood-ratio test that produces incorrect p-values for the fractional logit models.

**Recommendation (optional):** Replace "quasi-likelihood ratio test" with a more specific approach: "Compare M1 and M2 using the difference in deviance (from the binomial QL), with p-values from a χ²(p₂−p₁) distribution. If the dispersion parameter φ = deviance/(n−p₂) deviates substantially from 1, scale the test statistic by 1/φ (a quasi-likelihood ratio test). As a robust alternative, report Δ(Efron's R²) with bootstrap CIs."

#### 2.2.5 Cohen's f² with pseudo-R² — no interpretive caveat

**Location:** §7.6
**Type:** Documentation gap
**Severity:** Documentation

**Issue:** Cohen's f² = (R²₂ − R²₁) / (1 − R²₂) is specified with Cohen's benchmarks (0.02/0.15/0.35) for all models. For fractional logit, the R² used would be McFadden's pseudo-R² (as specified in §9.1). Pseudo-R² values are typically much lower than OLS R² for the same data, so a "small" Cohen's f² by OLS standards may in fact represent a substantial improvement for a fractional logit model. The design does not note this.

**Recommendation (optional):** Add a note: "For fractional logit models, f² is computed using McFadden's pseudo-R². Cohen's benchmarks (0.02/0.15/0.35) were developed for OLS R² and may not have the same interpretation for pseudo-R². These benchmarks are reported as approximate guides."

#### 2.2.6 Two-part hurdle model under-documented

**Location:** §2.2 (solution_gap), §7.2 (per-model table), §7.3 (model families), §11 (no diagnostic subsection)
**Type:** Documentation gap
**Severity:** Minor

**Issue:** The two-part hurdle model for B&B `solution_gap` is more complex than the other models (it combines logistic regression and fractional logit in sequence) but receives the least documentation:
- No dedicated diagnostics subsection (unlike OLS in §11.1, fractional logit in §11.2, elastic-net in §11.3)
- No justification for the hurdle vs. one-stage approach
- No discussion of how the 197 positive-gap observations affect the second-stage model's power (EPV is even lower than the binary model for the second stage)
- The per-model table says "Same as above" for part 1 (logistic) but doesn't specify whether M1 for part 1 uses regularized or standard logistic
- The second-stage fractional logit on gap>0 uses only 197 observations with ~26 predictors (EPV ≈ 7.6)

**Recommendation (optional):** Either (a) add a dedicated §11.x subsection with diagnostics, or (b) explicitly note that the hurdle model is a descriptive supplement without formal inference and add a caveat about the limited second-stage sample size.

#### 2.2.7 Fractional logit implementation detail — statsmodels `family=Binomial()` for proportions

**Location:** §13.1
**Type:** Implementation ambiguity
**Severity:** Minor

**Issue:** §13.1 specifies "statsmodels GLM with family=Binomial() and link=Logit() for fractional logit." In statsmodels, fractional logit with a continuous proportion response requires explicit handling: the endogenous variable must be passed as a 2-column array `[successes, failures]` or the `var_weights` argument must be used to specify the number of trials. If the response is simply a proportion in (0,1) without `var_weights`, statsmodels will treat it as a single Bernoulli trial, producing incorrect standard errors and deviance.

**Recommendation (optional):** Add implementation guidance: "For statsmodels fractional logit, pass the response as a proportion with `var_weights` set to the number of trials (n per cell) or use the 2-column `[successes, failures]` format with artificial counts. Use `cov_type='HC3'` for robust standard errors."

---

## 3. Cross-Check: Internal Consistency

### 3.1 Section reference cross-check

All section references in the revised document were verified:

| Reference | Target | Status |
|---|---|---|
| §2.1 → §6.1 (Block 4, solution_value) | §6.1 correctly states solution_value is not a response | ✓ |
| §2.2 → §7.2 (fractional logit) | §7.2 table confirms | ✓ |
| §2.2 → §4.6 (DP memory exclusion) | §4.6 entry matches | ✓ |
| §2.2 → §7.4 (fractional logit rationale) | §7.4 exists and is complete | ✓ |
| §2.2 → §7.5 (elastic-net rationale) | §7.5 exists and is complete | ✓ |
| §3.2 → §4.6 (model-specific exclusions) | §4.6 entries for log_memory_mb and log_nodes_explored | ✓ |
| §3.2 → §6.3 (mean_bound exclusion) | §6.3 confirms | ✓ |
| §4.6 → §7.2 (per-model table) | All exclusions reflected in table | ✓ (except fill_rate — see §2.1) |
| §7.6 → §9.1 (back-transformed RMSE) | §9.1 has Duan's smearing φ | ✓ |
| §8.3 → §9.2 (Brier for zero-event) | §9.2 confirms | ✓ |
| §9.3 → §15.1 (BH adjustment in table) | §15.1 mentions BH adj. p | ✓ |
| §11.1 → §12.1 (cluster-robust default) | §12.1 references cluster-robust SEs | ✓ |
| §13.3 → §7.2 (model count) | 9 responses in both | ✓ |

### 3.2 Response-to-predictor circularity audit

| Response | Predictors that could be circular | Excluded? | Status |
|---|---|---|---|
| DP `log_memory_mb` | `cells_allocated`, `nonzero_value_states`, `zero_value_states` | Yes (§4.6) | ✓ |
| DP `fill_rate` | `cells_allocated`, `nonzero_value_states`, `fill_rate` (self) | **No** | **✗ (NEW CRITICAL)** |
| B&B `log_nodes_explored` | `nodes_generated`, `internal_nodes` | Yes (§4.6) | ✓ |
| B&B `optimal` | `solution_value` (not in predictor groups) | N/A | ✓ |
| B&B `solution_gap` | Bound metrics (excluded), `solution_value` (not in predictors) | Yes (§4.6) | ✓ |
| Greedy `optimality_gap` | `solution_value` (not in predictor groups) | N/A (computed externally) | ✓ |
| Greedy `log_time_millis` | None identified | N/A | ✓ |
| DP `log_time_millis` | `total_evaluations` (causal but not definitional; valid RQ3 test) | No (intentional) | ✓ |
| B&B `log_time_millis` | `nodes_generated` (causal but not definitional) | No (intentional) | ✓ |

### 3.3 Confirmatory/exploratory/supplementary separation

The designations in §1 and §7.2 are consistent:

| Response | §1 Status | §7.2 Status | Match? |
|---|---|---|---|
| Greedy `log_time_millis` | Confirmatory | Confirmatory | ✓ |
| Greedy `optimality_gap` | Confirmatory | Confirmatory | ✓ |
| DP `log_time_millis` | Confirmatory | Confirmatory | ✓ |
| DP `log_memory_mb` | Exploratory | Exploratory | ✓ |
| DP `fill_rate` | Supplementary | Supplementary | ✓ |
| B&B `log_time_millis` | Confirmatory | Confirmatory | ✓ |
| B&B `optimal` | Exploratory | Exploratory | ✓ |
| B&B `log_nodes_explored` | Supplementary | Supplementary | ✓ |
| B&B `solution_gap` | (not in §1 table) | Supplementary | **Note:** §1 table has only 8 rows; `solution_gap` was added to §2.1 but not to §1's designation table |

### 3.4 Designation table mismatch

**Location:** §1 (confirmatory/exploratory table) vs. §2.1 (response table)
**Severity:** Minor

The §1 designations table lists 8 rows (does not include `solution_gap`), while §2.1 lists 9 responses (including `solution_gap`). The changelog indicates `solution_gap` was added to §2.1, but the §1 table was not updated to include its designation (supplementary).

**Recommendation (optional):** Add a row to §1's table: "B&B | solution_gap (hurdle) | Supplementary | Limited to 197 positive-gap observations; complex two-part model."

---

## 4. Findings Summary

### Critical (blocks implementation)

| # | Section | Issue | Impact |
|---|---------|-------|--------|
| **C1 (NEW)** | §2.2, §3.2, §4.6, §7.2 | DP `fill_rate` response: `cells_allocated`, `nonzero_value_states`, and `fill_rate` itself are not excluded from M2 predictors. `fill_rate = nonzero/cells` makes the relationship near-deterministic, directly analogous to the resolved M1 | ΔR² for `fill_rate` M2 is uninterpretable. Model cannot address RQ3 |

### Minor

| # | Section | Issue | Severity |
|---|---------|-------|----------|
| m2.1 | §7.2, §7.5 | B&B binary M1 (unregularized logistic, EPV ≈ 5.1) not discussed as potential reliability concern | Minor |
| m2.2 | §7.2 note | M1 parameter count "~39" should be ~42 (or clarified) | Minor |
| m2.3 | §3.2, §7.2 | B&B metric count "~31" inconsistent with sub-domain sum (≈24); "~28" in per-model table also inconsistent | Minor |
| m2.4 | §7.6 | Fractional logit QLR test underspecified (dispersion adjustment not described) | Minor |
| m2.5 | §7.6 | Cohen's f² benchmarks used with pseudo-R² without interpretive caveat | Documentation |
| m2.6 | §11 | Two-part hurdle model for `solution_gap` lacks dedicated diagnostics subsection | Documentation |
| m2.7 | §13.1 | `statsmodels family=Binomial()` for fractional logit: proportion vs. count specification not described | Implementation |
| m2.8 | §1 table | `solution_gap` missing from confirmatory/exploratory/supplementary designation table | Documentation |

### Resolved (original findings)

| Category | Total | Resolved | Not Resolved |
|---|---|---|---|
| Major (M1–M4) | 4 | 4 | 0 |
| Minor (m1–m6) | 6 | 6 | 0 |
| Documentation (d1–d10) | 10 | 10 | 0 |

---

## 5. Recommendations (Prioritized)

### Before implementation (blocking)

1. **Fix DP `fill_rate` circularity (C1):** Add `fill_rate`, `cells_allocated`, and `nonzero_value_states` to §4.6 as exclusions from M2 when the response is `fill_rate`. Update the per-model table in §7.2 accordingly. This mirrors the existing exclusion for `log_memory_mb` and is methodologically required for the same reason.

### Before implementation (strongly recommended)

2. **Fix B&B metric count (§3.2, §7.2):** Reconcile the 36 → ~24 (or ~26) usable count. Update "~31" and "~28" references. Verify by listing each of the 36 BB metrics with an explicit keep/exclude flag.

3. **Fix M1 parameter count (§7.2):** Correct "~39" to "~42" or add a clarifying note about VIF-driven pre-exclusions.

### Before implementation (documentation)

4. **Add `solution_gap` to §1 designation table.**
5. **Add Cohen's f² caveat for pseudo-R² (§7.6).**
6. **Add fractional logit QLR test specification (§7.6).**
7. **Add implementation note for statsmodels fractional logit (§13.1).**

### Optional (improves publication readiness)

8. **Apply elastic-net to B&B binary M1 as well**, or add an explicit caveat about M1's EPV ≈ 5.1.
9. **Add §11.4 for hurdle model diagnostics.**
10. **Add note about second-stage sample size (n=197) for `solution_gap` hurdle model.**

---

## 6. Final Verdict

**REVISE BEFORE IMPLEMENTATION**

**Basis:** One critical new issue (C1 — DP `fill_rate` circularity) blocks implementation. This issue was introduced by the revision itself — the `fill_rate` supplementary response was added to address the original M1 finding, but its predictor set was not updated to exclude the circular components (`cells_allocated`, `nonzero_value_states`, `fill_rate` itself). The problem is directly analogous to the original M1 and has the same consequence: an uninterpretable ΔR².

**However, the design is close to final.** The resolution is straightforward (add three exclusions to §4.6 and update one row in §7.2). Unlike the first audit, no redesign of model families or response definitions is needed. The core architecture (fractional logit for bounded responses, elastic-net for low-EPV binary, OLS with cluster-robust SEs for continuous, nested CV, BH-adjusted multiplicity control) is stable and well-documented.

Once C1 and the 8 minor issues (m2.1–m2.8) are addressed, the design should be ready to **PASS WITHOUT FURTHER AUDIT** for the following verified properties:

- All original 20 audit findings resolved ✓
- All model-specific circularity exclusions documented (pending C1 fix) ✓
- Per-model specification tables unambiguous ✓
- Model families appropriate to response supports ✓
- Multiplicity controlled for confirmatory tests ✓
- Cluster-robust SEs as default ✓
- LOFO CV with fold-level reporting ✓
- Elastic-net nested CV with 1-SE rule ✓
- Diagnostics specified for each model family ✓
- Software stack and pipeline specified ✓
