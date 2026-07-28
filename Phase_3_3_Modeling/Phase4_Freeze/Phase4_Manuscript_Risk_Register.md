# Phase 4 Manuscript Risk Register

| Risky Statement | Evidence-Safe Version |
| :--- | :--- |
| "Adding execution metrics significantly improves Branch and Bound performance predictions." | "Adding execution metrics increases the in-sample explained variance ($R^2$) of the Branch and Bound execution time model by $\Delta R^2 = 0.216$." |
| "Dynamic Programming is completely deterministic based on instance characteristics." | "For Dynamic Programming, instance characteristics alone explain 97.7% of the variance in execution time, leaving negligible residual variance for execution metrics to explain." |
| "The fractional logit models fail the link test, indicating they are misspecified." | "The link test for the fractional logit models is statistically significant, suggesting potential non-linearity in the logit scale." |
| "The models generalize well to new instances." | "In 5-fold and LOFO cross-validation on the 6,000-instance dataset, the models exhibit stable $R^2$ and RMSE performance, indicating robust in-distribution prediction." |
| "VIF thinning proves the models have no multicollinearity." | "VIF thinning (threshold > 10) removed 20 highly collinear predictors from the Branch and Bound model. The resulting thinned model exhibited a $\Delta R^2$ drop of only 0.006, suggesting the model's explanatory power is not primarily driven by multicollinearity." |
