# Phase 4 Claim Inventory

## Performance Claims (P)

**Claim P01: Greedy log_time_millis base vs execution**
- **Category:** Performance
- **Evidence:** `output/results/ols_metrics_aggregated.csv`
- **Supporting numbers:** M1 full_sample R^2 = 0.857, M2 full_sample R^2 = 0.858. Delta R^2 is negligible (~0.001).
- **Status:** Directly supported, Inferential (deterministic behavior).

**Claim P02: DynamicProgramming log_time_millis base vs execution**
- **Category:** Performance
- **Evidence:** `output/results/ols_metrics_aggregated.csv`
- **Supporting numbers:** M1 full_sample R^2 = 0.977, M2 full_sample R^2 = 0.979. Delta R^2 is negligible.
- **Status:** Directly supported, Inferential (highly deterministic).

**Claim P03: BranchAndBound log_time_millis and log_nodes_explored base vs execution**
- **Category:** Performance
- **Evidence:** `output/results/ols_metrics_aggregated.csv`
- **Supporting numbers:** log_nodes_explored M1 R^2 = 0.736, M2 R^2 = 0.979. Delta R^2 ~ 0.243. log_time_millis M1 R^2 = 0.745, M2 R^2 = 0.961. Delta R^2 ~ 0.216.
- **Status:** Directly supported, Inferential (execution metrics provide substantial explanatory power).

**Claim P04: Greedy optimality_gap deterministic behavior**
- **Category:** Performance
- **Evidence:** `output/results/flogit_metrics_aggregated.csv`
- **Supporting numbers:** M1 full_sample pseudo-R^2 = 0.215, M2 pseudo-R^2 = 0.273.
- **Status:** Directly supported, Descriptive.

**Claim P05: BranchAndBound optimal classification**
- **Category:** Performance
- **Evidence:** `output/cross_validation/lofo_folds_elasticnet.csv`
- **Supporting numbers:** Accuracy varies by fold (Uncorrelated=1.0, StronglyCorrelated=0.94, etc.). Brier score ~ 0.24-0.25.
- **Status:** Directly supported, Descriptive.

## Diagnostic Claims (D)

**Claim D01: VIF Thinning Robustness (B&B)**
- **Category:** Diagnostics
- **Evidence:** `output/diagnostics/vif_thinned_delta_r2_comparison.csv`
- **Supporting numbers:** 20 predictors removed. Raw delta R^2 = 0.243, Thinned delta R^2 = 0.236.
- **Status:** Directly supported, Inferential (robust to multicollinearity).

**Claim D02: VIF Thinning Robustness (Greedy & DP)**
- **Category:** Diagnostics
- **Evidence:** `output/diagnostics/vif_thinned_delta_r2_comparison.csv`
- **Supporting numbers:** Thinned delta R^2 becomes slightly negative (e.g., -0.064 for Greedy), showing execution metrics are redundant.
- **Status:** Directly supported, Inferential.

**Claim D03: Fractional Logit Link Tests**
- **Category:** Diagnostics
- **Evidence:** `assumption_summary_DynamicProgramming_fill_rate.txt`, `assumption_summary_Greedy_optimality_gap.txt`
- **Supporting numbers:** link_test_sig: True in both cases.
- **Status:** Directly supported, Descriptive (non-linearities present).

**Claim D04: Elastic-net Lambda Stability**
- **Category:** Diagnostics
- **Evidence:** `assumption_summary_BranchAndBound_optimal.txt`
- **Supporting numbers:** lambda_sd = 0.0 (constant C=10000.0).
- **Status:** Directly supported, Descriptive.

## Feature Importance Claims (F)

**Claim F01: Top standard predictors (B&B)**
- **Category:** Feature Importance
- **Evidence:** `std_beta_BandB_log_nodes_explored_M2.csv`
- **Supporting numbers:** See Top 5 ranked betas in CSV.
- **Status:** Directly supported, Descriptive.

**Claim F02: Zero-event LOFO families (Elastic-Net)**
- **Category:** Unexpected Findings
- **Evidence:** `output/cross_validation/zero_event_families.txt`
- **Supporting numbers:** Uncorrelated, WeaklyCorrelated lack variance in response.
- **Status:** Directly supported, Descriptive.

## Unsupported Areas Identified
- Generalization claims to instances outside the 6000-instance knapsack dataset.
- Causal statements regarding algorithmic performance.
- Practical hardware recommendations (time_millis is machine-specific).
- Algorithmic explanations of *why* specific execution paths occur (the models are descriptive/associative).
