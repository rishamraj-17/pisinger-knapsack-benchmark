from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats as sp_stats


def fit_ols(
    X: pd.DataFrame, y: np.ndarray
) -> sm.regression.linear_model.RegressionResultsWrapper:
    X_with_const = sm.add_constant(X.astype(float), prepend=True, has_constant='add')
    model = sm.OLS(y.astype(float), X_with_const).fit()
    return model


def predict_ols(
    model: sm.regression.linear_model.RegressionResultsWrapper,
    X: pd.DataFrame,
) -> np.ndarray:
    X_with_const = sm.add_constant(X.astype(float), prepend=True, has_constant='add')
    return model.predict(X_with_const).values


def ols_coefficients(
    model: sm.regression.linear_model.RegressionResultsWrapper,
    predictor_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    if hasattr(model.params, 'index'):
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
        "t_stat": tvalues,
        "p_value": pvalues,
        "ci_lower": ci[:, 0],
        "ci_upper": ci[:, 1],
    })
    return coefs


def cluster_robust_se(
    model: sm.regression.linear_model.RegressionResultsWrapper,
    groups: np.ndarray,
) -> sm.regression.linear_model.RegressionResultsWrapper:
    cr_model = model.get_robustcov_results(
        cov_type="cluster", groups=groups
    )
    return cr_model


def incremental_f_test(
    ssr_reduced: float,
    ssr_full: float,
    df_resid_reduced: int,
    df_resid_full: int,
) -> Dict[str, float]:
    delta_df = df_resid_reduced - df_resid_full
    if delta_df <= 0:
        return {"f_stat": float("nan"), "p_value": float("nan"), "delta_df": 0}
    f_stat = ((ssr_reduced - ssr_full) / delta_df) / (ssr_full / df_resid_full)
    p_value = float(1.0 - sp_stats.f.cdf(f_stat, delta_df, df_resid_full))
    return {
        "f_stat": float(f_stat),
        "p_value": p_value,
        "delta_df": int(delta_df),
    }


def standardized_beta(
    X: pd.DataFrame, y: np.ndarray
) -> pd.DataFrame:
    X_scaled = X.astype(float).copy()
    for col in X_scaled.columns:
        std = X_scaled[col].std(ddof=0)
        if std > 0:
            X_scaled[col] = (X_scaled[col] - X_scaled[col].mean()) / std
        else:
            X_scaled[col] = 0.0
    y_std = float(y.std(ddof=0))
    if y_std > 0:
        y_scaled = (y - y.mean()) / y_std
    else:
        y_scaled = np.zeros_like(y)
    model_scaled = fit_ols(X_scaled, y_scaled)
    std_coefs = ols_coefficients(model_scaled)
    std_coefs["coefficient"] = model_scaled.params.values
    return std_coefs


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
    y_std = float(y.std(ddof=0))
    if y_std > 0:
        y_scaled = (y - y.mean()) / y_std
    else:
        y_scaled = np.zeros_like(y)
    model_scaled = fit_fractional_logit(X_scaled, y_scaled)
    std_coefs = flogit_coefficients(model_scaled)
    std_coefs["coefficient"] = model_scaled.params.values
    return std_coefs


def fit_fractional_logit(
    X: pd.DataFrame, y: np.ndarray
):
    X_with_const = sm.add_constant(X.astype(float), prepend=True, has_constant='add')
    model = sm.GLM(
        y.astype(float),
        X_with_const,
        family=sm.families.Binomial(),
        cov_type='HC3',
    ).fit(maxiter=100, disp=False)
    if not model.converged:
        import warnings
        warnings.warn("Fractional logit GLM did not converge")
    return model


def predict_fractional_logit(
    model,
    X: pd.DataFrame,
) -> np.ndarray:
    X_with_const = sm.add_constant(X.astype(float), prepend=True, has_constant='add')
    return model.predict(X_with_const).values


def flogit_coefficients(
    model,
    predictor_names=None,
) -> pd.DataFrame:
    if hasattr(model.params, 'index'):
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
        "t_stat": tvalues,
        "p_value": pvalues,
        "ci_lower": ci[:, 0],
        "ci_upper": ci[:, 1],
    })
    return coefs


def _fast_pseudo_r2(X: np.ndarray, y: np.ndarray) -> float:
    Xc = sm.add_constant(X, prepend=True, has_constant='add')
    model = sm.GLM(
        y.astype(float), Xc,
        family=sm.families.Binomial(),
    ).fit(maxiter=100, disp=False)
    if not model.converged or model.llf is None or model.llnull is None or model.llnull == 0:
        del model
        return 0.0
    result = float(1.0 - model.llf / model.llnull)
    del model
    # statsmodels GLM.fit() creates reference cycles; gc reclaims them
    import gc
    gc.collect()
    return result


def bootstrap_delta_pseudo_r2(
    X_m1: pd.DataFrame,
    X_m2: pd.DataFrame,
    y: np.ndarray,
    family: np.ndarray,
    n_resamples: int = 1999,
    rng=None,
):
    if rng is None:
        rng = np.random.default_rng(42)
    unique_families = np.unique(family)
    family_indices = {
        fam: np.where(family == fam)[0]
        for fam in unique_families
    }
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

        pr2_m1 = _fast_pseudo_r2(X_m1_boot, y_boot)
        pr2_m2 = _fast_pseudo_r2(X_m2_boot, y_boot)

        delta_pseudo_r2_values[i] = pr2_m2 - pr2_m1

    ci_lower = float(np.percentile(delta_pseudo_r2_values, 2.5))
    ci_upper = float(np.percentile(delta_pseudo_r2_values, 97.5))
    return delta_pseudo_r2_values, (ci_lower, ci_upper)


def _fast_r2(X: np.ndarray, y: np.ndarray) -> float:
    from sklearn.linear_model import LinearRegression
    lr = LinearRegression(fit_intercept=True)
    lr.fit(X, y)
    return float(lr.score(X, y))


def bootstrap_delta_r2(
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
    family_indices = {
        fam: np.where(family == fam)[0]
        for fam in unique_families
    }
    X_m1_arr = X_m1.values.astype(float)
    X_m2_arr = X_m2.values.astype(float)
    y_arr = y.astype(float)

    delta_r2_values = np.empty(n_resamples)
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
        r2_m1 = _fast_r2(X_m1_boot, y_boot)
        r2_m2 = _fast_r2(X_m2_boot, y_boot)
        delta_r2_values[i] = r2_m2 - r2_m1
    ci_lower = float(np.percentile(delta_r2_values, 2.5))
    ci_upper = float(np.percentile(delta_r2_values, 97.5))
    return delta_r2_values, (ci_lower, ci_upper)
