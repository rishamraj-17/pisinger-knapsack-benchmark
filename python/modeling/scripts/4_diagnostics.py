import os
import sys
import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import RANDOM_SEED, MODEL_SPECS, ALGO_GREEDY, ALGO_DP, ALGO_BB
from utils.preprocessing import build_feature_matrices
from utils.models import fit_ols, fit_elasticnet, cluster_robust_se
from utils.fractional_models import fit_fractional_logit, flogit_cluster_robust_se
from utils.diagnostics import ols_diagnostics, fractional_logit_diagnostics, elasticnet_diagnostics, calculate_smearing_factor

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PREPARED_DIR = OUTPUT_DIR / "prepared"
RESULTS_DIR = OUTPUT_DIR / "results"
CV_DIR = OUTPUT_DIR / "cross_validation"
DIAG_DIR = OUTPUT_DIR / "diagnostics"
FIG_DIR = OUTPUT_DIR / "figures"

for d in [DIAG_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Helper for iterative VIF thinning
def perform_vif_thinning(X, y, model_algo, model_response):
    import statsmodels.stats.outliers_influence as smoi
    X_thinned = X.copy()
    removed = []
    
    for round_num in range(20):
        X_with_const = sm.add_constant(X_thinned.astype(float), prepend=True, has_constant='add')
        vif_values = []
        for i in range(X_with_const.shape[1]):
            if i == 0 and np.all(X_with_const.values[:, 0] == 1):
                vif_values.append(0.0)
            else:
                try:
                    vif_values.append(smoi.variance_inflation_factor(X_with_const.values, i))
                except:
                    vif_values.append(0.0)
                    
        vifs = pd.Series(vif_values, index=X_with_const.columns)
        vifs = vifs.drop('const', errors='ignore')
        
        max_vif = vifs.max()
        if max_vif > 10:
            drop_col = vifs.idxmax()
            removed.append(drop_col)
            X_thinned = X_thinned.drop(columns=[drop_col])
        else:
            break
            
    # Compute new Delta R2
    return X_thinned, removed

def run_diagnostics():
    print("Loading prepared dataset...")
    df_cache = {}
    for algo_label in ['Greedy', 'DP', 'BandB']:
        pkl_path = PREPARED_DIR / f"{algo_label}.pkl"
        if pkl_path.exists():
            df_cache[algo_label] = pd.read_pickle(str(pkl_path))
            if "instance_id" not in df_cache[algo_label].columns:
                df_cache[algo_label]["instance_id"] = range(len(df_cache[algo_label]))
    
    # Models to process (excluding hurdle)
    models = [
        (ALGO_GREEDY, 'log_time_millis'),
        (ALGO_GREEDY, 'optimality_gap'),
        (ALGO_DP, 'log_time_millis'),
        (ALGO_DP, 'log_memory_mb'),
        (ALGO_DP, 'fill_rate'),
        (ALGO_BB, 'log_time_millis'),
        (ALGO_BB, 'log_nodes_explored'),
        (ALGO_BB, 'optimal')
    ]
    
    vif_comparison_rows = []
    smearing_rows = []
    
    for algo, response in models:
        print(f"\n{'='*50}\nPhase 3.3.6 Diagnostics: {algo} - {response}")
        spec = MODEL_SPECS[(algo, response)]
        model_family = spec['family']
        
        # Build matrices
        algo_label = 'Greedy' if algo == ALGO_GREEDY else 'DP' if algo == ALGO_DP else 'BandB'
        data_df = df_cache[algo_label].copy()
        
        data_df.reset_index(drop=True, inplace=True)
        instance_ids = data_df['instance_id'].values
        families = data_df['family'].values
        
        import config
        X_m1, X_m2, y, m1_cols, m2_cols = build_feature_matrices(
            data_df, algo, response, MODEL_SPECS, config
        )
        
        model_name = f"{algo}_{response}"
        
        if model_family == 'ols':
            print("  Fitting M2 OLS...")
            model_m2 = fit_ols(X_m2, y)
            
            # Apply cluster robust inference
            cr_model_m2 = cluster_robust_se(model_m2, instance_ids)
            
            print("  Running OLS diagnostics...")
            res = ols_diagnostics(cr_model_m2, X_m2, y, model_name, DIAG_DIR)
            
            # Write assumption summary
            with open(DIAG_DIR / f"assumption_summary_{model_name}.txt", "w") as f:
                for k, v in res.items():
                    f.write(f"{k}: {v}\n")
                    
            if 'bp_lm_pval' in res:
                with open(DIAG_DIR / "residual_tests_ols.csv", "a") as f:
                    f.write(f"{model_name},{res['bp_lm_stat']},{res['bp_lm_pval']}\n")
                    
            # VIF thinning check
            if res.get('max_vif', 0) > 10:
                print("  VIF > 10 found. Performing iterative thinning...")
                X_m2_thinned, removed = perform_vif_thinning(X_m2, y, algo, response)
                
                # Save removed list
                pd.Series(removed).to_csv(DIAG_DIR / f"vif_removed_predictors_{model_name}.csv", index=False)
                
                # Re-fit M1 and thinned M2 to get delta R2
                model_m1 = fit_ols(X_m1, y)
                r2_m1 = model_m1.rsquared
                r2_m2_raw = model_m2.rsquared
                delta_r2_raw = r2_m2_raw - r2_m1
                
                model_m2_thinned = fit_ols(X_m2_thinned, y)
                r2_m2_thinned = model_m2_thinned.rsquared
                delta_r2_thinned = r2_m2_thinned - r2_m1
                
                vif_comparison_rows.append({
                    "algorithm": algo,
                    "response": response,
                    "raw_delta_r2": delta_r2_raw,
                    "thinned_delta_r2": delta_r2_thinned,
                    "diff": delta_r2_raw - delta_r2_thinned,
                    "removed_count": len(removed)
                })
            
            # Smearing factor for log-transformed continuous responses
            if response.startswith('log_'):
                print("  Calculating smearing factors...")
                y_orig = data_df[response.replace('log_', '')].values if response.replace('log_', '') in data_df.columns else None
                if y_orig is None and response == 'log_time_millis':
                    y_orig = data_df['time_millis'].values
                elif y_orig is None and response == 'log_memory_mb':
                    y_orig = data_df['memory_mb'].values
                elif y_orig is None and response == 'log_nodes_explored':
                    y_orig = data_df['nodes_explored'].values
                
                if y_orig is not None:
                    sm_res = calculate_smearing_factor(model_m2, y, y_orig, families, DIAG_DIR, model_name)
                    sm_res['algorithm'] = algo
                    sm_res['response'] = response
                    smearing_rows.append(sm_res)
                    
        elif model_family == 'fractional_logit':
            print("  Fitting M2 Fractional Logit...")
            model_m2 = fit_fractional_logit(X_m2, y)
            
            # Cluster robust
            cr_model_m2 = flogit_cluster_robust_se(model_m2, instance_ids)
            
            print("  Running Fractional Logit diagnostics...")
            res = fractional_logit_diagnostics(cr_model_m2, X_m2, y, model_name, DIAG_DIR)
            
            with open(DIAG_DIR / f"assumption_summary_{model_name}.txt", "w") as f:
                for k, v in res.items():
                    f.write(f"{k}: {v}\n")
                    
        elif model_family == 'elasticnet':
            print("  Fitting M2 Elastic-Net...")
            # We just fit once here to get a model for calibration curves, but we also read LOFO for lambda path
            model_m2 = fit_elasticnet(X_m2, y, alpha=0.5, cv_folds=5)
            
            lofo_path = CV_DIR / "lofo_folds_elasticnet.csv"
            lofo_df = pd.read_csv(lofo_path) if lofo_path.exists() else None
            
            print("  Running Elastic-Net diagnostics...")
            res = elasticnet_diagnostics(model_m2, X_m2, y, lofo_df, model_name, DIAG_DIR)
            
            with open(DIAG_DIR / f"assumption_summary_{model_name}.txt", "w") as f:
                for k, v in res.items():
                    f.write(f"{k}: {v}\n")

    # Save summary tables
    if vif_comparison_rows:
        pd.DataFrame(vif_comparison_rows).to_csv(DIAG_DIR / "vif_thinned_delta_r2_comparison.csv", index=False)
    else:
        with open(DIAG_DIR / "vif_thinned_delta_r2_comparison.csv", "w") as f:
            f.write("No VIF thinning needed for any model.\n")
            
    if smearing_rows:
        pd.DataFrame(smearing_rows).to_csv(DIAG_DIR / "smearing_factors.csv", index=False)

if __name__ == "__main__":
    run_diagnostics()
    print("\nPhase 3.3.6 Diagnostic checks completed successfully.")
