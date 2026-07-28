# Phase 4.1 — Evidence Extraction Master Document

This document is generated directly from the archived Phase 3 outputs.

## Section 1 — Dataset

- Dataset info unavailable: [Errno 2] No such file or directory: '/home/risham-raj-byahut/IdeaProjects/Emperical_Comparision/Phase_3_3_Modeling/Phase3_Archive/output/results/canonical_dataset.csv'

## Section 2 — Model Performance

### OLS Models
| cv_scheme   | algorithm   | response           | model   |   r_squared_mean |   r_squared_sd |   r_squared_ci_lower |   r_squared_ci_upper |   adj_r_squared_mean |   adj_r_squared_sd |   adj_r_squared_ci_lower |   adj_r_squared_ci_upper |   rmse_mean |     rmse_sd |   rmse_ci_lower |   rmse_ci_upper |   mae_mean |       mae_sd |   mae_ci_lower |   mae_ci_upper |    n |   p |   r_squared |   adj_r_squared |       rmse |        mae |
|:------------|:------------|:-------------------|:--------|-----------------:|---------------:|---------------------:|---------------------:|---------------------:|-------------------:|-------------------------:|-------------------------:|------------:|------------:|----------------:|----------------:|-----------:|-------------:|---------------:|---------------:|-----:|----:|------------:|----------------:|-----------:|-----------:|
| LOFO        | Greedy      | log_time_millis    | M1      |      -4.65715    |    12.0508     |         -19.6201     |           10.3058    |          -4.7071     |        12.1572     |              -19.8022    |              10.388      |    2.01122  |   2.91805   |       -1.61201  |        5.63445  |   1.89511  |   2.96449    |      -1.78578  |       5.57601  | 6000 |  42 | nan         |    nan          | nan        | nan        |
| LOFO        | Greedy      | log_time_millis    | M2      |      -5.06894    |    13.0214     |         -21.2372     |           11.0993    |          -5.12897    |        13.1502     |              -21.4571    |              11.1992     |    2.04988  |   3.0505    |       -1.73782  |        5.83759  |   1.94087  |   3.09499    |      -1.90206  |       5.7838   | 6000 |  47 | nan         |    nan          | nan        | nan        |
| 5-fold      | Greedy      | log_time_millis    | M1      |       0.854965   |     0.0136258  |           0.838046   |            0.871883  |           0.853684   |         0.0137461  |                0.836616  |               0.870752   |    0.544937 |   0.0244922 |        0.514526 |        0.575348 |   0.410577 |   0.0135067  |       0.393807 |       0.427348 | 6000 |  42 | nan         |    nan          | nan        | nan        |
| 5-fold      | Greedy      | log_time_millis    | M2      |       0.856378   |     0.0136599  |           0.839417   |            0.873338  |           0.854957   |         0.013795   |                0.837828  |               0.872086   |    0.542261 |   0.0244246 |        0.511934 |        0.572588 |   0.409594 |   0.0139782  |       0.392238 |       0.42695  | 6000 |  47 | nan         |    nan          | nan        | nan        |
| full_sample | Greedy      | log_time_millis    | M1      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  42 |   0.857298  |      0.856292   |   0.541166 |   0.407539 |
| full_sample | Greedy      | log_time_millis    | M2      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  47 |   0.858811  |      0.857696   |   0.538291 |   0.40639  |
| LOFO        | DP          | log_time_millis    | M1      |       0.630483   |     0.50629    |           0.00184044 |            1.25912   |           0.62722    |         0.51076    |               -0.0069724 |               1.26141    |    1.13446  |   1.00523   |       -0.113697 |        2.38261  |   0.931531 |   0.960535   |      -0.261131 |       2.12419  | 6000 |  42 | nan         |    nan          | nan        | nan        |
| LOFO        | DP          | log_time_millis    | M2      |       0.810232   |     0.262424   |           0.484389   |            1.13607   |           0.808153   |         0.265299   |                0.478741  |               1.13757    |    0.881093 |   0.636936  |        0.090233 |        1.67195  |   0.651782 |   0.418446   |       0.132213 |       1.17135  | 6000 |  52 | nan         |    nan          | nan        | nan        |
| 5-fold      | DP          | log_time_millis    | M1      |       0.977436   |     0.00140973 |           0.975685   |            0.979186  |           0.977237   |         0.00142218 |                0.975471  |               0.979003   |    0.361532 |   0.0107432 |        0.348192 |        0.374871 |   0.273546 |   0.00502489 |       0.267307 |       0.279786 | 6000 |  42 | nan         |    nan          | nan        | nan        |
| 5-fold      | DP          | log_time_millis    | M2      |       0.978682   |     0.00140806 |           0.976934   |            0.98043   |           0.978449   |         0.00142348 |                0.976681  |               0.980216   |    0.351415 |   0.0120555 |        0.336446 |        0.366384 |   0.268062 |   0.00531784 |       0.261459 |       0.274665 | 6000 |  52 | nan         |    nan          | nan        | nan        |
| full_sample | DP          | log_time_millis    | M1      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  42 |   0.977837  |      0.977681   |   0.358514 |   0.271161 |
| full_sample | DP          | log_time_millis    | M2      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  52 |   0.979156  |      0.978973   |   0.347687 |   0.265281 |
| LOFO        | DP          | log_memory_mb      | M1      |    -107.603      |   240.36       |        -406.049      |          190.844     |        -108.562      |       242.482      |             -409.643     |             192.52       |    6.82971  |  11.7476    |       -7.75685  |       21.4163   |   5.92163  |  12.2399     |      -9.27628  |      21.1195   | 6000 |  42 | nan         |    nan          | nan        | nan        |
| LOFO        | DP          | log_memory_mb      | M2      |    -110.427      |   246.749      |        -416.806      |          195.952     |        -111.624      |       249.399      |             -421.294     |             198.046      |    6.88472  |  11.9209    |       -7.91705  |       21.6865   |   5.9989   |  12.4013     |      -9.39934  |      21.3971   | 6000 |  51 | nan         |    nan          | nan        | nan        |
| 5-fold      | DP          | log_memory_mb      | M1      |       0.00515086 |     0.0111793  |          -0.00873012 |            0.0190318 |          -0.00363276 |         0.011278   |               -0.0176363 |               0.0103708  |    1.42707  |   0.290654  |        1.06618  |        1.78797  |   0.25801  |   0.0325972  |       0.217535 |       0.298484 | 6000 |  42 | nan         |    nan          | nan        | nan        |
| 5-fold      | DP          | log_memory_mb      | M2      |       0.00202039 |     0.0092947  |          -0.0095205  |            0.0135613 |          -0.00869928 |         0.00939453 |               -0.0203641 |               0.00296558 |    1.42907  |   0.289548  |        1.06955  |        1.7886   |   0.266141 |   0.0328938  |       0.225298 |       0.306984 | 6000 |  51 | nan         |    nan          | nan        | nan        |
| full_sample | DP          | log_memory_mb      | M1      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  42 |   0.0151224 |      0.00817848 |   1.44157  |   0.250631 |
| full_sample | DP          | log_memory_mb      | M2      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  51 |   0.0162869 |      0.00785219 |   1.44072  |   0.257906 |
| LOFO        | BandB       | log_time_millis    | M1      |       0.480449   |     0.118522   |           0.333285   |            0.627613  |           0.475862   |         0.119568   |                0.327398  |               0.624326   |    1.85669  |   0.754732  |        0.919566 |        2.79381  |   1.41467  |   0.521158   |       0.767568 |       2.06177  | 6000 |  42 | nan         |    nan          | nan        | nan        |
| LOFO        | BandB       | log_time_millis    | M2      |      -0.173863   |     2.22039    |          -2.93084    |            2.58311   |          -0.190232   |         2.25135    |               -2.98565   |               2.60519    |    1.99467  |   1.97875   |       -0.462273 |        4.45162  |   0.837536 |   0.372701   |       0.374767 |       1.30031  | 6000 |  66 | nan         |    nan          | nan        | nan        |
| 5-fold      | BandB       | log_time_millis    | M1      |       0.74034    |     0.0299697  |           0.703127   |            0.777552  |           0.738047   |         0.0302343  |                0.700506  |               0.775588   |    1.55901  |   0.0731358 |        1.4682   |        1.64982  |   1.09205  |   0.0388345  |       1.04384  |       1.14027  | 6000 |  42 | nan         |    nan          | nan        | nan        |
| 5-fold      | BandB       | log_time_millis    | M2      |       0.340317   |     1.37694    |          -1.36938    |            2.05002   |           0.331118   |         1.39614    |               -1.40242   |               2.06466    |    1.55119  |   2.01671   |       -0.952886 |        4.05526  |   0.441001 |   0.0678326  |       0.356776 |       0.525226 | 6000 |  66 | nan         |    nan          | nan        | nan        |
| full_sample | BandB       | log_time_millis    | M1      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  42 |   0.745243  |      0.743447   |   1.54997  |   1.08431  |
| full_sample | BandB       | log_time_millis    | M2      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  66 |   0.961343  |      0.960913   |   0.60377  |   0.402062 |
| LOFO        | BandB       | log_nodes_explored | M1      |       0.391285   |     0.117607   |           0.245256   |            0.537313  |           0.38591    |         0.118645   |                0.238592  |               0.533228   |    2.09555  |   1.24961   |        0.543957 |        3.64714  |   1.59145  |   0.923118   |       0.445245 |       2.73765  | 6000 |  42 | nan         |    nan          | nan        | nan        |
| LOFO        | BandB       | log_nodes_explored | M2      |      -0.43948    |     2.98503    |          -4.14588    |            3.26692   |          -0.458937   |         3.02537    |               -4.21543   |               3.29756    |    1.52101  |   1.3744    |       -0.185537 |        3.22756  |   1.18028  |   1.39294    |      -0.549282 |       2.90984  | 6000 |  64 | nan         |    nan          | nan        | nan        |
| 5-fold      | BandB       | log_nodes_explored | M1      |       0.732091   |     0.0316794  |           0.692756   |            0.771426  |           0.729725   |         0.0319591  |                0.690043  |               0.769408   |    1.63388  |   0.0813526 |        1.53286  |        1.73489  |   1.12707  |   0.0380492  |       1.07983  |       1.17432  | 6000 |  42 | nan         |    nan          | nan        | nan        |
| 5-fold      | BandB       | log_nodes_explored | M2      |       0.977884   |     0.0055392  |           0.971007   |            0.984762  |           0.977585   |         0.00561407 |                0.970615  |               0.984556   |    0.467084 |   0.0634253 |        0.388331 |        0.545837 |   0.219136 |   0.00985447 |       0.2069   |       0.231371 | 6000 |  64 | nan         |    nan          | nan        | nan        |
| full_sample | BandB       | log_nodes_explored | M1      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  42 |   0.736373  |      0.734515   |   1.6263   |   1.12004  |
| full_sample | BandB       | log_nodes_explored | M2      |     nan          |   nan          |         nan          |          nan         |         nan          |       nan          |              nan         |             nan          |  nan        | nan         |      nan        |      nan        | nan        | nan          |     nan        |     nan        | 6000 |  64 |   0.979522  |      0.979301   |   0.453259 |   0.215107 |

### Fractional Logit Models
| cv_scheme   | algorithm   | response       | model   |   pseudo_r_squared_mean |   pseudo_r_squared_sd |   pseudo_r_squared_ci_lower |   pseudo_r_squared_ci_upper |     rmse_mean |       rmse_sd |   rmse_ci_lower |   rmse_ci_upper |      mae_mean |        mae_sd |   mae_ci_lower |   mae_ci_upper |    n |   p |   pseudo_r_squared |   log_likelihood |     aic |      bic |          rmse |           mae |
|:------------|:------------|:---------------|:--------|------------------------:|----------------------:|----------------------------:|----------------------------:|--------------:|--------------:|----------------:|----------------:|--------------:|--------------:|---------------:|---------------:|-----:|----:|-------------------:|-----------------:|--------:|---------:|--------------:|--------------:|
| LOFO        | Greedy      | optimality_gap | M1      |                0.213606 |            0.0252027  |                    0.182313 |                    0.244899 |   0.283726    |   0.410709    |    -0.226236    |     0.793688    |   0.251552    |   0.412639    |   -0.260808    |    0.763911    | 6000 |  42 |         nan        |          nan     | nan     |    nan   | nan           | nan           |
| LOFO        | Greedy      | optimality_gap | M2      |                0.271922 |            0.0233254  |                    0.242959 |                    0.300884 |   0.0798946   |   0.136308    |    -0.0893538   |     0.249143    |   0.0368182   |   0.0619499   |   -0.0401027   |    0.113739    | 6000 |  47 |         nan        |          nan     | nan     |    nan   | nan           | nan           |
| 5-fold      | Greedy      | optimality_gap | M1      |                0.216396 |            0.00332573 |                    0.212267 |                    0.220526 |   0.0185815   |   0.000885086 |     0.0174825   |     0.0196804   |   0.00734298  |   0.000154266 |    0.00715143  |    0.00753452  | 6000 |  42 |         nan        |          nan     | nan     |    nan   | nan           | nan           |
| 5-fold      | Greedy      | optimality_gap | M2      |                0.273553 |            0.00310668 |                    0.269695 |                    0.27741  |   0.012839    |   0.0035241   |     0.00846323  |     0.0172147   |   0.00484545  |   0.000262086 |    0.00452003  |    0.00517087  | 6000 |  47 |         nan        |          nan     | nan     |    nan   | nan           | nan           |
| full_sample | Greedy      | optimality_gap | M1      |              nan        |          nan          |                  nan        |                  nan        | nan           | nan           |   nan           |   nan           | nan           | nan           |  nan           |  nan           | 6000 |  42 |           0.215548 |         -197.72  | 481.44  | -51763.5 |   0.0178757   |   0.00713078  |
| full_sample | Greedy      | optimality_gap | M2      |              nan        |          nan          |                  nan        |                  nan        | nan           | nan           |   nan           |   nan           | nan           | nan           |  nan           |  nan           | 6000 |  47 |           0.273065 |         -183.223 | 462.446 | -51749   |   0.0115448   |   0.00464075  |
| LOFO        | DP          | fill_rate      | M1      |                0.253212 |            0.00111398 |                    0.251829 |                    0.254595 |   0.0577981   |   0.0965255   |    -0.0620541   |     0.17765     |   0.0208731   |   0.0322266   |   -0.0191414   |    0.0608877   | 6000 |  42 |         nan        |          nan     | nan     |    nan   | nan           | nan           |
| LOFO        | DP          | fill_rate      | M2      |                0.269793 |            0.00271405 |                    0.266423 |                    0.273163 |   0.00118448  |   0.0014817   |    -0.000655291 |     0.00302426  |   0.000446402 |   0.000645367 |   -0.000354926 |    0.00124773  | 6000 |  51 |         nan        |          nan     | nan     |    nan   | nan           | nan           |
| 5-fold      | DP          | fill_rate      | M1      |                0.252766 |            0.00240961 |                    0.249774 |                    0.255758 |   0.00763318  |   0.00244568  |     0.00459646  |     0.0106699   |   0.00249887  |   9.99051e-05 |    0.00237482  |    0.00262292  | 6000 |  42 |         nan        |          nan     | nan     |    nan   | nan           | nan           |
| 5-fold      | DP          | fill_rate      | M2      |                0.269836 |            0.00238847 |                    0.26687  |                    0.272801 |   0.000388552 |   0.000229854 |     0.00010315  |     0.000673953 |   6.71011e-05 |   9.95143e-06 |    5.47448e-05 |    7.94574e-05 | 6000 |  51 |         nan        |          nan     | nan     |    nan   | nan           | nan           |
| full_sample | DP          | fill_rate      | M1      |              nan        |          nan          |                  nan        |                  nan        | nan           | nan           |   nan           |   nan           | nan           | nan           |  nan           |  nan           | 6000 |  42 |           0.252615 |         -176.828 | 439.655 | -51814.8 |   0.00625518  |   0.00236899  |
| full_sample | DP          | fill_rate      | M2      |              nan        |          nan          |                  nan        |                  nan        | nan           | nan           |   nan           |   nan           | nan           | nan           |  nan           |  nan           | 6000 |  51 |           0.269849 |         -172.75  | 449.5   | -51744.7 |   0.000324187 |   5.98595e-05 |

### Elastic-Net Models (LOFO)
|   brier_score |   accuracy |     auc_roc |   precision |     recall |    f1 | fold               |   best_c |
|--------------:|-----------:|------------:|------------:|-----------:|------:|:-------------------|---------:|
|      0.242224 |   1        | nan         |  nan        | nan        | nan   | Uncorrelated       |   0.0001 |
|      0.242318 |   1        | nan         |  nan        | nan        | nan   | WeaklyCorrelated   |   0.0001 |
|      0.25873  |   0.943333 |   0.0181355 |    0        |   0        |   0   | StronglyCorrelated |   0.0001 |
|      0.243458 |   0.9      |   0.0970602 |    0        |   0        |   0   | InverseCorrelated  |   0.0001 |
|      0.243571 |   0.98     |   0.450975  |    0.142857 |   0.333333 |   0.2 | AlmostEqualRatios  |   0.0001 |


## Section 3 — Feature Importance

### Standardized Betas (Top 5 per model)
### Permutation Importance (Top 5 per model)

## Section 4 — Diagnostics

### VIF Thinning
| algorithm          | response           |   raw_delta_r2 |   thinned_delta_r2 |       diff |   removed_count |
|:-------------------|:-------------------|---------------:|-------------------:|-----------:|----------------:|
| Greedy             | log_time_millis    |     0.0015125  |        -0.0644894  | 0.0660019  |              19 |
| DynamicProgramming | log_time_millis    |     0.00131843 |        -0.00791379 | 0.00923223 |              20 |
| DynamicProgramming | log_memory_mb      |     0.00116447 |        -0.00106209 | 0.00222656 |              20 |
| BranchAndBound     | log_time_millis    |     0.2161     |         0.211188   | 0.00491177 |              20 |
| BranchAndBound     | log_nodes_explored |     0.243149   |         0.236783   | 0.00636553 |              20 |

### Smearing Factors
|   pooled_phi |     rmse_pooled |     rmse_family |   rmse_diff_pct | algorithm          | response           |
|-------------:|----------------:|----------------:|----------------:|:-------------------|:-------------------|
|      1.36585 |     0.0532483   |     0.0527189   |         1.00425 | Greedy             | log_time_millis    |
|      1.06636 |     3.14026     |     3.05037     |         2.94689 | DynamicProgramming | log_time_millis    |
|      1.12954 |     0.20832     |     0.207881    |         0.21123 | DynamicProgramming | log_memory_mb      |
|      7.3874  | 12663.7         | 35806.3         |       -64.6329  | BranchAndBound     | log_time_millis    |
|      8.79947 |     7.26517e+07 |     2.19122e+08 |       -66.8441  | BranchAndBound     | log_nodes_explored |

### Assumption Summaries
#### assumption_summary_BranchAndBound_log_nodes_explored.txt
```
bp_lm_stat: 347.63244870401945
bp_lm_pval: 1.333567238303858e-40
bp_f_stat: 5.703358383496374
bp_f_pval: 4.107339391331099e-42
max_vif: 55845712.74371526
max_cooks_d: 5.906267414573351
num_cooks_gt_1: 1
partial_resid_error: 'numpy.ndarray' object has no attribute 'index'

```

#### assumption_summary_BranchAndBound_log_time_millis.txt
```
bp_lm_stat: 335.4440765161106
bp_lm_pval: 1.040293828532126e-37
bp_f_stat: 5.323345711776337
bp_f_pval: 4.520287866487596e-39
max_vif: 55927605.85065563
max_cooks_d: 859.3265921917175
num_cooks_gt_1: 1
partial_resid_error: 'numpy.ndarray' object has no attribute 'index'

```

#### assumption_summary_BranchAndBound_optimal.txt
```
lambda_sd: 0.0
lambda_min: 10000.0
lambda_max: 10000.0

```

#### assumption_summary_DynamicProgramming_fill_rate.txt
```
link_test_pval: 0.0001865171026694218
link_test_sig: True
max_coef_diff_sv: 28.14442588089843
max_se_ratio: 0.0063956719087265084

```

#### assumption_summary_DynamicProgramming_log_memory_mb.txt
```
bp_lm_stat: 98.64957509806183
bp_lm_pval: 7.119144926622543e-05
bp_f_stat: 1.9495958815522931
bp_f_pval: 6.47568085504633e-05
max_vif: 87386602259.9613
max_cooks_d: 0.14770032438423494
num_cooks_gt_1: 0
partial_resid_error: 'numpy.ndarray' object has no attribute 'index'

```

#### assumption_summary_DynamicProgramming_log_time_millis.txt
```
bp_lm_stat: 328.0330775213391
bp_lm_pval: 1.0503563229026199e-41
bp_f_stat: 6.6142185929571315
bp_f_pval: 3.932142554568946e-43
max_vif: 88095137658.3564
max_cooks_d: 0.05637458345072051
num_cooks_gt_1: 0
partial_resid_error: 'numpy.ndarray' object has no attribute 'index'

```

#### assumption_summary_Greedy_log_time_millis.txt
```
bp_lm_stat: 170.70292896086502
bp_lm_pval: 6.107092151781727e-16
bp_f_stat: 3.708427980592422
bp_f_pval: 3.2064417035752434e-16
max_vif: 54452658.06273041
max_cooks_d: 0.07361311124267167
num_cooks_gt_1: 0
partial_resid_error: 'numpy.ndarray' object has no attribute 'index'

```

#### assumption_summary_Greedy_optimality_gap.txt
```
link_test_pval: 4.122452446888132e-05
link_test_sig: True
max_coef_diff_sv: 2.2655691657239525
max_se_ratio: 0.27762232785176905

```


## Section 5 — Figures

Catalogue of generated figures:
- `coefficient_trace.png` (from `figures/`)
- `importance_BandB_log_nodes_explored.png` (from `figures/`)
- `importance_BandB_log_time_millis.png` (from `figures/`)
- `importance_BandB_optimal.png` (from `figures/`)
- `importance_BandB_solution_gap.png` (from `figures/`)
- `importance_DP_fill_rate.png` (from `figures/`)
- `importance_DP_log_memory_mb.png` (from `figures/`)
- `importance_DP_log_time_millis.png` (from `figures/`)
- `importance_Greedy_log_time_millis.png` (from `figures/`)
- `importance_Greedy_optimality_gap.png` (from `figures/`)
- `lambda_path_fold_AlmostEqualRatios.png` (from `figures/`)
- `lambda_path_fold_InverseCorrelated.png` (from `figures/`)
- `lambda_path_fold_StronglyCorrelated.png` (from `figures/`)
- `lambda_path_fold_Uncorrelated.png` (from `figures/`)
- `lambda_path_fold_WeaklyCorrelated.png` (from `figures/`)
- `autocorr_BranchAndBound_log_nodes_explored.png` (from `diagnostics/`)
- `autocorr_BranchAndBound_log_time_millis.png` (from `diagnostics/`)
- `autocorr_DynamicProgramming_log_memory_mb.png` (from `diagnostics/`)
- `autocorr_DynamicProgramming_log_time_millis.png` (from `diagnostics/`)
- `autocorr_Greedy_log_time_millis.png` (from `diagnostics/`)
- `calibration_curve_BranchAndBound_optimal.png` (from `diagnostics/`)
- `cooks_BranchAndBound_log_nodes_explored.png` (from `diagnostics/`)
- `cooks_BranchAndBound_log_time_millis.png` (from `diagnostics/`)
- `cooks_DynamicProgramming_log_memory_mb.png` (from `diagnostics/`)
- `cooks_DynamicProgramming_log_time_millis.png` (from `diagnostics/`)
- `cooks_Greedy_log_time_millis.png` (from `diagnostics/`)
- `qq_BranchAndBound_log_nodes_explored.png` (from `diagnostics/`)
- `qq_BranchAndBound_log_time_millis.png` (from `diagnostics/`)
- `qq_DynamicProgramming_log_memory_mb.png` (from `diagnostics/`)
- `qq_DynamicProgramming_log_time_millis.png` (from `diagnostics/`)
- `qq_Greedy_log_time_millis.png` (from `diagnostics/`)
- `residual_hist_BranchAndBound_log_nodes_explored.png` (from `diagnostics/`)
- `residual_hist_BranchAndBound_log_time_millis.png` (from `diagnostics/`)
- `residual_hist_DynamicProgramming_log_memory_mb.png` (from `diagnostics/`)
- `residual_hist_DynamicProgramming_log_time_millis.png` (from `diagnostics/`)
- `residual_hist_Greedy_log_time_millis.png` (from `diagnostics/`)
- `residual_vs_fitted_BranchAndBound_log_nodes_explored.png` (from `diagnostics/`)
- `residual_vs_fitted_BranchAndBound_log_time_millis.png` (from `diagnostics/`)
- `residual_vs_fitted_DynamicProgramming_log_memory_mb.png` (from `diagnostics/`)
- `residual_vs_fitted_DynamicProgramming_log_time_millis.png` (from `diagnostics/`)
- `residual_vs_fitted_Greedy_log_time_millis.png` (from `diagnostics/`)

## Section 6 — Tables

Catalogue of CSV tables:
- `elasticnet_metrics.csv` (from `results/`)
- `flogit_inference_DP_fill_rate.csv` (from `results/`)
- `flogit_inference_Greedy_optimality_gap.csv` (from `results/`)
- `flogit_inference_aggregated.csv` (from `results/`)
- `flogit_metrics_DP_fill_rate.csv` (from `results/`)
- `flogit_metrics_Greedy_optimality_gap.csv` (from `results/`)
- `flogit_metrics_aggregated.csv` (from `results/`)
- `hurdle_metrics.csv` (from `results/`)
- `ols_inference_BandB_log_nodes_explored.csv` (from `results/`)
- `ols_inference_BandB_log_time_millis.csv` (from `results/`)
- `ols_inference_DP_log_memory_mb.csv` (from `results/`)
- `ols_inference_DP_log_time_millis.csv` (from `results/`)
- `ols_inference_Greedy_log_time_millis.csv` (from `results/`)
- `ols_inference_aggregated.csv` (from `results/`)
- `ols_metrics_BandB_log_nodes_explored.csv` (from `results/`)
- `ols_metrics_BandB_log_time_millis.csv` (from `results/`)
- `ols_metrics_DP_log_memory_mb.csv` (from `results/`)
- `ols_metrics_DP_log_time_millis.csv` (from `results/`)
- `ols_metrics_Greedy_log_time_millis.csv` (from `results/`)
- `ols_metrics_aggregated.csv` (from `results/`)
- `cv5_folds_BandB_log_nodes_explored.csv` (from `cross_validation/`)
- `cv5_folds_BandB_log_time_millis.csv` (from `cross_validation/`)
- `cv5_folds_DP_log_memory_mb.csv` (from `cross_validation/`)
- `cv5_folds_DP_log_time_millis.csv` (from `cross_validation/`)
- `cv5_folds_Greedy_log_time_millis.csv` (from `cross_validation/`)
- `cv5_folds_flogit_DP_fill_rate.csv` (from `cross_validation/`)
- `cv5_folds_flogit_Greedy_optimality_gap.csv` (from `cross_validation/`)
- `lofo_folds_BandB_log_nodes_explored.csv` (from `cross_validation/`)
- `lofo_folds_BandB_log_time_millis.csv` (from `cross_validation/`)
- `lofo_folds_DP_log_memory_mb.csv` (from `cross_validation/`)
- `lofo_folds_DP_log_time_millis.csv` (from `cross_validation/`)
- `lofo_folds_Greedy_log_time_millis.csv` (from `cross_validation/`)
- `lofo_folds_elasticnet.csv` (from `cross_validation/`)
- `lofo_folds_flogit_DP_fill_rate.csv` (from `cross_validation/`)
- `lofo_folds_flogit_Greedy_optimality_gap.csv` (from `cross_validation/`)
- `lofo_folds_hurdle.csv` (from `cross_validation/`)
- `correlation_verification_BranchAndBound.csv` (from `diagnostics/`)
- `correlation_verification_DynamicProgramming.csv` (from `diagnostics/`)
- `correlation_verification_Greedy.csv` (from `diagnostics/`)
- `full_sample_coefs_BandB_log_nodes_explored_M1.csv` (from `diagnostics/`)
- `full_sample_coefs_BandB_log_nodes_explored_M2.csv` (from `diagnostics/`)
- `full_sample_coefs_BandB_log_time_millis_M1.csv` (from `diagnostics/`)
- `full_sample_coefs_BandB_log_time_millis_M2.csv` (from `diagnostics/`)
- `full_sample_coefs_DP_log_memory_mb_M1.csv` (from `diagnostics/`)
- `full_sample_coefs_DP_log_memory_mb_M2.csv` (from `diagnostics/`)
- `full_sample_coefs_DP_log_time_millis_M1.csv` (from `diagnostics/`)
- `full_sample_coefs_DP_log_time_millis_M2.csv` (from `diagnostics/`)
- `full_sample_coefs_Greedy_log_time_millis_M1.csv` (from `diagnostics/`)
- `full_sample_coefs_Greedy_log_time_millis_M2.csv` (from `diagnostics/`)
- `full_sample_coefs_flogit_DP_fill_rate_M1.csv` (from `diagnostics/`)
- `full_sample_coefs_flogit_DP_fill_rate_M2.csv` (from `diagnostics/`)
- `full_sample_coefs_flogit_Greedy_optimality_gap_M1.csv` (from `diagnostics/`)
- `full_sample_coefs_flogit_Greedy_optimality_gap_M2.csv` (from `diagnostics/`)
- `residual_tests_ols.csv` (from `diagnostics/`)
- `se_comparison_DP_fill_rate_M1.csv` (from `diagnostics/`)
- `se_comparison_DP_fill_rate_M2.csv` (from `diagnostics/`)
- `se_comparison_Greedy_optimality_gap_M1.csv` (from `diagnostics/`)
- `se_comparison_Greedy_optimality_gap_M2.csv` (from `diagnostics/`)
- `smearing_factors.csv` (from `diagnostics/`)
- `std_beta_BandB_log_nodes_explored_M2.csv` (from `diagnostics/`)
- `std_beta_BandB_log_time_millis_M2.csv` (from `diagnostics/`)
- `std_beta_DP_log_memory_mb_M2.csv` (from `diagnostics/`)
- `std_beta_DP_log_time_millis_M2.csv` (from `diagnostics/`)
- `std_beta_Greedy_log_time_millis_M2.csv` (from `diagnostics/`)
- `std_beta_flogit_DP_fill_rate_M2.csv` (from `diagnostics/`)
- `std_beta_flogit_Greedy_optimality_gap_M2.csv` (from `diagnostics/`)
- `vif_BranchAndBound_log_nodes_explored.csv` (from `diagnostics/`)
- `vif_BranchAndBound_log_time_millis.csv` (from `diagnostics/`)
- `vif_DynamicProgramming_log_memory_mb.csv` (from `diagnostics/`)
- `vif_DynamicProgramming_log_time_millis.csv` (from `diagnostics/`)
- `vif_Greedy_log_time_millis.csv` (from `diagnostics/`)
- `vif_removed_predictors_BranchAndBound_log_nodes_explored.csv` (from `diagnostics/`)
- `vif_removed_predictors_BranchAndBound_log_time_millis.csv` (from `diagnostics/`)
- `vif_removed_predictors_DynamicProgramming_log_memory_mb.csv` (from `diagnostics/`)
- `vif_removed_predictors_DynamicProgramming_log_time_millis.csv` (from `diagnostics/`)
- `vif_removed_predictors_Greedy_log_time_millis.csv` (from `diagnostics/`)
- `vif_thinned_delta_r2_comparison.csv` (from `diagnostics/`)

## Section 7 — Unexpected Findings


## Section 8 — Traceability Matrix

| Claim | Archive File | Paper Section |
|---|---|---|
| OLS Performance | output/results/ols_metrics_aggregated.csv | Model Performance |
| VIF Thinning Robustness | output/diagnostics/vif_thinned_delta_r2_comparison.csv | Diagnostics |
| Smearing Factors | output/diagnostics/smearing_factors.csv | Diagnostics |
