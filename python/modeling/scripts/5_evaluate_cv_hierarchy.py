"""
scripts/5_evaluate_cv_hierarchy.py

Consolidates out-of-sample Delta R^2_test for M1 -> M2a -> M2b at every holdout level.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

from config import (
    ALGO_BB, ALGO_GREEDY, ALGO_DP, MODEL_SPECS, M2_PREDICTOR_LABELS,
    GROUP_A_INSTANCE_CHARACTERISTICS, RANDOM_SEED
)
from utils.cv import (
    FiveFoldStratifiedSplitter, ConfigHoldoutSplitter,
    SizeExtrapolationSplitter, CapacityExtrapolationSplitter, LofoFoldSplitter
)
from utils.models import (
    fit_ols, predict_ols,
    fit_fractional_logit, predict_fractional_logit,
    fit_elasticnet, predict_elasticnet,
    fit_hurdle, predict_hurdle
)
from utils.preprocessing import build_feature_matrices

RNG = np.random.default_rng(RANDOM_SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
PREPARED_DIR = BASE_DIR / "output" / "prepared"
OUTPUT_DIR = BASE_DIR.parent.parent / "results" / "revision-2" / "cv-hierarchy"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _get_model_funcs(spec_family):
    if spec_family == "ols":
        return fit_ols, predict_ols
    elif spec_family == "fractional_logit":
        return fit_fractional_logit, predict_fractional_logit
    elif spec_family == "elasticnet":
        return fit_elasticnet, predict_elasticnet
    elif spec_family == "hurdle":
        return fit_hurdle, predict_hurdle
    else:
        raise ValueError(f"Unknown family {spec_family}")


def compute_r2(y_true, y_pred, family):
    if family in ["ols", "elasticnet"]:
        return r2_score(y_true, y_pred)
    elif family == "fractional_logit":
        # pseudo-R2 (squared pearson corr)
        if np.std(y_pred) == 0:
            return 0.0
        return np.corrcoef(y_true, y_pred)[0, 1] ** 2
    elif family == "hurdle":
        # hurdle prediction is already continuous expected value
        return r2_score(y_true, y_pred)
    return 0.0


def evaluate_level(level_name, splitter, df, X_m1, X_m2a, X_m2b, y, family, lofo_mode=None):
    r2_m1_list, r2_m2a_list, r2_m2b_list = [], [], []
    fitter, predictor = _get_model_funcs(family)

    for train_idx, test_idx, fold_id in splitter.split(df):
        if len(train_idx) == 0 or len(test_idx) == 0:
            continue
            
        X_m1_train, y_train = X_m1.iloc[train_idx].copy(), y[train_idx]
        X_m1_test, y_test = X_m1.iloc[test_idx].copy(), y[test_idx]

        X_m2a_train = X_m2a.iloc[train_idx].copy()
        X_m2a_test = X_m2a.iloc[test_idx].copy()
        
        X_m2b_train = X_m2b.iloc[train_idx].copy()
        X_m2b_test = X_m2b.iloc[test_idx].copy()

        # Handle LOFO-A (drop families)
        if lofo_mode == "LOFO-A":
            fam_cols = [c for c in X_m1.columns if c.startswith("family_")]
            X_m1_train.drop(columns=fam_cols, inplace=True, errors="ignore")
            X_m1_test.drop(columns=fam_cols, inplace=True, errors="ignore")
            X_m2a_train.drop(columns=fam_cols, inplace=True, errors="ignore")
            X_m2a_test.drop(columns=fam_cols, inplace=True, errors="ignore")
            X_m2b_train.drop(columns=fam_cols, inplace=True, errors="ignore")
            X_m2b_test.drop(columns=fam_cols, inplace=True, errors="ignore")

        # Fit M1
        try:
            m1_model = fitter(X_m1_train, y_train)
            pred_m1 = predictor(m1_model, X_m1_test)
            r2_m1_list.append(compute_r2(y_test, pred_m1, family))
        except Exception as e:
            r2_m1_list.append(0.0)

        # Fit M2a
        if X_m2a is not None and not X_m2a.empty:
            try:
                m2a_model = fitter(pd.concat([X_m1_train, X_m2a_train], axis=1), y_train)
                pred_m2a = predictor(m2a_model, pd.concat([X_m1_test, X_m2a_test], axis=1))
                r2_m2a_list.append(compute_r2(y_test, pred_m2a, family))
            except Exception as e:
                r2_m2a_list.append(0.0)
        else:
            r2_m2a_list.append(0.0)

        # Fit M2b
        if X_m2b is not None and not X_m2b.empty:
            try:
                m2b_model = fitter(pd.concat([X_m1_train, X_m2b_train], axis=1), y_train)
                pred_m2b = predictor(m2b_model, pd.concat([X_m1_test, X_m2b_test], axis=1))
                r2_m2b_list.append(compute_r2(y_test, pred_m2b, family))
            except Exception as e:
                import traceback
                traceback.print_exc()
                r2_m2b_list.append(0.0)
        else:
            r2_m2b_list.append(0.0)

    r2_m1 = np.mean(r2_m1_list) if r2_m1_list else 0.0
    r2_m2a = np.mean(r2_m2a_list) if r2_m2a_list else 0.0
    r2_m2b = np.mean(r2_m2b_list) if r2_m2b_list else 0.0

    return {
        "Level": level_name,
        "R2_M1_test": r2_m1,
        "R2_M2a_test": r2_m2a,
        "R2_M2b_test": r2_m2b,
        "Delta_R2_M1_M2a": r2_m2a - r2_m1,
        "Delta_R2_M2a_M2b": r2_m2b - r2_m2a,
        "Delta_R2_M1_M2b": r2_m2b - r2_m1,
    }

def main():
    print("=" * 60)
    print("Evaluating CV Hierarchy: M1 -> M2a -> M2b")
    print("=" * 60)

    # 1. Load data
    bb_path = PREPARED_DIR / "BandB.pkl"
    if not bb_path.exists():
        print(f"ERROR: {bb_path} not found. Run 1_prepare_data.py first.")
        return
        
    df_bb = pd.read_pickle(str(bb_path))
    
    # Load BB snapshots (M2a will be 5% fraction)
    snap_path = BASE_DIR.parent.parent / "data" / "instrumentation" / "bb_snapshots.csv"
    if snap_path.exists():
        snapshots = pd.read_csv(snap_path)
        m2a_df = snapshots[snapshots["snapshot_fraction"] == 0.05].copy()
        
        # Drop histogram columns before merging
        hist_cols = ["depth_histogram", "queue_histogram", "improvement_depths", "improvement_nodes"]
        m2a_df = m2a_df.drop(columns=[c for c in hist_cols if c in m2a_df.columns])
        
        # Keep only columns that survived 1_prepare_data.py
        valid_cols = [c for c in m2a_df.columns if c in df_bb.columns or c == "instance_id"]
        m2a_df = m2a_df[valid_cols].copy()
        
        # Apply preprocessing matching 1_prepare_data.py (log transform, arctanh transform)
        # We simulate the most critical log transforms here for M2a
        for col in m2a_df.columns:
            if m2a_df[col].dtype in [np.float64, np.int64] and col not in ["snapshot_fraction", "instance_id", "n", "capacity", "seed"]:
                # simple log transform approximation for the snapshots
                m2a_df[col] = np.log1p(m2a_df[col])
        
        # Merge on instance_id
        df_bb = df_bb.merge(m2a_df, on="instance_id", how="left", suffixes=("", "_m2a"))
    else:
        print(f"Warning: {snap_path} not found. M2a will be empty.")

    results = []

    # Focus on Branch and Bound
    algo = ALGO_BB
    for response in ["log_time_millis", "log_nodes_explored"]:
        spec = MODEL_SPECS[(algo, response)]
        family = spec["family"]
        m2_label = spec["m2_predictor_label"]
        m2_cols = M2_PREDICTOR_LABELS[m2_label]
        
        X_m1, X_m2b, y, _, _ = build_feature_matrices(df_bb, algo, response, MODEL_SPECS, None)
        
        # Build X_m2a (early execution features)
        m2a_cols_present = [c + "_m2a" for c in m2_cols if c + "_m2a" in df_bb.columns]
        if m2a_cols_present:
            X_m2a = df_bb[m2a_cols_present].fillna(0).copy()
        else:
            X_m2a = pd.DataFrame()
            
        print(f"\nEvaluating {algo} -> {response} ({family})")
        
        levels = [
            ("L1: 5-Fold Stratified", FiveFoldStratifiedSplitter(), None),
            ("L2: Config Holdout", ConfigHoldoutSplitter(), None),
            ("L3: Size Extrapolation", SizeExtrapolationSplitter(), None),
            ("L4: Capacity Extrapolation", CapacityExtrapolationSplitter(), None),
            ("L5: LOFO-B (Keep Family)", LofoFoldSplitter(), "LOFO-B"),
            ("L5: LOFO-A (Drop Family)", LofoFoldSplitter(), "LOFO-A"),
        ]

        for lvl_name, splitter, lofo_mode in levels:
            res = evaluate_level(lvl_name, splitter, df_bb, X_m1, X_m2a, X_m2b, y, family, lofo_mode)
            res["Algorithm"] = algo
            res["Target"] = response
            results.append(res)
            print(f"  {lvl_name}: M1={res['R2_M1_test']:.3f}, M2a={res['R2_M2a_test']:.3f}, M2b={res['R2_M2b_test']:.3f}")
            
    df_results = pd.DataFrame(results)
    
    # Reorder columns
    cols = ["Level", "Algorithm", "Target", "R2_M1_test", "R2_M2a_test", "R2_M2b_test", "Delta_R2_M1_M2a", "Delta_R2_M2a_M2b", "Delta_R2_M1_M2b"]
    df_results = df_results[cols]
    
    out_path = OUTPUT_DIR / "delta_r2_cv_hierarchy.csv"
    df_results.to_csv(out_path, index=False)
    print(f"\nSaved consolidated table to {out_path}")

if __name__ == "__main__":
    main()
