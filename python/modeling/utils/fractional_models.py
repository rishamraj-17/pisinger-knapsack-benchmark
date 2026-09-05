import numpy as np
import pandas as pd
import statsmodels.api as sm

from utils.models import (
    fit_fractional_logit,
    predict_fractional_logit,
    flogit_coefficients,
    standardized_beta_flogit,
    bootstrap_delta_pseudo_r2,
)


def fit_fractional_logit_unadjusted(X, y):
    X_with_const = sm.add_constant(X.astype(float), prepend=True, has_constant='add')
    model = sm.GLM(
        y.astype(float),
        X_with_const,
        family=sm.families.Binomial(),
    ).fit(maxiter=100, disp=False)
    if not model.converged:
        import warnings
        warnings.warn("Fractional logit GLM (unadjusted) did not converge")
    return model


def flogit_cluster_robust_se(model, groups):
    X = model.model.exog
    y = model.model.endog
    family = model.family
    cr_model = sm.GLM(
        y, X, family=family,
    ).fit(
        cov_type='cluster', cov_kwds={'groups': groups},
        maxiter=100, disp=False,
    )
    if not cr_model.converged:
        import warnings
        warnings.warn("Fractional logit GLM (cluster SE) did not converge")
    return cr_model


def extract_ll_aic_bic(model):
    llf = float(model.llf) if model.llf is not None else float("nan")
    llnull = float(model.llnull) if model.llnull is not None else float("nan")
    aic_val = float(model.aic) if hasattr(model, 'aic') and model.aic is not None else float("nan")
    bic_val = float(model.bic) if hasattr(model, 'bic') and model.bic is not None else float("nan")
    return {
        "log_likelihood": llf,
        "null_log_likelihood": llnull,
        "aic": aic_val,
        "bic": bic_val,
    }
