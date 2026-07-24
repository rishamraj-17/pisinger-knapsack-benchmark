import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

from config import (
    ALGO_DP, ALGO_GREEDY,
    ALGORITHM_LABEL_MAP,
    MODEL_SPECS,
    N_BOOTSTRAP_RESAMPLES,
    RANDOM_SEED,
)
from utils.fractional_logit import (
    fit_fractional_logit,
    predict_fractional_logit,
    flogit_coefficients,
    cluster_robust_se_flogit,
    pseudo_r_squared_mcfadden,
    standardized_beta_flogit,
    bootstrap_delta_pseudo_r2,
    _bernoulli_log_likelihood,
)
from utils.preprocessing import build_feature_matrices
from utils.cv import LofoFoldSplitter, FiveFoldStratifiedSplitter
from utils.metrics import (
    brier_score,
    rmse,
    mae,
    cohens_f2,
)

RNG = np.random.default_rng(RANDOM_SEED)
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PREPARED_DIR = OUTPUT_DIR / "prepared"
RESULTS_DIR = OUTPUT_DIR / "results"
CV_DIR = OUTPUT_DIR / "cross_validation"
DIAG_DIR = OUTPUT_DIR / "diagnostics"


def _compute_cv_metrics(
    y_true_fold: np.ndarray,
    y_pred_fold: np.ndarray,
    y_train_mean: float,
) -> dict:
    y_bar = y_train_mean
    ll_model_fold = _bernoulli_log_likelihood(y_true_fold, y_pred_fold)
    ll_null_fold = _bernoulli_log_likelihood(y_true_fold, np.full_like(y_true_fold, y_bar))
    pseudo_r2 = 1.0 - ll_model_fold / ll_null_fold if ll_null_fold != 0 else 0.0
    brier = brier_score(y_true_fold, y_pred_fold)
    rmse_val = rmse(y_true_fold, y_pred_fold)
    mae_val = mae(y_true_fold, y_pred_fold)
    return {
        "pseudo_r_squared": float(pseudo_r2),
        "brier_score": brier,
        "rmse": rmse_val,
        "mae": mae_val,
    }


def _aggregate_cv_metrics(fold_metrics: list, n_folds: int) -> dict:
    metrics_df = pd.DataFrame(fold_metrics)
    agg = {}
    for col in ["pseudo_r_squared", "brier_score", "rmse", "mae"]:
        values = metrics_df[col].values.astype(float)
        mean_val = float(np.mean(values))
        sd_val = float(np.std(values, ddof=1)) if n_folds > 1 else 0.0
        t_val = sp_stats.t.ppf(0.975, df=n_folds - 1) if n_folds > 1 else float("nan")
        ci_half = t_val * sd_val / np.sqrt(n_folds) if n_folds > 1 else float("nan")
        agg[f"{col}_mean"] = mean_val
        agg[f"{col}_sd"] = sd_val
        agg[f"{col}_ci_lower"] = mean_val - ci_half
        agg[f"{col}_ci_upper"] = mean_val + ci_half
    return agg


def run_lofo_cv(
    df: pd.DataFrame,
    X_m1: pd.DataFrame,
    X_m2: pd.DataFrame,
    y: np.ndarray,
) -> dict:
    splitter = LofoFoldSplitter()
    m1_fold_metrics = []
    m2_fold_metrics = []
    m1_fold_preds: list = []
    m2_fold_preds: list = []
    fold_labels: list = []

    for train_idx, test_idx, held_out_family in splitter.split(df):
        y_train, y_test = y[train_idx], y[test_idx]
        y_train_mean = float(np.mean(y_train))
        X_m1_train, X_m1_test = X_m1.iloc[train_idx], X_m1.iloc[test_idx]
        X_m2_train, X_m2_test = X_m2.iloc[train_idx], X_m2.iloc[test_idx]

        model_m1 = fit_fractional_logit(X_m1_train, y_train)
        model_m2 = fit_fractional_logit(X_m2_train, y_train)

        y_pred_m1 = predict_fractional_logit(model_m1, X_m1_test)
        y_pred_m2 = predict_fractional_logit(model_m2, X_m2_test)

        m1_metrics = _compute_cv_metrics(y_test, y_pred_m1, y_train_mean)
        m2_metrics = _compute_cv_metrics(y_test, y_pred_m2, y_train_mean)

        for d in [m1_metrics, m2_metrics]:
            d["held_out_family"] = held_out_family

        m1_fold_metrics.append(m1_metrics)
        m2_fold_metrics.append(m2_metrics)
        m1_fold_preds.append(y_pred_m1)
        m2_fold_preds.append(y_pred_m2)
        fold_labels.append(held_out_family)

    n_folds = len(m1_fold_metrics)
    m1_agg = _aggregate_cv_metrics(m1_fold_metrics, n_folds)
    m2_agg = _aggregate_cv_metrics(m2_fold_metrics, n_folds)

    fold_rows = []
    for i, fam in enumerate(fold_labels):
        fold_rows.append({
            "fold": fam,
            "model": "M1",
            **m1_fold_metrics[i],
        })
        fold_rows.append({
            "fold": fam,
            "model": "M2",
            **m2_fold_metrics[i],
        })

    return {
        "m1_summary": m1_agg,
        "m2_summary": m2_agg,
        "fold_details": pd.DataFrame(fold_rows),
        "fold_metrics_m1": pd.DataFrame(m1_fold_metrics),
        "fold_metrics_m2": pd.DataFrame(m2_fold_metrics),
    }


def run_5fold_cv(
    df: pd.DataFrame,
    X_m1: pd.DataFrame,
    X_m2: pd.DataFrame,
    y: np.ndarray,
) -> dict:
    splitter = FiveFoldStratifiedSplitter()
    m1_fold_metrics = []
    m2_fold_metrics = []
    m1_fold_preds: list = []
    m2_fold_preds: list = []
    fold_indices: list = []

    for train_idx, test_idx, fold_idx in splitter.split(df):
        y_train, y_test = y[train_idx], y[test_idx]
        y_train_mean = float(np.mean(y_train))
        X_m1_train, X_m1_test = X_m1.iloc[train_idx], X_m1.iloc[test_idx]
        X_m2_train, X_m2_test = X_m2.iloc[train_idx], X_m2.iloc[test_idx]

        model_m1 = fit_fractional_logit(X_m1_train, y_train)
        model_m2 = fit_fractional_logit(X_m2_train, y_train)

        y_pred_m1 = predict_fractional_logit(model_m1, X_m1_test)
        y_pred_m2 = predict_fractional_logit(model_m2, X_m2_test)

        m1_metrics = _compute_cv_metrics(y_test, y_pred_m1, y_train_mean)
        m2_metrics = _compute_cv_metrics(y_test, y_pred_m2, y_train_mean)

        for d in [m1_metrics, m2_metrics]:
            d["fold"] = int(fold_idx)

        m1_fold_metrics.append(m1_metrics)
        m2_fold_metrics.append(m2_metrics)
        m1_fold_preds.append(y_pred_m1)
        m2_fold_preds.append(y_pred_m2)
        fold_indices.append(int(fold_idx))

    n_folds = len(m1_fold_metrics)
    m1_agg = _aggregate_cv_metrics(m1_fold_metrics, n_folds)
    m2_agg = _aggregate_cv_metrics(m2_fold_metrics, n_folds)

    fold_rows = []
    for i, fidx in enumerate(fold_indices):
        fold_rows.append({
            "fold": fidx,
            "model": "M1",
            **m1_fold_metrics[i],
        })
        fold_rows.append({
            "fold": fidx,
            "model": "M2",
            **m2_fold_metrics[i],
        })

    return {
        "m1_summary": m1_agg,
        "m2_summary": m2_agg,
        "fold_details": pd.DataFrame(fold_rows),
        "fold_metrics_m1": pd.DataFrame(m1_fold_metrics),
        "fold_metrics_m2": pd.DataFrame(m2_fold_metrics),
    }


def run_full_sample(
    X_m1: pd.DataFrame,
    X_m2: pd.DataFrame,
    y: np.ndarray,
    instance_id: np.ndarray,
    predictor_names_m1: list,
    predictor_names_m2: list,
) -> dict:
    model_m1 = fit_fractional_logit(X_m1, y)
    model_m2 = fit_fractional_logit(X_m2, y)

    model_m1_cr = cluster_robust_se_flogit(model_m1, instance_id)
    model_m2_cr = cluster_robust_se_flogit(model_m2, instance_id)

    coefs_m1 = flogit_coefficients(model_m1_cr, predictor_names=list(model_m1.params.index))
    coefs_m2 = flogit_coefficients(model_m2_cr, predictor_names=list(model_m2.params.index))

    y_pred_m1 = predict_fractional_logit(model_m1, X_m1)
    y_pred_m2 = predict_fractional_logit(model_m2, X_m2)

    n = len(y)
    pseudo_r2_m1 = pseudo_r_squared_mcfadden(model_m1, y)
    pseudo_r2_m2 = pseudo_r_squared_mcfadden(model_m2, y)

    cohen_f2 = cohens_f2(pseudo_r2_m1, pseudo_r2_m2)

    brier_m1 = brier_score(y, y_pred_m1)
    brier_m2 = brier_score(y, y_pred_m2)
    rmse_m1 = rmse(y, y_pred_m1)
    rmse_m2 = rmse(y, y_pred_m2)
    mae_m1 = mae(y, y_pred_m1)
    mae_m2 = mae(y, y_pred_m2)

    return {
        "model_m1": model_m1,
        "model_m2": model_m2,
        "model_m1_cr": model_m1_cr,
        "model_m2_cr": model_m2_cr,
        "coefs_m1": coefs_m1,
        "coefs_m2": coefs_m2,
        "pseudo_r2_m1": pseudo_r2_m1,
        "pseudo_r2_m2": pseudo_r2_m2,
        "cohen_f2": cohen_f2,
        "y_pred_m1": y_pred_m1,
        "y_pred_m2": y_pred_m2,
        "brier_m1": brier_m1,
        "brier_m2": brier_m2,
        "rmse_m1": rmse_m1,
        "rmse_m2": rmse_m2,
        "mae_m1": mae_m1,
        "mae_m2": mae_m2,
    }


def run_flogit_pipeline(
    df: pd.DataFrame,
    algo: str,
    response: str,
    spec: dict,
    algo_label: str,
) -> dict:
    print(f"\n{'='*60}")
    print(f"Fractional Logit Model: {algo_label} — {response}")
    print(f"  Status: {spec['status']}")

    X_m1, X_m2, y, pred_names_m1, pred_names_m2 = build_feature_matrices(
        df, algo, response, MODEL_SPECS, None
    )
    p_m1 = X_m1.shape[1]
    p_m2 = X_m2.shape[1]
    n_total = len(y)
    print(f"  n={n_total}, p_M1={p_m1}, p_M2={p_m2}")
    print(f"  y range: [{float(y.min()):.6f}, {float(y.max()):.6f}]")

    has_nan = np.isnan(y).sum()
    if has_nan > 0:
        print(f"  WARNING: {has_nan} NaN values in y — dropping")
        valid_mask = ~np.isnan(y)
        y = y[valid_mask]
        X_m1 = X_m1.iloc[valid_mask]
        X_m2 = X_m2.iloc[valid_mask]
        df = df.iloc[valid_mask].copy()

    print(f"  [1/5] LOFO CV...")
    lofo_results = run_lofo_cv(df, X_m1, X_m2, y)
    print(f"    M1 pseudo-R² (mean±SD): {lofo_results['m1_summary']['pseudo_r_squared_mean']:.4f} ± {lofo_results['m1_summary']['pseudo_r_squared_sd']:.4f}")
    print(f"    M2 pseudo-R² (mean±SD): {lofo_results['m2_summary']['pseudo_r_squared_mean']:.4f} ± {lofo_results['m2_summary']['pseudo_r_squared_sd']:.4f}")

    print(f"  [2/5] 5-fold CV...")
    cv5_results = run_5fold_cv(df, X_m1, X_m2, y)
    print(f"    M1 pseudo-R² (mean±SD): {cv5_results['m1_summary']['pseudo_r_squared_mean']:.4f} ± {cv5_results['m1_summary']['pseudo_r_squared_sd']:.4f}")
    print(f"    M2 pseudo-R² (mean±SD): {cv5_results['m2_summary']['pseudo_r_squared_mean']:.4f} ± {cv5_results['m2_summary']['pseudo_r_squared_sd']:.4f}")

    print(f"  [3/5] Full-sample fit...")
    full = run_full_sample(
        X_m1, X_m2, y,
        instance_id=df["instance_id"].values,
        predictor_names_m1=pred_names_m1,
        predictor_names_m2=pred_names_m2,
    )
    print(f"    M1 pseudo-R²={full['pseudo_r2_m1']:.4f}")
    print(f"    M2 pseudo-R²={full['pseudo_r2_m2']:.4f}")
    print(f"    Δpseudo-R²={full['pseudo_r2_m2'] - full['pseudo_r2_m1']:.4f}")
    print(f"    Cohen's f²={full['cohen_f2']:.4f}")
    print(f"    M1 Brier={full['brier_m1']:.6f}, RMSE={full['rmse_m1']:.6f}, MAE={full['mae_m1']:.6f}")
    print(f"    M2 Brier={full['brier_m2']:.6f}, RMSE={full['rmse_m2']:.6f}, MAE={full['mae_m2']:.6f}")

    print(f"  [4/5] Bootstrap Δpseudo-R² CI...")
    delta_pseudo_r2_values, delta_pseudo_r2_ci = bootstrap_delta_pseudo_r2(
        X_m1, X_m2, y,
        family=df["family"].values,
        n_resamples=N_BOOTSTRAP_RESAMPLES,
        rng=RNG,
    )
    print(f"    Δpseudo-R² 95% CI: [{delta_pseudo_r2_ci[0]:.4f}, {delta_pseudo_r2_ci[1]:.4f}]")

    print(f"  [5/5] Standardised β (M2)...")
    std_beta_m2 = standardized_beta_flogit(X_m2, y)

    cr_coefs_m2 = full["coefs_m2"]

    return {
        "algo": algo,
        "algo_label": algo_label,
        "response": response,
        "status": spec["status"],
        "lofo": lofo_results,
        "cv5": cv5_results,
        "full": full,
        "delta_pseudo_r2_ci": delta_pseudo_r2_ci,
        "std_beta_m2": std_beta_m2,
        "cr_coefs_m2": cr_coefs_m2,
        "n": n_total,
        "p_m1": p_m1,
        "p_m2": p_m2,
    }


def save_results(algo_label: str, response: str, results: dict):
    prefix = f"{algo_label}_{response}"

    lofo_summary = {
        "cv_scheme": "LOFO",
        "algorithm": algo_label,
        "response": response,
        "model": "M1",
        **results["lofo"]["m1_summary"],
    }
    lofo_summary_m2 = {
        "cv_scheme": "LOFO",
        "algorithm": algo_label,
        "response": response,
        "model": "M2",
        **results["lofo"]["m2_summary"],
    }
    cv5_summary = {
        "cv_scheme": "5-fold",
        "algorithm": algo_label,
        "response": response,
        "model": "M1",
        **results["cv5"]["m1_summary"],
    }
    cv5_summary_m2 = {
        "cv_scheme": "5-fold",
        "algorithm": algo_label,
        "response": response,
        "model": "M2",
        **results["cv5"]["m2_summary"],
    }
    full_m1 = {
        "cv_scheme": "full_sample",
        "algorithm": algo_label,
        "response": response,
        "model": "M1",
        "pseudo_r_squared": results["full"]["pseudo_r2_m1"],
        "brier_score": results["full"]["brier_m1"],
        "rmse": results["full"]["rmse_m1"],
        "mae": results["full"]["mae_m1"],
    }
    full_m2 = {
        "cv_scheme": "full_sample",
        "algorithm": algo_label,
        "response": response,
        "model": "M2",
        "pseudo_r_squared": results["full"]["pseudo_r2_m2"],
        "brier_score": results["full"]["brier_m2"],
        "rmse": results["full"]["rmse_m2"],
        "mae": results["full"]["mae_m2"],
    }

    metrics_rows = [
        lofo_summary, lofo_summary_m2,
        cv5_summary, cv5_summary_m2,
        full_m1, full_m2,
    ]
    for row in metrics_rows:
        row["n"] = results["n"]
        row["p"] = results["p_m1"] if row["model"] == "M1" else results["p_m2"]

    inference_row = {
        "algorithm": algo_label,
        "response": response,
        "status": results["status"],
        "delta_pseudo_r2": results["full"]["pseudo_r2_m2"] - results["full"]["pseudo_r2_m1"],
        "cohen_f2": results["full"]["cohen_f2"],
        "delta_pseudo_r2_ci_lower": results["delta_pseudo_r2_ci"][0],
        "delta_pseudo_r2_ci_upper": results["delta_pseudo_r2_ci"][1],
    }

    metrics_df = pd.DataFrame(metrics_rows)
    metrics_path = RESULTS_DIR / f"flogit_metrics_{prefix}.csv"
    metrics_df.to_csv(metrics_path, index=False)
    print(f"  Saved metrics: {metrics_path.name}")

    inference_df = pd.DataFrame([inference_row])
    inference_path = RESULTS_DIR / f"flogit_inference_{prefix}.csv"
    inference_df.to_csv(inference_path, index=False)
    print(f"  Saved inference: {inference_path.name}")

    lofo_folds = results["lofo"]["fold_details"]
    lofo_path = CV_DIR / f"lofo_folds_flogit_{prefix}.csv"
    lofo_cols = ["fold", "model", "pseudo_r_squared", "brier_score", "rmse", "mae"]
    lofo_folds[lofo_cols].to_csv(lofo_path, index=False)
    print(f"  Saved LOFO folds: {lofo_path.name}")

    cv5_folds = results["cv5"]["fold_details"]
    cv5_path = CV_DIR / f"cv5_folds_flogit_{prefix}.csv"
    cv5_cols = ["fold", "model", "pseudo_r_squared", "brier_score", "rmse", "mae"]
    cv5_folds[cv5_cols].to_csv(cv5_path, index=False)
    print(f"  Saved 5-fold folds: {cv5_path.name}")

    coefs_m1_path = DIAG_DIR / f"full_sample_coefs_flogit_{prefix}_M1.csv"
    results["full"]["coefs_m1"].to_csv(coefs_m1_path, index=False)
    print(f"  Saved M1 coefficients: {coefs_m1_path.name}")

    coefs_m2_path = DIAG_DIR / f"full_sample_coefs_flogit_{prefix}_M2.csv"
    cr_coefs = results["cr_coefs_m2"]
    cr_coefs.to_csv(coefs_m2_path, index=False)
    print(f"  Saved M2 coefficients (cluster-robust): {coefs_m2_path.name}")

    std_beta_path = DIAG_DIR / f"std_beta_flogit_{prefix}_M2.csv"
    results["std_beta_m2"].to_csv(std_beta_path, index=False)
    print(f"  Saved standardized β (M2): {std_beta_path.name}")

    return metrics_df, inference_df


def main():
    print("=" * 60)
    print("Phase 3.3.3 — Fractional Logit Models")
    print("=" * 60)

    for dir_path in [RESULTS_DIR, CV_DIR, DIAG_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

    flogit_specs = [
        (algo, resp, spec)
        for (algo, resp), spec in MODEL_SPECS.items()
        if spec["family"] == "fractional_logit"
    ]
    print(f"\nFound {len(flogit_specs)} fractional logit model specifications:")
    for algo, resp, spec in flogit_specs:
        label = ALGORITHM_LABEL_MAP[algo]
        print(f"  {label:12s} — {resp:25s} [{spec['status']}]")

    all_metrics = []
    all_inference = []

    for algo, response, spec in flogit_specs:
        algo_label = ALGORITHM_LABEL_MAP[algo]
        prepared_path = PREPARED_DIR / f"{algo_label}.pkl"
        if not prepared_path.exists():
            print(f"\n  ERROR: Prepared data not found: {prepared_path}")
            continue

        df = pd.read_pickle(str(prepared_path))
        if "instance_id" not in df.columns:
            df["instance_id"] = range(len(df))

        results = run_flogit_pipeline(df, algo, response, spec, algo_label)
        metrics_df, inference_df = save_results(algo_label, response, results)
        all_metrics.append(metrics_df)
        all_inference.append(inference_df)

    if all_metrics:
        combined_metrics = pd.concat(all_metrics, ignore_index=True)
        combined_metrics.to_csv(
            RESULTS_DIR / "flogit_metrics_aggregated.csv", index=False
        )
        print(f"\nSaved aggregated metrics: flogit_metrics_aggregated.csv")

    if all_inference:
        combined_inference = pd.concat(all_inference, ignore_index=True)
        combined_inference.to_csv(
            RESULTS_DIR / "flogit_inference_aggregated.csv", index=False
        )
        print(f"Saved aggregated inference: flogit_inference_aggregated.csv")

    print("\n" + "=" * 60)
    print("PHASE 3.3.3 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
