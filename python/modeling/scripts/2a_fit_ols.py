import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

from config import (
    ALGO_BB, ALGO_DP, ALGO_GREEDY,
    ALGORITHM_CANONICAL,
    ALGORITHM_LABEL_MAP,
    MODEL_SPECS,
    N_BOOTSTRAP_RESAMPLES,
    RANDOM_SEED,
)
from utils.models import (
    fit_ols,
    predict_ols,
    ols_coefficients,
    cluster_robust_se,
    incremental_f_test,
    standardized_beta,
    bootstrap_delta_r2,
)
from utils.preprocessing import build_feature_matrices
from utils.cv import LofoFoldSplitter, FiveFoldStratifiedSplitter
from utils.metrics import (
    r_squared,
    adj_r_squared,
    rmse,
    mae,
    cohens_f2,
    duan_smearing,
    backtransformed_rmse,
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
    n_train: int,
    n_params: int,
) -> dict:
    r2 = r_squared(y_true_fold, y_pred_fold)
    r2_adj = adj_r_squared(r2, n=n_train, p=n_params)
    rmse_val = rmse(y_true_fold, y_pred_fold)
    mae_val = mae(y_true_fold, y_pred_fold)
    return {
        "r_squared": r2,
        "adj_r_squared": r2_adj,
        "rmse": rmse_val,
        "mae": mae_val,
    }


def _aggregate_cv_metrics(fold_metrics: list, n_folds: int) -> dict:
    metrics_df = pd.DataFrame(fold_metrics)
    agg = {}
    for col in ["r_squared", "adj_r_squared", "rmse", "mae"]:
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
    p_m1: int,
    p_m2: int,
) -> dict:
    splitter = LofoFoldSplitter()
    m1_fold_metrics = []
    m2_fold_metrics = []
    m1_fold_preds: list = []
    m2_fold_preds: list = []
    fold_labels: list = []

    for train_idx, test_idx, held_out_family in splitter.split(df):
        y_train, y_test = y[train_idx], y[test_idx]
        X_m1_train, X_m1_test = X_m1.iloc[train_idx], X_m1.iloc[test_idx]
        X_m2_train, X_m2_test = X_m2.iloc[train_idx], X_m2.iloc[test_idx]

        model_m1 = fit_ols(X_m1_train, y_train)
        model_m2 = fit_ols(X_m2_train, y_train)

        y_pred_m1 = predict_ols(model_m1, X_m1_test)
        y_pred_m2 = predict_ols(model_m2, X_m2_test)

        n_train = len(train_idx)
        m1_metrics = _compute_cv_metrics(y_test, y_pred_m1, n_train, p_m1)
        m2_metrics = _compute_cv_metrics(y_test, y_pred_m2, n_train, p_m2)

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
            "y_true": y[df["family"].values == fam].tolist(),
            "y_pred": m1_fold_preds[i].tolist(),
            **m1_fold_metrics[i],
        })
        fold_rows.append({
            "fold": fam,
            "model": "M2",
            "y_true": y[df["family"].values == fam].tolist(),
            "y_pred": m2_fold_preds[i].tolist(),
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
    p_m1: int,
    p_m2: int,
) -> dict:
    splitter = FiveFoldStratifiedSplitter()
    m1_fold_metrics = []
    m2_fold_metrics = []
    m1_fold_preds: list = []
    m2_fold_preds: list = []
    fold_indices: list = []

    for train_idx, test_idx, fold_idx in splitter.split(df):
        y_train, y_test = y[train_idx], y[test_idx]
        X_m1_train, X_m1_test = X_m1.iloc[train_idx], X_m1.iloc[test_idx]
        X_m2_train, X_m2_test = X_m2.iloc[train_idx], X_m2.iloc[test_idx]

        model_m1 = fit_ols(X_m1_train, y_train)
        model_m2 = fit_ols(X_m2_train, y_train)

        y_pred_m1 = predict_ols(model_m1, X_m1_test)
        y_pred_m2 = predict_ols(model_m2, X_m2_test)

        n_train = len(train_idx)
        m1_metrics = _compute_cv_metrics(y_test, y_pred_m1, n_train, p_m1)
        m2_metrics = _compute_cv_metrics(y_test, y_pred_m2, n_train, p_m2)

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
    model_m1 = fit_ols(X_m1, y)
    model_m2 = fit_ols(X_m2, y)

    model_m1_cr = cluster_robust_se(model_m1, instance_id)
    model_m2_cr = cluster_robust_se(model_m2, instance_id)

    coefs_m1 = ols_coefficients(model_m1_cr, predictor_names=list(model_m1.params.index))
    coefs_m2 = ols_coefficients(model_m2_cr, predictor_names=list(model_m2.params.index))

    y_pred_m1 = predict_ols(model_m1, X_m1)
    y_pred_m2 = predict_ols(model_m2, X_m2)

    n = len(y)
    r2_m1 = float(model_m1.rsquared)
    r2_m2 = float(model_m2.rsquared)
    r2_adj_m1 = float(model_m1.rsquared_adj)
    r2_adj_m2 = float(model_m2.rsquared_adj)

    f_test = incremental_f_test(
        ssr_reduced=float(model_m1.ssr),
        ssr_full=float(model_m2.ssr),
        df_resid_reduced=int(model_m1.df_resid),
        df_resid_full=int(model_m2.df_resid),
    )

    cohen_f2 = cohens_f2(r2_m1, r2_m2)

    residuals_m1 = (y - y_pred_m1).astype(float)
    residuals_m2 = (y - y_pred_m2).astype(float)

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
        "r2_m1": r2_m1,
        "r2_m2": r2_m2,
        "r2_adj_m1": r2_adj_m1,
        "r2_adj_m2": r2_adj_m2,
        "f_test": f_test,
        "cohen_f2": cohen_f2,
        "residuals_m1": residuals_m1,
        "residuals_m2": residuals_m2,
        "y_pred_m1": y_pred_m1,
        "y_pred_m2": y_pred_m2,
        "rmse_m1": rmse_m1,
        "rmse_m2": rmse_m2,
        "mae_m1": mae_m1,
        "mae_m2": mae_m2,
    }


def run_ols_pipeline(
    df: pd.DataFrame,
    algo: str,
    response: str,
    spec: dict,
    algo_label: str,
) -> dict:
    print(f"\n{'='*60}")
    print(f"OLS Model: {algo_label} — {response}")
    print(f"  Status: {spec['status']}")

    X_m1, X_m2, y, pred_names_m1, pred_names_m2 = build_feature_matrices(
        df, algo, response, MODEL_SPECS, None
    )
    p_m1 = X_m1.shape[1]
    p_m2 = X_m2.shape[1]
    n_total = len(y)
    print(f"  n={n_total}, p_M1={p_m1}, p_M2={p_m2}")

    has_nan = np.isnan(y).sum()
    if has_nan > 0:
        print(f"  WARNING: {has_nan} NaN values in y — dropping")
        valid_mask = ~np.isnan(y)
        y = y[valid_mask]
        X_m1 = X_m1.iloc[valid_mask]
        X_m2 = X_m2.iloc[valid_mask]
        df = df.iloc[valid_mask].copy()

    print(f"  [1/5] LOFO CV...")
    lofo_results = run_lofo_cv(df, X_m1, X_m2, y, p_m1, p_m2)
    print(f"    M1 R² (mean±SD): {lofo_results['m1_summary']['r_squared_mean']:.4f} ± {lofo_results['m1_summary']['r_squared_sd']:.4f}")
    print(f"    M2 R² (mean±SD): {lofo_results['m2_summary']['r_squared_mean']:.4f} ± {lofo_results['m2_summary']['r_squared_sd']:.4f}")

    print(f"  [2/5] 5-fold CV...")
    cv5_results = run_5fold_cv(df, X_m1, X_m2, y, p_m1, p_m2)
    print(f"    M1 R² (mean±SD): {cv5_results['m1_summary']['r_squared_mean']:.4f} ± {cv5_results['m1_summary']['r_squared_sd']:.4f}")
    print(f"    M2 R² (mean±SD): {cv5_results['m2_summary']['r_squared_mean']:.4f} ± {cv5_results['m2_summary']['r_squared_sd']:.4f}")

    print(f"  [3/5] Full-sample fit...")
    full = run_full_sample(
        X_m1, X_m2, y,
        instance_id=df["instance_id"].values,
        predictor_names_m1=pred_names_m1,
        predictor_names_m2=pred_names_m2,
    )
    print(f"    M1 R²={full['r2_m1']:.4f}, R²_adj={full['r2_adj_m1']:.4f}")
    print(f"    M2 R²={full['r2_m2']:.4f}, R²_adj={full['r2_adj_m2']:.4f}")
    print(f"    ΔR²_adj={full['r2_adj_m2'] - full['r2_adj_m1']:.4f}")
    print(f"    F({full['f_test']['delta_df']}, {int(full['model_m2'].df_resid)})={full['f_test']['f_stat']:.4f}, p={full['f_test']['p_value']:.6f}")
    print(f"    Cohen's f²={full['cohen_f2']:.4f}")

    print(f"  [4/5] Bootstrap ΔR² CI...")
    delta_r2_values, delta_r2_ci = bootstrap_delta_r2(
        X_m1, X_m2, y,
        family=df["family"].values,
        n_resamples=N_BOOTSTRAP_RESAMPLES,
        rng=RNG,
    )
    print(f"    ΔR² 95% CI: [{delta_r2_ci[0]:.4f}, {delta_r2_ci[1]:.4f}]")

    print(f"  [5/5] Back-transformed RMSE...")
    family_labels = df["family"].values
    smearing_m1 = duan_smearing(full["residuals_m1"], family_labels)
    smearing_m2 = duan_smearing(full["residuals_m2"], family_labels)
    smearing_pooled_m1 = smearing_m1.get("pooled", 1.0)
    smearing_pooled_m2 = smearing_m2.get("pooled", 1.0)

    bt_rmse_m1 = backtransformed_rmse(y, full["y_pred_m1"], smearing_pooled_m1)
    bt_rmse_m2 = backtransformed_rmse(y, full["y_pred_m2"], smearing_pooled_m2)
    print(f"    M1 smearing φ={smearing_pooled_m1:.4f}, back-RMSE={bt_rmse_m1:.4f}")
    print(f"    M2 smearing φ={smearing_pooled_m2:.4f}, back-RMSE={bt_rmse_m2:.4f}")

    print(f"  Standardised β (M2)...")
    std_beta_m2 = standardized_beta(X_m2, y)

    cr_coefs_m2 = full["coefs_m2"]

    return {
        "algo": algo,
        "algo_label": algo_label,
        "response": response,
        "status": spec["status"],
        "lofo": lofo_results,
        "cv5": cv5_results,
        "full": full,
        "delta_r2_ci": delta_r2_ci,
        "smearing_m1": smearing_m1,
        "smearing_m2": smearing_m2,
        "bt_rmse_m1": bt_rmse_m1,
        "bt_rmse_m2": bt_rmse_m2,
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
        "r_squared": results["full"]["r2_m1"],
        "adj_r_squared": results["full"]["r2_adj_m1"],
        "rmse": results["full"]["rmse_m1"],
        "mae": results["full"]["mae_m1"],
    }
    full_m2 = {
        "cv_scheme": "full_sample",
        "algorithm": algo_label,
        "response": response,
        "model": "M2",
        "r_squared": results["full"]["r2_m2"],
        "adj_r_squared": results["full"]["r2_adj_m2"],
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

    ft = results["full"]["f_test"]
    inference_row = {
        "algorithm": algo_label,
        "response": response,
        "status": results["status"],
        "delta_r2_adj": results["full"]["r2_adj_m2"] - results["full"]["r2_adj_m1"],
        "f_stat": ft["f_stat"],
        "f_p_value": ft["p_value"],
        "delta_df": ft["delta_df"],
        "cohen_f2": results["full"]["cohen_f2"],
        "delta_r2_ci_lower": results["delta_r2_ci"][0],
        "delta_r2_ci_upper": results["delta_r2_ci"][1],
        "bt_rmse_m1": results["bt_rmse_m1"],
        "bt_rmse_m2": results["bt_rmse_m2"],
        "smearing_phi_m1_pooled": results["smearing_m1"].get("pooled", float("nan")),
        "smearing_phi_m2_pooled": results["smearing_m2"].get("pooled", float("nan")),
    }

    metrics_df = pd.DataFrame(metrics_rows)
    metrics_path = RESULTS_DIR / f"ols_metrics_{prefix}.csv"
    metrics_df.to_csv(metrics_path, index=False)
    print(f"  Saved metrics: {metrics_path.name}")

    inference_df = pd.DataFrame([inference_row])
    inference_path = RESULTS_DIR / f"ols_inference_{prefix}.csv"
    inference_df.to_csv(inference_path, index=False)
    print(f"  Saved inference: {inference_path.name}")

    lofo_folds = results["lofo"]["fold_details"]
    lofo_path = CV_DIR / f"lofo_folds_{prefix}.csv"
    lofo_cols = ["fold", "model", "r_squared", "adj_r_squared", "rmse", "mae"]
    lofo_folds[lofo_cols].to_csv(lofo_path, index=False)
    print(f"  Saved LOFO folds: {lofo_path.name}")

    cv5_folds = results["cv5"]["fold_details"]
    cv5_path = CV_DIR / f"cv5_folds_{prefix}.csv"
    cv5_cols = ["fold", "model", "r_squared", "adj_r_squared", "rmse", "mae"]
    cv5_folds[cv5_cols].to_csv(cv5_path, index=False)
    print(f"  Saved 5-fold folds: {cv5_path.name}")

    coefs_m1_path = DIAG_DIR / f"full_sample_coefs_{prefix}_M1.csv"
    results["full"]["coefs_m1"].to_csv(coefs_m1_path, index=False)
    print(f"  Saved M1 coefficients: {coefs_m1_path.name}")

    coefs_m2_path = DIAG_DIR / f"full_sample_coefs_{prefix}_M2.csv"
    cr_coefs = results["cr_coefs_m2"]
    cr_coefs.to_csv(coefs_m2_path, index=False)
    print(f"  Saved M2 coefficients (cluster-robust): {coefs_m2_path.name}")

    std_beta_path = DIAG_DIR / f"std_beta_{prefix}_M2.csv"
    results["std_beta_m2"].to_csv(std_beta_path, index=False)
    print(f"  Saved standardized β (M2): {std_beta_path.name}")

    return metrics_df, inference_df


def main():
    print("=" * 60)
    print("Phase 3.3.2 — OLS Models (5 Continuous Responses)")
    print("=" * 60)

    for dir_path in [RESULTS_DIR, CV_DIR, DIAG_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

    ols_specs = [
        (algo, resp, spec)
        for (algo, resp), spec in MODEL_SPECS.items()
        if spec["family"] == "ols"
    ]
    print(f"\nFound {len(ols_specs)} OLS model specifications:")
    for algo, resp, spec in ols_specs:
        label = ALGORITHM_LABEL_MAP[algo]
        print(f"  {label:12s} — {resp:25s} [{spec['status']}]")

    all_metrics = []
    all_inference = []

    for algo, response, spec in ols_specs:
        algo_label = ALGORITHM_LABEL_MAP[algo]
        prepared_path = PREPARED_DIR / f"{algo_label}.pkl"
        if not prepared_path.exists():
            print(f"\n  ERROR: Prepared data not found: {prepared_path}")
            continue

        df = pd.read_pickle(str(prepared_path))
        if "instance_id" not in df.columns:
            df["instance_id"] = range(len(df))

        results = run_ols_pipeline(df, algo, response, spec, algo_label)
        metrics_df, inference_df = save_results(algo_label, response, results)
        all_metrics.append(metrics_df)
        all_inference.append(inference_df)

    if all_metrics:
        combined_metrics = pd.concat(all_metrics, ignore_index=True)
        combined_metrics.to_csv(
            RESULTS_DIR / "ols_metrics_aggregated.csv", index=False
        )
        print(f"\nSaved aggregated metrics: ols_metrics_aggregated.csv")

    if all_inference:
        combined_inference = pd.concat(all_inference, ignore_index=True)
        combined_inference.to_csv(
            RESULTS_DIR / "ols_inference_aggregated.csv", index=False
        )
        print(f"Saved aggregated inference: ols_inference_aggregated.csv")

    print("\n" + "=" * 60)
    print("PHASE 3.3.2 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
