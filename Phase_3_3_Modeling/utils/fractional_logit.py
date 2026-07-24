from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.families.links import Logit

EPS_LOG: float = 1e-15


def _bernoulli_log_likelihood(
    y: np.ndarray, y_pred: np.ndarray
) -> float:
    y_pred_clipped = np.clip(y_pred, EPS_LOG, 1.0 - EPS_LOG)
    return float(
        np.sum(y * np.log(y_pred_clipped) + (1.0 - y) * np.log(1.0 - y_pred_clipped))
    )


def _pseudo_r2_value(
    y: np.ndarray, y_pred: np.ndarray, y_bar: float
) -> float:
    ll_model = _bernoulli_log_likelihood(y, y_pred)
    ll_null = _bernoulli_log_likelihood(y, np.full_like(y, y_bar))
    if ll_null == 0:
        return 0.0
    return float(1.0 - ll_model / ll_null)


def fit_fractional_logit(
    X: pd.DataFrame, y: np.ndarray
) -> sm.genmod.generalized_linear_model.GLMResultsWrapper:
    X_with_const = sm.add_constant(X.astype(float), prepend=True, has_constant="add")
    model = sm.GLM(y.astype(float), X_with_const, family=Binomial(link=Logit())).fit()
    return model


def predict_fractional_logit(
    model: sm.genmod.generalized_linear_model.GLMResultsWrapper,
    X: pd.DataFrame,
) -> np.ndarray:
    X_with_const = sm.add_constant(X.astype(float), prepend=True, has_constant="add")
    return model.predict(X_with_const).values


def flogit_coefficients(
    model: sm.genmod.generalized_linear_model.GLMResultsWrapper,
    predictor_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    if hasattr(model.params, "index"):
        pred_names = list(model.params.index)
    elif predictor_names is not None:
        pred_names = predictor_names
    else:
        pred_names = [f"x{i}" for i in range(len(model.params))]

    params = np.asarray(model.params)
    bse = np.asarray(model.bse)
    tvalues = np.asarray(model.tvalues)
    pvalues = np.asarray(model.pvalues)
    ci = np.asarray(model.conf_int())

    coefs = pd.DataFrame({
        "predictor": pred_names,
        "coefficient": params,
        "se": bse,
        "z_stat": tvalues,
        "p_value": pvalues,
        "ci_lower": ci[:, 0],
        "ci_upper": ci[:, 1],
    })
    return coefs


def cluster_robust_se_flogit(
    model: sm.genmod.generalized_linear_model.GLMResultsWrapper,
    groups: np.ndarray,
) -> sm.genmod.generalized_linear_model.GLMResultsWrapper:
    X = model.model.exog
    y = model.model.endog
    family = model.model.family
    cr_model = sm.GLM(y, X, family=family).fit(
        cov_type="cluster", cov_kwds={"groups": groups}
    )
    return cr_model


def pseudo_r_squared_mcfadden(
    model: sm.genmod.generalized_linear_model.GLMResultsWrapper,
    y: np.ndarray,
) -> float:
    y_pred = model.predict()
    y_bar = float(np.mean(y))
    return _pseudo_r2_value(y, y_pred, y_bar)


def _fast_pseudo_r2(
    X: np.ndarray, y: np.ndarray
) -> float:
    Xc = sm.add_constant(X, prepend=True, has_constant="add")
    model = sm.GLM(y, Xc, family=Binomial(link=Logit())).fit(disp=False)
    y_pred = model.predict(Xc)
    y_bar = float(np.mean(y))
    return _pseudo_r2_value(y, y_pred, y_bar)


def bootstrap_delta_pseudo_r2(
    X_m1: pd.DataFrame,
    X_m2: pd.DataFrame,
    y: np.ndarray,
    family: np.ndarray,
    n_resamples: int = 1999,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, Tuple[float, float]]:
    if rng is None:
        rng = np.random.default_rng(42)
    unique_families = np.unique(family)
    family_indices = {fam: np.where(family == fam)[0] for fam in unique_families}
    X_m1_arr = X_m1.values.astype(float)
    X_m2_arr = X_m2.values.astype(float)
    y_arr = y.astype(float)

    delta_pseudo_r2_values = np.empty(n_resamples)
    for i in range(n_resamples):
        all_boot_idx = []
        for fam in unique_families:
            fam_idx = family_indices[fam]
            n_fam = len(fam_idx)
            boot_fam = rng.choice(fam_idx, size=n_fam, replace=True)
            all_boot_idx.append(boot_fam)
        boot_idx = np.concatenate(all_boot_idx)
        y_boot = y_arr[boot_idx]
        X_m1_boot = X_m1_arr[boot_idx]
        X_m2_boot = X_m2_arr[boot_idx]
        pseudo_r2_m1 = _fast_pseudo_r2(X_m1_boot, y_boot)
        pseudo_r2_m2 = _fast_pseudo_r2(X_m2_boot, y_boot)
        delta_pseudo_r2_values[i] = pseudo_r2_m2 - pseudo_r2_m1

    ci_lower = float(np.percentile(delta_pseudo_r2_values, 2.5))
    ci_upper = float(np.percentile(delta_pseudo_r2_values, 97.5))
    return delta_pseudo_r2_values, (ci_lower, ci_upper)


def standardized_beta_flogit(
    X: pd.DataFrame, y: np.ndarray
) -> pd.DataFrame:
    X_scaled = X.astype(float).copy()
    for col in X_scaled.columns:
        std = X_scaled[col].std(ddof=0)
        if std > 0:
            X_scaled[col] = (X_scaled[col] - X_scaled[col].mean()) / std
        else:
            X_scaled[col] = 0.0
    model_scaled = fit_fractional_logit(X_scaled, y)
    std_coefs = flogit_coefficients(model_scaled)
    return std_coefs
