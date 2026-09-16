"""
scripts/3b_shape_features.py

Runs M3 shape feature selection inside CV loops to prevent data leakage.
Source: Phase 3.3 Implementation Plan, Task 7.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import r2_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    ALGO_BB, MODEL_SPECS, M2_PREDICTOR_LABELS
)
from utils.cv import LofoFoldSplitter
from utils.preprocessing import build_feature_matrices

BASE_DIR = Path(__file__).resolve().parent.parent
PREPARED_DIR = BASE_DIR / "output" / "prepared"
RESULTS_DIR = BASE_DIR.parent.parent / "results" / "revision-2"
OUTPUT_DIR = RESULTS_DIR / "importance"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_vif(X):
    X_const = sm.add_constant(X)
    vif_data = pd.DataFrame()
    vif_data['feature'] = X_const.columns
    # Handle collinearity/singular matrix
    try:
        vifs = [variance_inflation_factor(X_const.values, i) for i in range(X_const.shape[1])]
    except Exception:
        vifs = [float('inf')] * X_const.shape[1]
    vif_data['VIF'] = vifs
    return vif_data


def select_features_vif(X_shape, drop_priority, threshold=10.0):
    X_shape_std = (X_shape - X_shape.mean()) / (X_shape.std() + 1e-9)
    trimmed_features = list(X_shape.columns)
    
    while True:
        vif_data = compute_vif(X_shape_std[trimmed_features])
        vif_ex_const = vif_data[vif_data['feature'] != 'const']
        
        if vif_ex_const.empty:
            break
            
        max_vif = vif_ex_const['VIF'].max()
        if max_vif <= threshold:
            break
            
        problem_features = vif_ex_const[vif_ex_const['VIF'] > threshold]['feature'].tolist()
        
        to_drop = None
        for p in drop_priority:
            if p in problem_features:
                to_drop = p
                break
                
        # If no priority feature has VIF > threshold, drop the one with max VIF
        if to_drop is None:
            to_drop = vif_ex_const.loc[vif_ex_const['VIF'].idxmax(), 'feature']
            
        trimmed_features.remove(to_drop)
        if len(trimmed_features) == 0:
            break
            
    # Always drop depth_p90 if it somehow survived (per validate_m3.py user request)
    if 'depth_p90' in trimmed_features:
        trimmed_features.remove('depth_p90')
        
    return trimmed_features


def main():
    print("=" * 60)
    print("M3 Shape Feature Selection Inside CV (LOFO-B)")
    print("=" * 60)

    bb_path = PREPARED_DIR / "BandB.pkl"
    if not bb_path.exists():
        print(f"ERROR: {bb_path} not found.")
        return
        
    df_bb = pd.read_pickle(str(bb_path))
    
    # Load shape features
    shapes_path = BASE_DIR.parent.parent / "data" / "instrumentation" / "shape_features.csv"
    if not shapes_path.exists():
        print(f"ERROR: {shapes_path} not found.")
        return
        
    shapes = pd.read_csv(shapes_path)
    df = df_bb.merge(shapes, on="instance_id", how="inner")
    
    shape_features = ['depth_p10', 'depth_p50', 'depth_p90', 'depth_entropy', 'depth_skew', 'queue_entropy']
    for col in shape_features:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    algo = ALGO_BB
    response = "log_nodes_explored"
    
    spec = MODEL_SPECS[(algo, response)]
    
    X_m1, X_m2, y, _, _ = build_feature_matrices(df, algo, response, MODEL_SPECS, None)
    X_shape = df[shape_features].copy()
    
    splitter = LofoFoldSplitter()
    
    drop_priority = ['depth_p50', 'depth_p90', 'depth_p10', 'depth_skew', 'depth_entropy', 'queue_entropy']
    
    results = []
    
    for train_idx, test_idx, fold_id in splitter.split(df):
        if len(train_idx) == 0 or len(test_idx) == 0:
            continue
            
        print(f"\nProcessing Fold: {fold_id}")
            
        X2_train, X2_test = X_m2.iloc[train_idx].copy(), X_m2.iloc[test_idx].copy()
        X_shape_train, X_shape_test = X_shape.iloc[train_idx].copy(), X_shape.iloc[test_idx].copy()
        y_train, y_test = y[train_idx], y[test_idx]
        
        # 1. Feature selection on TRAIN ONLY
        selected_shapes = select_features_vif(X_shape_train, drop_priority, threshold=10.0)
        print(f"  Selected Shape Features: {selected_shapes}")
        
        # Build M3 train/test
        if len(selected_shapes) > 0:
            X3_train = pd.concat([X2_train, X_shape_train[selected_shapes]], axis=1)
            X3_test = pd.concat([X2_test, X_shape_test[selected_shapes]], axis=1)
        else:
            X3_train = X2_train.copy()
            X3_test = X2_test.copy()
            
        # Add constants
        X2_train_c = sm.add_constant(X2_train.astype(float), has_constant='add')
        X2_test_c = sm.add_constant(X2_test.astype(float), has_constant='add')
        
        X3_train_c = sm.add_constant(X3_train.astype(float), has_constant='add')
        X3_test_c = sm.add_constant(X3_test.astype(float), has_constant='add')
        
        # Fit OLS
        m2_model = sm.OLS(y_train, X2_train_c).fit(cov_type='HC3')
        m3_model = sm.OLS(y_train, X3_train_c).fit(cov_type='HC3')
        
        # Predict and score
        pred2 = m2_model.predict(X2_test_c)
        pred3 = m3_model.predict(X3_test_c)
        
        r2_m2 = r2_score(y_test, pred2)
        r2_m3 = r2_score(y_test, pred3)
        delta_r2 = r2_m3 - r2_m2
        
        print(f"  M2 R2: {r2_m2:.4f}, M3 R2: {r2_m3:.4f}, Delta: {delta_r2:.4f}")
        
        results.append({
            "fold": fold_id,
            "selected_features": ", ".join(selected_shapes),
            "n_selected": len(selected_shapes),
            "r2_m2": r2_m2,
            "r2_m3": r2_m3,
            "delta_r2": delta_r2
        })
        
    df_res = pd.DataFrame(results)
    out_path = OUTPUT_DIR / "m3_shape_feature_cv_results.csv"
    df_res.to_csv(out_path, index=False)
    print(f"\nSaved results to {out_path}")
    print(f"Mean Delta R2 (M3 - M2): {df_res['delta_r2'].mean():.4f}")

if __name__ == "__main__":
    main()
