import gc
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message="unknown kwargs")
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss, accuracy_score, mean_squared_error, mean_absolute_error

from config import RANDOM_SEED, MODEL_SPECS, ALGORITHM_LABEL_MAP, ALGO_BB
from utils.models import fit_hurdle, predict_hurdle
from utils.preprocessing import build_feature_matrices
from utils.cv import LofoFoldSplitter

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PREPARED_DIR = OUTPUT_DIR / "prepared"
RESULTS_DIR = OUTPUT_DIR / "results"
CV_DIR = OUTPUT_DIR / "cross_validation"

for d in [RESULTS_DIR, CV_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def _compute_hurdle_metrics(y_true, y_pred, y_bin_true, p_pos):
    y_bin_pred = (p_pos >= 0.5).astype(int)
    metrics = {}
    
    # Part 1: classification metrics for zero vs positive
    metrics["brier_score"] = brier_score_loss(y_bin_true, p_pos)
    metrics["accuracy"] = accuracy_score(y_bin_true, y_bin_pred)
    if len(np.unique(y_bin_true)) > 1:
        metrics["auc_roc"] = roc_auc_score(y_bin_true, p_pos)
    else:
        metrics["auc_roc"] = float('nan')
        
    # Combined prediction metrics
    metrics["rmse"] = np.sqrt(mean_squared_error(y_true, y_pred))
    metrics["mae"] = mean_absolute_error(y_true, y_pred)
    
    return metrics


def main():
    print("=" * 60)
    print("Phase 3.3.4 — Hurdle Model (Solution Gap)")
    print("=" * 60)
    
    algo = ALGO_BB
    algo_label = ALGORITHM_LABEL_MAP[algo]
    response = "solution_gap"
    
    prepared_path = PREPARED_DIR / f"{algo_label}.pkl"
    if not prepared_path.exists():
        print(f"ERROR: Prepared data not found: {prepared_path}")
        return
        
    df = pd.read_pickle(str(prepared_path))
    if "instance_id" not in df.columns:
        df["instance_id"] = range(len(df))
        
    y = df[response].values
    
    X_m1, X_m2, _, _, _ = build_feature_matrices(df, algo, response, MODEL_SPECS, None)
    
    print(f"  Total samples: {len(y)}")
    print(f"  Positive gap samples: {(y > 0).sum()}")
    print(f"  M1 predictors: {X_m1.shape[1]}")
    print(f"  M2 predictors: {X_m2.shape[1]}")
    print(f"  M2 EPV: {(y > 0).sum()} / {X_m2.shape[1]} = {(y > 0).sum() / X_m2.shape[1]:.2f}")
    
    splitter = LofoFoldSplitter()
    
    fold_metrics = []
    
    for idx, (train_idx, test_idx, held_out_family) in enumerate(splitter.split(df)):
        print(f"  Fitting LOFO Fold: {held_out_family}...")
        y_train, y_test = y[train_idx], y[test_idx]
        y_bin_test = (y_test > 0).astype(int)
        
        X_m1_train, X_m1_test = X_m1.iloc[train_idx], X_m1.iloc[test_idx]
        X_m2_train, X_m2_test = X_m2.iloc[train_idx], X_m2.iloc[test_idx]
        
        # Fit M1
        model_m1 = fit_hurdle(X_m1_train, y_train)
        y_pred_m1 = predict_hurdle(model_m1, X_m1_test)
        p_pos_m1 = model_m1['part1'].predict_proba(X_m1_test.astype(float))[:, 1]
        
        m1_metrics = _compute_hurdle_metrics(y_test, y_pred_m1, y_bin_test, p_pos_m1)
        m1_metrics["fold"] = held_out_family
        m1_metrics["model"] = "M1"
        fold_metrics.append(m1_metrics)
        
        # Fit M2
        model_m2 = fit_hurdle(X_m2_train, y_train)
        y_pred_m2 = predict_hurdle(model_m2, X_m2_test)
        p_pos_m2 = model_m2['part1'].predict_proba(X_m2_test.astype(float))[:, 1]
        
        m2_metrics = _compute_hurdle_metrics(y_test, y_pred_m2, y_bin_test, p_pos_m2)
        m2_metrics["fold"] = held_out_family
        m2_metrics["model"] = "M2"
        fold_metrics.append(m2_metrics)
        
    lofo_df = pd.DataFrame(fold_metrics)
    lofo_path = CV_DIR / "lofo_folds_hurdle.csv"
    lofo_df.to_csv(lofo_path, index=False)
    print(f"\n  Saved LOFO metrics: {lofo_path.name}")
    
    # Save full sample metrics (simple average over folds for output)
    agg_df = lofo_df.groupby("model").mean(numeric_only=True).reset_index()
    agg_path = RESULTS_DIR / "hurdle_metrics.csv"
    agg_df.to_csv(agg_path, index=False)
    print(f"  Saved aggregated hurdle metrics: {agg_path.name}")
    
    print("\n" + "=" * 60)
    print("PHASE 3.3.4 (Hurdle) COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
