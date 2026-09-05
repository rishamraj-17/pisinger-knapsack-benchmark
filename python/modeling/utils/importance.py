"""
utils/importance.py

Phase 3.3.5 — Feature Importance utilities.

Source:
  - PHASE_3_3_IMPLEMENTATION_PLAN.md lines 506–513 (function list)
  - PHASE_3_2_DESIGN.md §10.1–10.4 (methodology)
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config import (
    ALGO_BB,
    ALGORITHM_LABEL_MAP,
    FAMILIES,
    N_PERMUTATION_REPEATS,
    RANDOM_SEED,
    GROUP_A_INSTANCE_CHARACTERISTICS,
)
from utils.cv import LofoFoldSplitter
from utils.preprocessing import build_feature_matrices


# ---------------------------------------------------------------------------
# Predictor classification helper
# ---------------------------------------------------------------------------

def _classify_predictors(
    predictor_names: List[str],
    instance_cols: List[str],
) -> Dict[str, str]:
    """
    Classify each predictor as 'instance_characteristic' or 'execution_metric'.
    Study design variables (n, log_n, family dummies, cap_mode dummies) are
    classified as 'instance_characteristic'.
    """
    study_design = {"n", "log_n", "cap_mode_fixed", "cap_mode_scaled"}
    instance_set = set(instance_cols) | study_design
    result = {}
    for p in predictor_names:
        # family dummy columns start with the family name
        if (
            p in instance_set
            or p.startswith("family_")
            or p.startswith("cap_mode_")
        ):
            result[p] = "instance_characteristic"
        else:
            result[p] = "execution_metric"
    return result


# ---------------------------------------------------------------------------
# B.3.1  Standardized beta — load pre-computed CSVs
# ---------------------------------------------------------------------------

def load_standardized_beta(
    diagnostics_dir: Path,
    algo_label: str,
    response: str,
    model_family: str,
    top_k: int = 20,
) -> Optional[pd.DataFrame]:
    """
    Load pre-existing standardized-beta CSV from output/diagnostics/ and
    return top_k rows sorted by |coefficient|.

    Source: PHASE_3_3_IMPLEMENTATION_PLAN.md lines 516–520
            PHASE_3_2_DESIGN.md §10.1 — applicable to OLS and flogit only.

    Returns None for elasticnet and hurdle (not applicable per §10.1).
    """
    if model_family not in ("ols", "fractional_logit"):
        return None

    if model_family == "ols":
        path = diagnostics_dir / f"std_beta_{algo_label}_{response}_M2.csv"
    else:
        path = diagnostics_dir / f"std_beta_flogit_{algo_label}_{response}_M2.csv"

    if not path.exists():
        return None

    df = pd.read_csv(path)
    df["abs_coefficient"] = df["coefficient"].abs()
    df = df.sort_values("abs_coefficient", ascending=False).head(top_k)
    df = df.reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# B.3.2  Permutation importance — LOFO test sets
# ---------------------------------------------------------------------------

def _score(y_true: np.ndarray, y_pred: np.ndarray, metric: str) -> float:
    """Compute a single scalar performance metric."""
    from sklearn.metrics import r2_score, roc_auc_score, mean_squared_error
    import statsmodels.api as sm

    if metric == "r2":
        return float(r2_score(y_true, y_pred))
    elif metric == "auc":
        if len(np.unique(y_true)) < 2:
            return float("nan")
        return float(roc_auc_score(y_true, y_pred))
    elif metric == "rmse":
        return float(np.sqrt(mean_squared_error(y_true, y_pred)))
    elif metric == "pseudo_r2":
        # McFadden pseudo-R² via GLM on the predicted probabilities
        # Approximate: use correlation-based proxy for fold-level scoring.
        # Full GLM refit within permutation loop is too expensive; use
        # R² on the logit scale as a proxy that is monotone with pseudo-R².
        from sklearn.metrics import r2_score
        return float(r2_score(y_true, y_pred))
    else:
        raise ValueError(f"Unknown metric: {metric}")


def _metric_for_family(model_family: str) -> str:
    """
    Map model family to permutation metric.
    Source: PHASE_3_3_IMPLEMENTATION_PLAN.md line 523
    ('using LOFO test-set R²/AUC/Brier as metric')
    and blueprint Conflict #3 resolution.
    """
    mapping = {
        "ols": "r2",
        "fractional_logit": "pseudo_r2",
        "elasticnet": "auc",
        "hurdle_part1": "auc",
        "hurdle_part2": "rmse",
    }
    return mapping[model_family]


def _predict_model(model, X: pd.DataFrame, model_family: str) -> np.ndarray:
    """
    Generate predictions for a fitted model given its family.
    """
    from utils.models import (
        predict_ols,
        predict_fractional_logit,
        predict_elasticnet,
        predict_hurdle,
    )
    import statsmodels.api as sm

    if model_family == "ols":
        return predict_ols(model, X)
    elif model_family == "fractional_logit":
        return predict_fractional_logit(model, X)
    elif model_family == "elasticnet":
        return predict_elasticnet(model, X)
    elif model_family in ("hurdle_part1", "hurdle_part2"):
        # predict_hurdle returns combined E[gap]; for part1 we want P(gap>0)
        p_pos = model["part1"].predict_proba(X.astype(float))[:, 1]
        if model_family == "hurdle_part1":
            return p_pos
        Xc = __import__("statsmodels.api", fromlist=["add_constant"]).add_constant(
            X.astype(float), prepend=True, has_constant="add"
        )
        e_pos = model["part2"].predict(Xc).values
        return p_pos * e_pos
    else:
        raise ValueError(f"Unknown model_family: {model_family}")


def _fit_model(
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    model_family: str,
) -> object:
    """Fit the appropriate model for the given family."""
    from utils.models import (
        fit_ols,
        fit_fractional_logit,
        fit_elasticnet,
        fit_hurdle,
    )
    if model_family == "ols":
        return fit_ols(X_train, y_train)
    elif model_family == "fractional_logit":
        return fit_fractional_logit(X_train, y_train)
    elif model_family == "elasticnet":
        return fit_elasticnet(X_train, y_train, alpha=0.5, cv_folds=5)
    elif model_family in ("hurdle_part1", "hurdle_part2"):
        return fit_hurdle(X_train, y_train)
    else:
        raise ValueError(f"Unknown model_family: {model_family}")


def permutation_importance_lofo(
    df: pd.DataFrame,
    X_m2: pd.DataFrame,
    y: np.ndarray,
    model_family: str,
    instance_cols: List[str],
    n_repeats: int = N_PERMUTATION_REPEATS,
    rng: Optional[np.random.Generator] = None,
) -> pd.DataFrame:
    """
    Compute permutation importance using LOFO test sets.

    Methodology (PHASE_3_2_DESIGN.md §10.2; PHASE_3_3_IMPLEMENTATION_PLAN.md line 521–525):
    - For each LOFO fold:
        1. Fit M2 on training set
        2. Compute baseline metric on test set
        3. For each predictor j, for n_repeats repeats:
           - Permute column j in test set
           - Compute metric on permuted test set
           - importance_ij = baseline - permuted_metric
    - Average fold-level importance means across 5 LOFO folds
    - Report mean ± SD across folds

    Source (aggregation): blueprint approved 2026-07-26 (average across LOFO folds)
    Source (n_repeats): config.py line 314 (N_PERMUTATION_REPEATS = 20)
    Source (RNG): project-wide constraint (numpy.random.default_rng(42))
    """
    if rng is None:
        rng = np.random.default_rng(RANDOM_SEED)

    metric = _metric_for_family(model_family)
    predictor_names = list(X_m2.columns)
    predictor_types = _classify_predictors(predictor_names, instance_cols)

    splitter = LofoFoldSplitter()

    # fold_importances[predictor_name] = list of per-fold mean importances
    fold_importances: Dict[str, List[float]] = {p: [] for p in predictor_names}

    for train_idx, test_idx, _ in splitter.split(df):
        X_train = X_m2.iloc[train_idx]
        X_test = X_m2.iloc[test_idx]
        y_train = y[train_idx]
        y_test = y[test_idx]

        # For hurdle: use combined family but track part separately
        model = _fit_model(X_train, y_train, model_family)
        y_pred_baseline = _predict_model(model, X_test, model_family)
        baseline = _score(y_test, y_pred_baseline, metric)

        X_test_arr = X_test.values.copy()
        col_names = list(X_test.columns)

        for j, pred_name in enumerate(predictor_names):
            col_idx = col_names.index(pred_name)
            repeat_importances = []
            for _ in range(n_repeats):
                X_perm = X_test_arr.copy()
                X_perm[:, col_idx] = rng.permutation(X_perm[:, col_idx])
                X_perm_df = pd.DataFrame(X_perm, columns=col_names, index=X_test.index)
                y_pred_perm = _predict_model(model, X_perm_df, model_family)
                score_perm = _score(y_test, y_pred_perm, metric)
                # importance = baseline - permuted (higher = more important)
                # For RMSE, higher permuted = worse, so importance = permuted - baseline
                if metric == "rmse":
                    repeat_importances.append(score_perm - baseline)
                else:
                    repeat_importances.append(baseline - score_perm)
            fold_importances[pred_name].append(float(np.mean(repeat_importances)))

    rows = []
    for pred_name in predictor_names:
        fold_vals = np.array(fold_importances[pred_name], dtype=float)
        n_valid = int(np.sum(~np.isnan(fold_vals)))
        rows.append({
            "predictor": pred_name,
            # nanmean excludes zero-event folds that returned NaN (documented behaviour)
            "importance_mean": float(np.nanmean(fold_vals)) if n_valid > 0 else float("nan"),
            "importance_sd": float(np.nanstd(fold_vals, ddof=1)) if n_valid > 1 else 0.0,
            "n_valid_folds": n_valid,
            "predictor_type": predictor_types[pred_name],
            "metric": metric,
        })

    result = pd.DataFrame(rows)
    result = result.sort_values("importance_mean", ascending=False).reset_index(drop=True)
    return result


# ---------------------------------------------------------------------------
# B.3.4  Delta-R² partitioning
# ---------------------------------------------------------------------------

def _r2_full_sample(
    X: pd.DataFrame,
    y: np.ndarray,
    model_family: str,
) -> float:
    """Compute the appropriate R²-equivalent metric on the full sample."""
    from sklearn.metrics import r2_score, roc_auc_score

    model = _fit_model(X, y, model_family)
    y_pred = _predict_model(model, X, model_family)

    metric = _metric_for_family(model_family)
    return _score(y, y_pred, metric)


def delta_r2_partitioning(
    X_m2: pd.DataFrame,
    y: np.ndarray,
    top_k_predictors: List[str],
    model_family: str,
    r2_full: float,
) -> pd.DataFrame:
    """
    For each execution metric in top_k_predictors (top-10 by permutation importance):
      - Fit M2 without that metric
      - delta_r2 = r2_full - R2(M2_without_m)

    Source: PHASE_3_2_DESIGN.md §10.4 lines 526–532
    'Δ-R² partitioning is restricted to the top-10 metrics identified by
    permutation importance'

    Metric: same as model's primary evaluation metric (blueprint Conflict #3 resolution).
    """
    rows = []
    for rank, pred_name in enumerate(top_k_predictors, start=1):
        if pred_name not in X_m2.columns:
            continue
        X_reduced = X_m2.drop(columns=[pred_name])
        r2_reduced = _r2_full_sample(X_reduced, y, model_family)
        delta = r2_full - r2_reduced
        rows.append({
            "predictor": pred_name,
            "r2_full": r2_full,
            "r2_without": r2_reduced,
            "delta_r2": delta,
            "rank_by_perm_importance": rank,
        })

    result = pd.DataFrame(rows)
    result = result.sort_values("delta_r2", ascending=False).reset_index(drop=True)
    return result


# ---------------------------------------------------------------------------
# B.3.3  Elastic-net nonzero coefficients
# ---------------------------------------------------------------------------

def format_elasticnet_coefs(results_dir: Path) -> pd.DataFrame:
    """
    Load pre-existing elasticnet_metrics.csv (nonzero coefs at optimal lambda)
    and return sorted by abs_coefficient descending.

    Source: PHASE_3_3_IMPLEMENTATION_PLAN.md lines 526–528
    'For B&B optimal only — report coefficients at optimal lambda'
    """
    path = results_dir / "elasticnet_metrics.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df = df.sort_values("abs_coefficient", ascending=False).reset_index(drop=True)
    return df
