# Phase 4 Unsupported Claims

This document lists claims that currently lack direct evidence in the archive.

1. **Generalization Claims:** The archive only contains metrics evaluated on the specific 6,000 instance dataset generated in Phase 1. Any claim that these models predict behavior on *other* datasets is UNSUPPORTED.
2. **Hardware/Runtime Equivalency:** `log_time_millis` is highly specific to the CPU/RAM used during execution. Claims that these absolute times represent general bounds are UNSUPPORTED.
3. **Causal Assertions:** The models are OLS, Fractional Logit, and Elastic-Net (associative models). Any claim that feature X *causes* execution time Y is UNSUPPORTED.
4. **Algorithmic Optimality Claims:** Any claim that DP is "better" than Greedy overall is UNSUPPORTED; the metrics only show behavior distributions, not absolute superiority in all scenarios.
