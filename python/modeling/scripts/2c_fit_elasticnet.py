import gc
import sys
import warnings
from pathlib import Path
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", message="unknown kwargs")
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss, accuracy_score, precision_score, recall_score, f1_score

from config import RANDOM_SEED, MODEL_SPECS, ALGORITHM_LABEL_MAP, ALGO_BB
from utils.models import fit_elasticnet, predict_elasticnet, elasticnet_lambda_path
from utils.preprocessing import build_feature_matrices
from utils.cv import LofoFoldSplitter

RNG = np.random.default_rng(RANDOM_SEED)
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PREPARED_DIR = OUTPUT_DIR / "prepared"
RESULTS_DIR = OUTPUT_DIR / "results"
CV_DIR = OUTPUT_DIR / "cross_validation"
DIAG_DIR = OUTPUT_DIR / "diagnostics"
FIG_DIR = OUTPUT_DIR / "figures"

for d in [RESULTS_DIR, CV_DIR, DIAG_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def _compute_classification_metrics(y_true, y_pred_prob):
    y_pred = (y_pred_prob >= 0.5).astype(int)
    metrics = {
        "brier_score": brier_score_loss(y_true, y_pred_prob),
        "accuracy": accuracy_score(y_true, y_pred),
    }
    
    if len(np.unique(y_true)) > 1:
        metrics["auc_roc"] = roc_auc_score(y_true, y_pred_prob)
        metrics["precision"] = precision_score(y_true, y_pred, zero_division=0)
        metrics["recall"] = recall_score(y_true, y_pred, zero_division=0)
        metrics["f1"] = f1_score(y_true, y_pred, zero_division=0)
    else:
        metrics["auc_roc"] = float('nan')
        metrics["precision"] = float('nan')
        metrics["recall"] = float('nan')
        metrics["f1"] = float('nan')
        
    return metrics


def plot_lambda_path(Cs, mean_deviance, se_deviance, fold_name):
    plt.figure(figsize=(8, 6))
    log_lambdas = -np.log10(Cs) # Since C = 1/lambda
    
    plt.plot(log_lambdas, mean_deviance, 'b-', label='Mean Deviance')
    plt.fill_between(log_lambdas, mean_deviance - se_deviance, mean_deviance + se_deviance, color='b', alpha=0.2)
    
    min_idx = np.argmin(mean_deviance)
    threshold = mean_deviance[min_idx] + se_deviance[min_idx]
    
    plt.axvline(log_lambdas[min_idx], color='r', linestyle='--', label='Min Deviance')
    
    valid_indices = np.where(mean_deviance <= threshold)[0]
    best_c_idx = valid_indices[np.argmin(Cs[valid_indices])]
    
    plt.axvline(log_lambdas[best_c_idx], color='g', linestyle='--', label='1-SE Rule Selected')
    plt.axhline(threshold, color='k', linestyle=':', label='1-SE Threshold')
    
    plt.xlabel('-log10(C) [propto log10(lambda)]')
    plt.ylabel('Deviance')
    plt.title(f'Elastic-Net CV Deviance Path (Fold: {fold_name})')
    plt.legend()
    
    path = FIG_DIR / f"lambda_path_fold_{fold_name}.png"
    plt.savefig(path, bbox_inches='tight')
    plt.close()


def plot_coefficient_trace(model, X_cols):
    cv_model = model.cv_model_
    Cs = cv_model.Cs_
    # coefs_paths_ is dict: {class: ndarray of shape (n_folds, n_Cs, n_features)}
    class_label = list(cv_model.coefs_paths_.keys())[0]
    coefs_paths = cv_model.coefs_paths_[class_label]
    
    mean_coefs = coefs_paths.mean(axis=0) # shape (n_Cs, n_features)
    
    plt.figure(figsize=(10, 8))
    log_lambdas = -np.log10(Cs)
    
    for i in range(mean_coefs.shape[1]):
        plt.plot(log_lambdas, mean_coefs[:, i])
        
    plt.axvline(-np.log10(model.best_c_), color='k', linestyle='--', label='Selected C (1-SE Rule)')
    plt.xlabel('-log10(C)')
    plt.ylabel('Coefficient Value')
    plt.title('Coefficient Trace Plot')
    plt.legend(['Selected C'])
    
    path = FIG_DIR / "coefficient_trace.png"
    plt.savefig(path, bbox_inches='tight')
    plt.close()


def main():
    print("=" * 60)
    print("Phase 3.3.4 — Elastic-Net Logistic Regression")
    print("=" * 60)
    
    algo = ALGO_BB
    algo_label = ALGORITHM_LABEL_MAP[algo]
    response = "optimal"
    
    prepared_path = PREPARED_DIR / f"{algo_label}.pkl"
    if not prepared_path.exists():
        print(f"ERROR: Prepared data not found: {prepared_path}")
        return
        
    df = pd.read_pickle(str(prepared_path))
    if "instance_id" not in df.columns:
        df["instance_id"] = range(len(df))
        
    # Invert 'optimal' so that events = False (did not complete)
    # Actually the design models `optimal=False` as the event for B&B
    # Check if 'optimal' is boolean
    if df[response].dtype == bool:
        y = (~df[response]).astype(int).values
    else:
        y = (df[response] == 0).astype(int).values # assuming 0 is false
        
    spec = MODEL_SPECS.get((algo, "optimal"), {"status": "Exploratory"})
    
    X_m1, X_m2, _, _, _ = build_feature_matrices(df, algo, response, MODEL_SPECS, None)
    
    splitter = LofoFoldSplitter()
    
    fold_metrics = []
    zero_event_families = []
    
    for idx, (train_idx, test_idx, held_out_family) in enumerate(splitter.split(df)):
        print(f"  Fitting LOFO Fold: {held_out_family}...")
        y_train, y_test = y[train_idx], y[test_idx]
        X_m2_train, X_m2_test = X_m2.iloc[train_idx], X_m2.iloc[test_idx]
        
        if len(np.unique(y_test)) == 1:
            zero_event_families.append(held_out_family)
            print(f"    WARNING: Zero events in held-out family {held_out_family}")
            
        model = fit_elasticnet(X_m2_train, y_train, alpha=0.5, cv_folds=5)
        Cs, mean_dev, se_dev = elasticnet_lambda_path(model)
        plot_lambda_path(Cs, mean_dev, se_dev, held_out_family)
        
        y_pred_prob = predict_elasticnet(model, X_m2_test)
        metrics = _compute_classification_metrics(y_test, y_pred_prob)
        metrics["fold"] = held_out_family
        metrics["best_c"] = model.best_c_
        fold_metrics.append(metrics)
        
    lofo_df = pd.DataFrame(fold_metrics)
    lofo_path = CV_DIR / "lofo_folds_elasticnet.csv"
    lofo_df.to_csv(lofo_path, index=False)
    print(f"\n  Saved LOFO metrics: {lofo_path.name}")
    
    zero_event_path = DIAG_DIR / "zero_event_families.txt"
    with open(zero_event_path, "w") as f:
        f.write("\n".join(zero_event_families))
    print(f"  Saved zero event families list: {zero_event_path.name}")
    
    print("\n  Fitting Full-Sample Model...")
    full_model = fit_elasticnet(X_m2, y, alpha=0.5, cv_folds=5)
    plot_coefficient_trace(full_model, X_m2.columns)
    
    # Extract nonzero coefficients
    coefs = full_model.coef_[0]
    nonzero_idx = np.where(coefs != 0)[0]
    nonzero_coefs = coefs[nonzero_idx]
    nonzero_names = X_m2.columns[nonzero_idx]
    
    coef_df = pd.DataFrame({
        "predictor": nonzero_names,
        "coefficient": nonzero_coefs,
        "abs_coefficient": np.abs(nonzero_coefs)
    }).sort_values("abs_coefficient", ascending=False)
    
    coef_path = RESULTS_DIR / "elasticnet_metrics.csv"
    coef_df.to_csv(coef_path, index=False)
    print(f"  Saved nonzero coefficients: {coef_path.name}")
    
    print("\n" + "=" * 60)
    print("PHASE 3.3.4 (Elastic-Net) COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
