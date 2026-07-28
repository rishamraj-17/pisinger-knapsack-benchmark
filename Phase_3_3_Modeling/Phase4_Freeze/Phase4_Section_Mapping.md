# Phase 4 Section Mapping

## 1. Dataset & Methodology
- Claim F02: Zero-event LOFO families (Elastic-Net)
- Evidence: `canonical_dataset.csv`, `zero_event_families.txt`

## 2. Model Performance (Base vs Execution)
- Claim P01: Greedy log_time_millis base vs execution
- Claim P02: DynamicProgramming log_time_millis base vs execution
- Claim P03: BranchAndBound log_time_millis and log_nodes_explored base vs execution
- Claim P04: Greedy optimality_gap deterministic behavior
- Claim P05: BranchAndBound optimal classification

## 3. Diagnostics & Robustness
- Claim D01: VIF Thinning Robustness (B&B)
- Claim D02: VIF Thinning Robustness (Greedy & DP)
- Claim D03: Fractional Logit Link Tests
- Claim D04: Elastic-net Lambda Stability
- Evidence: `smearing_factors.csv`, `assumption_summary_*.txt`, `residual_hist_*.png`

## 4. Feature Importance
- Claim F01: Top standard predictors (B&B)
- Evidence: `std_beta_*.csv`, `*_permutation_importance.csv`, `importance_*.png`

## 5. Limitations
- Unsupported Area: Generalization beyond current dataset
- Unsupported Area: Causal interpretations
- Unsupported Area: Hardware-specific absolute times
