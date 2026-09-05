# Phase 3.2 — Predictive Statistical Modeling: Independent Design Audit

**Audit of:** `governance/PHASE_3_2_DESIGN.md`
**Design Date:** 2026-07-21
**Audit Date:** 2026-07-21
**Auditor:** Independent methodological review (fresh perspective, no prior involvement)
**Primary Objective:** Verify design soundness for RQ3 before any implementation

---

## Executive Summary

**Verdict: REVISE BEFORE IMPLEMENTATION**

The Phase 3.2 design document is structurally well-organized, correctly identifies the nested model comparison framework (M1 vs M2), proposes appropriate cross-validation (LOFO by family), and includes thorough diagnostic planning. The core analytical strategy — ΔR² via incremental F-test — is appropriate for RQ3. Variable exclusions correctly incorporate Phase 3.1 and Audit findings.

**However, four major issues and six minor issues require resolution before implementation.** The most critical concerns are: (1) a near-circular predictor–response relationship in the DP memory model, (2) use of OLS for a bounded [0,1] response, (3) insurmountable data sparsity for B&B logistic regression under the proposed predictor count, and (4) an unresolved inconsistency in the role of `solution_value`. These are not implementation-level details — they affect the validity of the statistical conclusions and must be addressed in the design before any code is written.

---

## 1. Research Question Alignment

### 1.1 Does the design answer RQ3?

RQ3 asks two questions:
> (a) *To what extent do algorithm-specific internal execution metrics provide additional explanatory power beyond instance characteristics for modeling runtime and solution quality?*
> (b) *Which execution metrics are most influential for each algorithm across diverse knapsack instance families?*

**Part (a):** Yes, the M1-vs-M2 nested comparison directly tests this. ΔR², Cohen's f², and incremental F-test are appropriate. The LOFO CV across families adds external validity. **Adequate.**

**Part (b):** Yes, standardized β weights, permutation importance, and Δ-R² partitioning are standard and complementary approaches. **Adequate.**

### 1.2 Are all proposed models necessary?

The design defines 7 algorithm–response pairs (5 continuous + 1 binary + 1 secondary continuous). All map to RQ3:

| Response | Necessity | Assessment |
|---|---|---|
| Greedy `log_time` | Core RQ3 runtime question | ✓ |
| Greedy `optimality_gap` | Core RQ3 quality question (heuristic) | ✓ |
| DP `log_time` | Core RQ3 runtime question | ✓ |
| DP `log_memory` | RQ3 "quality" for exact algorithm | Needs justification (§2.2) |
| B&B `log_time` | Core RQ3 runtime question | ✓ |
| B&B `optimal` (binary) | RQ3 quality (completeness) | Needs justification (§2.2) |
| B&B `log_nodes` (secondary) | RQ3 efficiency dimension | ✓ |

**Missing model:** B&B `solution_quality_gap` as a continuous quality measure. For the 197 incomplete B&B runs, `optimal_value` is available in the dataset (populated for B&B rows) and a continuous relative gap `(optimal_value − solution_value) / optimal_value` could be computed, analogous to the Greedy gap measure. This would give a continuous quality response for all 6,000 B&B rows (0 for complete, >0 for incomplete), complementing the binary `optimal` model. Currently, the design treats the 197 incomplete runs as a binary outcome, discarding information about *how close* B&B's best-found solution is to optimal. **Optional addition.**

### 1.3 Is there any leakage between predictors and responses?

**MAJOR ISSUE 1: Predictor–response circularity in DP `log_memory_mb` model**

In the M2 model for DP memory, the predictor set includes:
- `cells_allocated` (DP execution metric, under "Table structure" in §3.2)
- `nonzero_value_states`, `zero_value_states` (also DP metrics)

DP memory is proportional to `cells_allocated` (the DP table has `cells_allocated` entries, each of fixed size). Including `cells_allocated` as a predictor of `memory_mb` is **near-circular** — it uses the number of allocated DP cells to predict the memory consumed by those same cells. This is not "additional explanatory power"; it is near-identity.

The ΔR² for M2 over M1 in this model would be trivially large regardless of whether execution metrics add scientific insight. RQ3's question about "additional explanatory power" assumes a meaningful partition of variance, not a definitional relationship.

**Impact:** The DP memory model's M2-M1 comparison is uninterpretable as a test of RQ3. The design partially mitigates this via the Block 1 multicollinearity decision (drop `cells_allocated`, retain `average_fillable_items`), but the rationale there is multicollinearity across all models, not the circularity specific to this one model. If `cells_allocated` is dropped for multicollinearity reasons, the problem is solved for this model, but the design should explicitly state this and ensure the block decision is applied consistently for the DP memory model specifically.

**Verdict: MANDATORY REVISION.** Explicitly exclude `cells_allocated`, `nonzero_value_states`, and `zero_value_states` from the DP `log_memory_mb` M2 predictor set, or provide a justification for why this is not circular.

**MAJOR ISSUE 2: Near-circularity in B&B `log_nodes_explored` model**

The secondary response `log_nodes_explored` (B&B search efficiency) is modeled with `nodes_generated` and `internal_nodes` as predictors in M2. `nodes_explored` and `nodes_generated` are near-identical for complete runs — nodes must be generated before they can be explored, and the ratio `explored_generated_ratio` (already excluded as near-constant at 96.8% = 1.0) confirms this. Including `nodes_generated` to predict `nodes_explored` is definitional, not explanatory.

**Impact:** The secondary model is not useful for RQ3' explanatory-power question. However, since this is labeled "secondary" and is not the primary vehicle for RQ3, the severity is lower than Issue 1.

**Verdict: RECOMMENDED REVISION.** Exclude `nodes_generated` and `internal_nodes` from the B&B `log_nodes_explored` model's M2 predictor set, or demote the model to exploratory and caveat heavily.

### 1.4 Role of `solution_value` — unresolved inconsistency

§2.1 does not list `solution_value` as a response variable for any algorithm. However, §6.1 (Block 4) and §6.3 (Block 4) state:

> "All bound columns dropped; `solution_value` is the response for quality models"
> "Bound metrics are near-perfectly correlated with the response itself; including them would be circular"

This statement treats `solution_value` as a response variable, but it is never defined as one in §2. The bound-column dropping decision depends on which response model is being considered. If `solution_value` is NOT a response, then the bound columns (mean_bound, max_bound, min_bound) may still be legitimate predictors for `log_time_millis` or `log_nodes_explored` — their correlation with `solution_value` doesn't automatically disqualify them from predicting other responses. The near-perfect correlation within Block 4 is between bound columns and `solution_value`, not between bound columns and time/node-count responses.

**Impact:** Ambiguity in the exclusion logic. If bound columns are dropped preemptively across ALL models based on this reasoning, valid predictors may be discarded. If they are retained, the design needs to clarify.

**Verdict: MANDATORY REVISION.** Clarify whether `solution_value` is a response (and add it to §2.1 if so) or not. State the Block 4 exclusion rule per response model, not globally.

---

## 2. Statistical Validity

### 2.1 Response variables

**MAJOR ISSUE 3: OLS for bounded `optimality_gap_sqrt` response**

`optimality_gap_sqrt = √((DP_solution − Greedy_solution) / DP_solution)` yields a response bounded in [0, 1]. OLS linear regression makes no assumptions about the response distribution (it only assumes normally distributed residuals), so the bounded support is not automatically fatal. However:

1. **Predictions can fall outside [0, 1]**, especially at the boundary where Greedy finds the optimum (gap = 0). With ~600 observations at gap ≈ 0 (Greedy exact on Inverse Correlated), the model will predict negative gaps for some instances — an impossible value.
2. **Variance compression at boundaries**: The conditional variance of a bounded response typically decreases near the boundaries (ceiling/floor effects). Even with HC3 robust SEs, point estimates from OLS on bounded data are known to be biased in small samples with boundary mass.
3. **OLS assumes additive effects on the sqrt scale**, which may not be appropriate if the gap is zero for a structurally different reason (Greedy is provably optimal on Inverse Correlated vs. accidentally optimal on Uncorrelated).

**Better alternatives** (in increasing order of rigour):
- **Fractional logit** (GLM with logit link, binomial family, robust SEs): Handles [0,1] bounded response naturally.
- **Beta regression**: Parametric model for proportions; handles heteroscedasticity via a precision parameter.
- **Tobit regression** (if the boundary is viewed as censoring): If gap = 0 represents "Greedy solved this instance exactly," Tobit treats this as left-censoring.

**Impact:** Without addressing this, the Greedy quality model may produce invalid predictions and misleading importance rankings at the boundary, which is scientifically important (the Inverse Correlated family where Greedy is provably exact).

**Verdict: MANDATORY REVISION.** Replace OLS for `optimality_gap_sqrt` with beta regression or fractional logit. At minimum, add a sensitivity analysis comparing OLS (with robust SEs) to a bounded-support model.

### 2.2 Predictor transform: Fisher z for correlations

The design proposes "Fisher z-transform" for `pearson_corr`, `spearman_corr`, `kendall_corr`. This is technically an *arctanh* transformation (z = arctanh(r)). The "Fisher z-transform" conventionally refers to applying this to a *sample correlation coefficient* to stabilize its variance for inference, relying on the known sampling distribution. Here, each instance's correlation is a population parameter (the exact correlation of its weight–value pairs), not a sample estimate. The justification for the transformation is therefore different: it maps [-1, +1] → (-∞, +∞), which can improve linearity with the response.

**Minor concern:** If any instance has a correlation of exactly ±1, arctanh(±1) = ±∞, producing an infinite predictor. This is impossible in practice for continuous-valued Pisinger instances (sampling from continuous distributions makes exact ±1 correlation probability-zero), but the implementation should handle the edge case gracefully (e.g., clip to ±0.9999).

**Verdict: OPTIONAL.** The transform is not wrong, but its rationale should be "arctanh to unbounded support for linearity" rather than "Fisher z for variance stabilization." Add an edge-case guard.

### 2.3 Cross-validation strategy

**Minor issue: LOFO variance with 5 families**

Leave-one-family-out with only 5 folds produces a cross-validated performance estimate with 4 effective degrees of freedom. The standard error of the mean R² across folds is:

SE(R²_LOFO) = SD(R²_foldᵢ) / √5

With only 5 estimates, the SD is itself estimated with 4 df. The 95% CI for the mean LOFO R² spans approximately ±2.78 × SE (using t₄). If SD(R²_fold) ≈ 0.10 (plausible if one family is much harder to predict), the CI half-width is ~0.12 — wide enough to obscure meaningful ΔR² differences.

The design acknowledges this in §8.1 ("may understate predictive performance") but does not quantify the variance issue. The secondary random 5-fold CV (8.2) provides a lower-variance alternative but breaks the strict family-generalization evaluation.

**Verdict: DOCUMENTATION RECOMMENDATION.** Add a note that the LOFO estimate has high variance due to only 5 folds. Report fold-level R² values alongside the mean to allow readers to assess heterogeneity.

**Minor issue: B&B logistic LOFO for families with zero incomplete runs**

The design notes (§8.3) that some families (e.g., Uncorrelated) may have zero `optimal=false` instances. For LOFO folds where `optimal=false` is absent in the held-out set:
- AUC is undefined (no positive class to compute TPR/FPR)
- Precision/Recall are undefined for the minority class
- Accuracy becomes trivial (always predict "complete")

The design says "report per-family AUC separately" but doesn't specify what happens when AUC cannot be computed. For logistic regression, family-level predictions for a held-out family where the training set has zero events may also suffer from a different intercept (if the prevalence differs across families).

**Verdict: RECOMMENDED REVISION.** For the B&B logistic model, specify how to handle folds where the held-out family has zero `optimal=false` instances. Options: (a) use stratified LOFO that preserves the event proportion, (b) exclude those families from AUC computation and report only accuracy/Brier, or (c) note that this reduces the effective number of folds.

### 2.4 Feature importance

The three-tier approach (standardized β, permutation importance, Δ-R² partitioning) is comprehensive and appropriate. The design correctly notes the sensitivity of β weights to residual collinearity (§10.1) and the order-dependence of Δ-R² partitioning (§10.3).

**Minor issue:** The LMG metric (Lindeman, Merenda, Gold) is mentioned as an alternative but not committed to. LMG averages Shapley-value-like contributions over all orderings, which resolves the order-dependence. For ~66 predictors, computing LMG requires fitting 2^66 ≈ 10^20 models — computationally infeasible. If the design intends LMG, it should note this infeasibility and propose a practical alternative (e.g., only for the top-10 metrics identified by permutation importance).

**Verdict: DOCUMENTATION RECOMMENDATION.** Add a note that LMG is computationally infeasible for >20 predictors and specify a practical fallback (e.g., subset LMG on the top-k metrics from permutation importance).

---

## 3. Regression Assumptions

### 3.1 Overlooked violations

**MAJOR ISSUE 4: Events-per-variable ratio in B&B logistic model**

The B&B binary response `optimal` has 197 events (optimal = false) in 6,000 observations. In M2, the design proposes ~35 instance characteristics + ~31 B&B execution metrics = ~66 predictors. The events-per-variable (EPV) ratio is 197 / 66 ≈ 3.0.

Standard guidelines for logistic regression recommend a minimum EPV of 10 (Peduzzi et al., 1996) to 20 (Harrell, 2015). Below these thresholds, logistic regression produces:
- Biased coefficient estimates (inflated in absolute magnitude, away from zero)
- Unreliable standard errors (confidence intervals too wide)
- Overfitted predictions (near-perfect in-sample classification, poor out-of-sample)
- Increased risk of complete or quasi-complete separation

For M1 (instance characteristics only): ~39 predictors, EPV ≈ 5.1 — still below the recommended threshold. The design mentions Firth's penalized likelihood for separation (§11.2) but does not discuss the broader insufficient-event problem.

**Impact:** The B&B logistic model comparison (M1 vs M2) will produce unreliable ΔR² estimates and unreliable feature importance rankings. The secondary sensitivity analysis (§12.3) that excludes incomplete runs makes this moot by removing the response entirely, but that is a different analysis.

**Better approaches:**
1. **Penalized/regularized logistic regression** (ridge, lasso, or elastic net): Regularization shrinks coefficients toward zero, reducing overfitting. This is the standard approach for low-EPV settings.
2. **Reduce predictor dimensionality**: Use PCA on execution metrics before entering the logistic model, or select a subset of theoretically justified metrics.
3. **Exact logistic regression** (for very sparse data): Computationally expensive but unbiased.
4. **Acknowledge the limitation** and treat the binary model as exploratory if regularization is not adopted.

**Verdict: MANDATORY REVISION.** The design must either (a) adopt penalized/regularized logistic regression with cross-validated tuning, (b) substantially reduce the predictor count for the binary model, or (c) explicitly acknowledge the EPV problem and treat the binary analysis as exploratory with strong caveats. Do not proceed with standard maximum-likelihood logistic regression for 66 predictors with 197 events.

### 3.2 Independence assumption

**Minor issue: Clustered residuals by `n` and `instance_id`**

The design uses Durbin-Watson to test independence (§11.1). Durbin-Watson detects serial correlation in time-ordered residuals. The data are not time-ordered; they are grouped by (size, family, capacity_mode, seed). Durbin-Watson is not informative here.

Residuals are likely correlated within groups:
- By `n`: All 20-item instances share structural simplicity; residuals for these will be more similar to each other than to 1000-item residuals.
- By `(instance_id)`: The same instance in fixed and scaled mode shares item weights/values; residuals for these two rows may be correlated.

The design mentions "cluster-robust SEs by (family, n) if within-group correlation detected" but treats this as a contingency rather than a default. The clustered design (6 n-levels, 5 families, 2 capacity modes, 100 seeds per cell) guarantees some within-group correlation.

**Verdict: RECOMMENDED REVISION.** Make cluster-robust standard errors (by `instance_id` or by `(family, n)`) the default for all inference (coefficient CIs, F-tests), not a fallback diagnostic. Drop Durbin-Watson from the diagnostic list (or note it is only meaningful if data are ordered by execution sequence).

### 3.3 Normality tests with large n

The design proposes Shapiro-Wilk (n < 5000) and Anderson-Darling (n > 5000) for normality of residuals. With n ≈ 6000 per algorithm, both tests have enormous power: they will reject normality for *any* practically insignificant deviation (a Q-Q plot of residuals from a well-specified model will almost certainly be flagged as "significantly non-normal"). This is a well-known issue: at n > 1000, formal normality tests are more a measure of sample size than of assumption violation.

**Verdict: RECOMMENDED REVISION.** Prioritize visual diagnostics (Q-Q plots with confidence envelopes, residual histograms) over formal tests. If formal tests are included, add a note at the recommended n-threshold: "Given n ≈ 6000 per algorithm, these tests may reject even for practically negligible deviations. Assessment relies primarily on visual diagnostics."

### 3.4 Linearity of `n`

The design enters `n` as a linear term with "consider quadratic or log(n)" as a contingency. For all three algorithms, the relationship between n and runtime is known to be nonlinear:
- Greedy: O(n log n) → ~linear in practice
- DP: O(n·W) with W = 1000 (fixed) or W ≈ 250·n (scaled) → O(n) or O(n²)
- B&B: Depends exponentially/polynomially on n, varying by family

A purely linear term cannot capture these fundamentally different scaling relationships. The design should default to a flexible specification:

**Recommended:** Include both `n` and `log(n)` as predictors (or `n` and `n²`, or natural splines with 3-4 df). This is standard practice for benchmarks across orders of magnitude.

**Verdict: RECOMMENDED REVISION.** Add log(n) as a default predictor (not a contingency). The rationale: the experimental design spans n ∈ {20, 50, 100, 200, 500, 1000} — a 50× range across which performance is known to scale nonlinearly.

---

## 4. Multicollinearity Strategy

### 4.1 VIF threshold and pre-filtering

A VIF threshold of 10 is standard and appropriate. The two-stage approach (pre-filter correlation blocks → VIF check after fit) is sensible.

**Minor issue:** The correlation blocks in §6.1 were computed on the pooled dataset (all three algorithms). Per-algorithm correlations may differ materially. For example:
- Block 1 (`avg_fillable_items` ↔ `cells_allocated`) exists only for DP rows (since P cells_allocated is a DP metric, empty for Greedy/B&B). The pooled correlation includes DP rows (where both are present) and Greedy/B&B rows (where `cells_allocated` is absent). The correlation reported from Phase 3.1 was computed pairwise-complete, so it only used DP rows. This is fine.
- Block 2 includes `capacity_density` (DP metric) and `solution_density` (Greedy metric). These never co-occur in the same row. The pairwise correlation was computed on... nothing common. Wait — `capacity_density` is a DP metric (column 90) and `solution_density` is a Greedy metric (column 106). They appear in different rows. The Phase 3.1 correlation used pairwise-complete, meaning the correlation was computed from rows where BOTH columns are populated. Since no row has both DP and Greedy metrics, the pairwise correlation would have zero observations and should be NaN.

This suggests the correlation blocks reported in Phase 3.1 may have been computed differently than assumed. If using all-row, all-column correlation without algorithm separation, the Greedy-only and DP-only columns would have been excluded from pairwise-complete (since they'd never co-occur with other algorithm's columns), which would make Block 2's reported correlation of 0.994 suspicious.

Actually, this might indicate a problem with Phase 3.1's correlation computation if it was done on the full pooled dataset — but the audit confirmed the block correlations. Let me not re-audit Phase 3.1. The point is that the design should recompute per-algorithm correlations before pre-filtering.

**Verdict: OPTIONAL REVISION.** Specify that correlation blocks verified within each algorithm's subset before pre-filtering, not only from the pooled analysis.

### 4.2 Compositional relationships among DP metrics

DP evaluation metrics (`include_count`, `exclude_count`, `tie_count`, `total_evaluations`) may form an approximate composition: `include_count + exclude_count + tie_count ≈ total_evaluations`. If this relationship holds exactly or nearly, including all four creates a near-singular design matrix. The Phase 3.1 Report flagged `total_evaluations` as correlated with these, but the design does not address potential exact linear dependence.

**Verdict: OPTIONAL REVISION.** Verify the identity `include + exclude + tie = total_evaluations` (or `include_count + exclude_count + tie_count` = ... it depends on how `total_evaluations` is defined in the DP instrumentation code). If the relationship is exact, drop at least one of these predictors or add a note.

---

## 5. Algorithm-Specific Modeling

### 5.1 Separate models per algorithm

The design models each algorithm separately. This is correct for RQ3:

1. **RQ3 explicitly asks "for each algorithm."**
2. **Metric sets are disjoint** (B&B metrics are empty for DP/Greedy rows and vice versa). Pooling would require imputing missing metrics or creating a unified feature space that discards algorithm-specific information.
3. **Variance structure differs** across algorithms (Greedy: μs scale; B&B: ms to s scale).

**No change needed.**

### 5.2 Are pooled models ever justified?

Pooled models could address a different question: "Do the same instance features predict performance across algorithms?" This is not RQ3 but could be a supplementary analysis. The design correctly does not make this a primary analysis.

**Verdict: No action needed.**

### 5.3 Cross-algorithm comparison of metric importance

The design proposes separate importance rankings per algorithm (§10.4). Since the metric sets differ, these rankings are not directly comparable across algorithms. The design does not address this. A reviewer might ask: "How do you compare 'the most influential metric for B&B' with 'the most influential metric for Greedy' when they measure different phenomena?" This is inherent to the design and not a flaw, but it should be acknowledged.

**Verdict: DOCUMENTATION RECOMMENDATION.** Add a note: "Because metric sets are algorithm-specific, feature importance rankings are reported per-algorithm. Cross-algorithm comparisons of importance magnitude are not meaningful due to different response scales and predictor sets."

---

## 6. Threats to Validity

### 6.1 Already acknowledged (verified correct)

The design's §16 lists 7 limitations. All are correctly identified and appropriately scoped. No issues found.

### 6.2 Not acknowledged — requiring addition

**T1 — Multiple comparison inflation (§9.3, §15.1):**
The design reports 7 primary model comparisons (M1 vs M2 for each algorithm–response pair) plus family-level breakdowns, capacity-mode sensitivity analyses, and multiple importance metrics. None of the comparison thresholds use multiplicity correction (Bonferroni, Holm, Benjamini-Hochberg). With 7 independent tests at α = 0.05, the familywise error rate is 1 − (0.95)⁷ ≈ 0.30. Even if dependencies reduce this, the probability of at least one false-positive "significant ΔR²" is non-negligible.

**Recommended action:** Designate the Greedy and B&B `log_time_millis` models as primary confirmatory tests (2 comparisons). All others are exploratory/supporting. Report Benjamini-Hochberg adjusted p-values for the full set. This is standard practice in empirical software engineering and optimization venues.

**T2 — Back-transformed RMSE formula inconsistency (§9.1 vs §11.3):**
§9.1 defines back-transformed RMSE as:
`√(Σ(exp(yᵢ) − exp(ŷᵢ))² / n)`
§11.3 defines Duan's smearing estimator:
`ŷ_original = exp(ŷ_log) × (1/n) Σ exp(eᵢ)`

The formula in §9.1 does not apply the smearing factor. The naïve back-transform `exp(ŷᵢ_log)` predicts the conditional median, not the conditional mean. RMSE computed on median predictions systematically overestimates error when residuals are right-skewed on the original scale (which is exactly why log transforms are used). The corrected formula should use bias-adjusted predictions:
`ŷᵢ_original = exp(ŷᵢ_log) × φ`
where φ = (1/n) Σ exp(eᵢ).

**T3 — Greedy memory as a non-issue, but not discussed:**
The design notes (§4.5) that 3,517 rows have `memory_mb = 0` (all Greedy). Greedy memory is trivially small and is not used as a Greedy response. This is correct. However, the design does not note that `memory_mb` for Greedy rows is essentially noise (the JVM's measured memory at the time of measurement may dominate the algorithm's actual memory footprint). For completeness, this should be stated.

**T4 — Residual dependence in split-plot structure:**
The experiment design is a split-plot: each instance (whole plot) is run under both capacity modes (subplot). The two rows for the same instance share weight/value structure. Models that pool both capacity modes should account for this. The design includes `capacity_mode` as a dummy (addressing mean differences) but does not address correlation between the two rows (within-instance correlation). Cluster-robust SEs by `instance_id` would address this.

**T5 — Bootstrap ΔR² method underspecified:**
§7.3 proposes "bootstrap CI (percentile method, 1999 resamples, stratified by family)." The bootstrap sampling method is not specified:
- *Pairs bootstrap* (resample (y, X) rows with replacement): standard for regression, preserves the joint distribution.
- *Residual bootstrap* (fit M1, resample residuals, add back): assumption-dependent (requires correct model specification).
- *Wild bootstrap*: robust to heteroscedasticity.

The design should specify pairs bootstrap (most assumptions-free for nested model comparison). Also, resampling should be stratified by algorithm (implicitly done since models are per-algorithm) and by family (as specified). The number 1999 is uncommon — 999 or 1999 yield slightly different percentile intervals. Recommend standardizing to 1999 or documenting the choice.

### 6.3 Reproducibility threats

**T6 — Seed management:**
The design uses seed = 42 for all random processes. This is consistent with Phase 3.1 and ensures exact reproducibility. **Adequate.**

**T7 — Data leakage in Greedy optimality_gap computation:**
The design computes Greedy's optimality_gap by joining DP's `solution_value` on `(instance_id, capacity_mode)`. The DP solution is exact for all instances. **No leakage** — the join uses only identifiers that exist before any algorithm runs. **Correct.**

**T8 — Software versioning:**
The design specifies `statsmodels`, `scikit-learn`, `scipy`, `pandas`, `numpy`. All standard. But it does not pin versions or specify a virtual environment. For reproducibility, a `requirements.txt` or `environment.yml` should be produced with the implementation.

---

## 7. Reviewer Perspective

A reviewer at a strong empirical SE or optimization venue would likely raise the following challenges. I have assessed each for validity:

| # | Challenge | Assessment | Design Response |
|---|---|---|---|
| 1 | "DP `memory_mb` with `cells_allocated` as a predictor is circular — you are using the number of allocated cells to predict the memory consumed by those same cells." | **Valid.** The ΔR² would be inflated trivially. | **MANDATORY REVISION** per Major Issue 1. |
| 2 | "You use OLS for a bounded [0,1] response. Why not beta regression or fractional logit?" | **Valid.** Boundary predictions can be out of range. | **MANDATORY REVISION** per Major Issue 3. |
| 3 | "Your B&B logistic model has 197 events and ~66 predictors. The EPV is ~3. How reliable are your coefficients?" | **Valid.** Biased estimates, overfitting, unreliable CIs. | **MANDATORY REVISION** per Major Issue 4. |
| 4 | "What is `solution_value`? §2 doesn't use it as a response, but §6 treats it as one. Which is it?" | **Valid.** Internal inconsistency. | **MANDATORY REVISION** per Major Issue 2. |
| 5 | "You test 7 model pairs without multiplicity correction. How many of your 'significant' ΔR² values survive adjustment?" | **Valid.** FWER ≈ 0.30 uncorrected. | **RECOMMENDED.** Add BH adjustment. |
| 6 | "Your LOFO estimate uses only 5 folds. The CI around mean R² must be very wide. Can you quantify?" | **Valid.** 4 df for the SE estimate. | **RECOMMENDED.** Report fold-level values, add variance note. |
| 7 | "`n` is entered linearly, but algorithm runtime is known to be nonlinear in n across your range (20–1000). Why not log(n) or splines?" | **Valid.** O(n log n), O(nW), O(2ⁿ) scaling. | **RECOMMENDED.** Add log(n) as default. |
| 8 | "Your clusters by (n, family) induce correlated residuals. Durbin-Watson is not appropriate for this grouped structure." | **Valid.** Use cluster-robust SEs as default. | **RECOMMENDED.** Make default, not contingency. |
| 9 | "B&B's binary `optimal` is a coarse quality metric. Why not use the continuous relative gap for all B&B rows?" | **Partially valid.** Continuous gap gives resolution. | **[New] OPTIONAL.** Add as supplementary. |
| 10 | "Your back-transformed RMSE does not apply Duan's smearing factor. You are computing RMSE for median predictions, not mean predictions." | **Valid.** Inconsistency between §9.1 and §11.3. | **RECOMMENDED.** Fix formula. |

---

## 8. Issues Summary and Impact

### Major Issues (mandatory revision before implementation)

| # | Section | Issue | Impact | Severity |
|---|---------|-------|--------|----------|
| M1 | §2.1, §3.2, §6.3 | DP `log_memory_mb` response predicted by `cells_allocated` (near-identity) | ΔR² uninterpretable for this model | **CRITICAL** |
| M2 | §2.1, §6.1, §6.3 | Inconsistent handling of `solution_value` (treated as response in §6 but not listed in §2) | Unclear exclusion logic for bound columns; potential loss of valid predictors or retention of circular ones | **HIGH** |
| M3 | §2.2, §7.2 | OLS for bounded [0,1] `optimality_gap_sqrt` without addressing boundary support | Invalid predictions at gap ≈ 0; biased importance for key family (Inverse Correlated) | **HIGH** |
| M4 | §7.2, §11.2 | B&B logistic regression with EPV ≈ 3 (197 events, ~66 predictors) | Unreliable coefficients, overfitting, invalid CIs | **HIGH** |

### Minor Issues (recommended revision)

| # | Section | Issue | Impact | Severity |
|---|---------|-------|--------|----------|
| m1 | §7.2, §3.2 | B&B `log_nodes_explored` secondary model with `nodes_generated` as predictor (near-circular) | Secondary model adds little scientific value; demote or exclude | **MODERATE** |
| m2 | §8.1 | LOFO with 5 folds yields high-variance CV estimate | Readers may overinterpret fold-level R² precision | **LOW** |
| m3 | §8.3 | B&B logistic LOFO: families with zero `optimal=false` produce undefined AUC | AUC cannot be computed for some folds; need fallback plan | **LOW** |
| m4 | §5.2 | Fisher z/arctanh for correlation predictors without ±1 edge-case guard | Runtime error if any instance has r = ±1 | **LOW** |
| m5 | §11.1 | Durbin-Watson inappropriate for grouped data; cluster-robust SEs should be default | Incorrect independence assessment; inflated significance | **MODERATE** |
| m6 | §9.1, §11.3 | Back-transformed RMSE formula omits Duan's smearing factor | RMSE computed on median predictions, not mean; systematically overestimated error | **LOW** |

### Documentation Recommendations

| # | Section | Issue |
|---|---------|-------|
| d1 | §9.3 | Multiple comparison problem: 7+ simultaneous tests without adjustment |
| d2 | §5.2 | Default to log(n) + n (not pure linear), not as a contingency |
| d3 | §11.1 | Prioritize visual normality diagnostics over formal tests at n = 6000 |
| d4 | §10.3 | LMG infeasibility for >20 predictors; specify fallback |
| d5 | §6.1 | Recompute correlation blocks per-algorithm subset, not just pooled |
| d6 | §6.3 | Check compositional identity among DP evaluation metrics |
| d7 | §14 / §16 | Add note that per-algorithm importance rankings are not directly comparable across algorithms |
| d8 | §13.1 | Add `requirements.txt` for software version pinning |
| d9 | §7.3 | Specify pairs bootstrap method for ΔR² CI |
| d10 | §12.1 | Add within-instance correlation (same instance in both capacity modes) as validity note |

---

## 9. Recommendations (Prioritized)

### Before implementation (blocking)

1. **Fix DP memory model (§2.1, §3.2, §6.3):** Explicitly exclude `cells_allocated`, `nonzero_value_states`, `zero_value_states` from M2 predictors when the response is `log_memory_mb`. Document this as a structural exclusion (not a VIF decision).

2. **Resolve `solution_value` inconsistency (§2.1, §6.1, §6.3):** Either (a) add `solution_value` as a response for B&B solution quality and define it in §2.1, or (b) remove the statement that bound columns are dropped because they correlate with "the response" and re-evaluate Block 4's exclusion per response model.

3. **Replace OLS for `optimality_gap_sqrt` (§2.2, §7.2):** Adopt beta regression or fractional logit (GLM with binomial family, logit link, robust SEs). OLS can be retained as a sensitivity analysis but must not be the primary model.

4. **Address B&B logistic EPV problem (§7.2, §11.2):** Adopt ridge/lasso/elastic-net logistic regression with cross-validated tuning, or substantially reduce the predictor set (e.g., top-10 execution metrics by univariate association + PCA components), or explicitly move the binary model to exploratory status with strong caveats.

### Before implementation (strongly recommended)

5. **Default to log(n) + n (§5.2):** Replace "consider quadratic or log(n)" with a default inclusion of log(n) alongside linear n. Known nonlinear scaling across 20–1000 items justifies this.

6. **Cluster-robust SEs as default (§11.1):** Replace Durbin-Watson with cluster-robust standard errors by `instance_id` (for within-instance correlation) or by `(family, n)` (for within-cell correlation). Make this the default for all inference.

7. **Fix back-transformed RMSE (§9.1):** Apply Duan's smearing factor to back-transformed predictions before computing RMSE.

### Before implementation (documentation)

8. **Add multiplicity note (§9.3):** State which comparisons are confirmatory vs. exploratory. Report BH-adjusted p-values.

9. **Quantify LOFO variance (§8.1):** Add the formula for the LOFO SE and note the wide CI due to 5 folds.

10. **Specify bootstrap method (§7.3):** State "pairs bootstrap resampled within family strata."

---

## 10. Final Verdict

**REVISE BEFORE IMPLEMENTATION**

**Basis:** Four major issues (M1–M4) affect the validity of specific model comparisons in the primary RQ3 analysis. These are not implementation details — they affect whether the statistical conclusions from those models can be trusted:

- **M1** (DP memory circularity) would produce a trivially inflated ΔR² that does not address RQ3.
- **M2** (solution_value inconsistency) creates ambiguity about predictor exclusion that could propagate to incorrect model specifications.
- **M3** (OLS on bounded response) risks invalid out-of-range predictions and unreliable feature importance for the Greedy quality model.
- **M4** (low EPV for logistic regression) would produce unreliable coefficient estimates and overconfident inference for the B&B binary model.

All four are correctable without redesigning the study. The design's core framework (nested model comparison, LOFO CV, per-algorithm analysis, comprehensive diagnostics) is sound and should be preserved.

The minor issues (m1–m6) and documentation gaps (d1–d10) are non-blocking but should be resolved before implementation to ensure the analysis is publication-ready.

The design is close to a PASS WITH MINOR ISSUES once M1–M4 are resolved. As written, it requires revision.

---

## Appendix: Items Verified as Correct

The following design decisions were verified and require no change:

| Decision | Verdict |
|----------|---------|
| Separate per-algorithm models (§1) | ✓ Correct for RQ3 |
| M1 vs M2 nested comparison (§7.1) | ✓ Appropriate framework |
| LOFO CV by family (§8.1) | ✓ Strong for generalization assessment |
| ΔR² + Cohen's f² + F-test (§7.3) | ✓ Standard, appropriate effect size |
| Variable exclusions from Phase 3.1 + Audit (§4) | ✓ Complete and accurate |
| Log transforms for skewed responses (§2.3) | ✓ Supported by Phase 3.1 skewness |
| Log transforms for skewed predictors (§5.2) | ✓ Correct |
| Three-tier feature importance (§10.1–10.4) | ✓ Comprehensive, complementary |
| Diagnostic checklist (§11.1–11.2) | ✓ Thorough |
| Capacity mode sensitivity (§12.1) | ✓ Good practice |
| B&B incomplete-run sensitivity (§12.3) | ✓ Essential for censored data |
| Fixed seed = 42 (§8.4, §13.4) | ✓ Ensures exact reproducibility |
| Greedy optimality_gap computed externally from DP solution (§2.2) | ✓ Correct — avoids structural missingness |
| Categorical encoding (§5.3) | ✓ Standard one-hot + binary dummy |
| Exclusion of constant/near-constant/ redundant variables (§4) | ✓ Matches Phase 3.1 + Audit |
| String histogram columns excluded from primary analysis (§5.4) | ✓ Pragmatic; scalar summaries as supplement | 
