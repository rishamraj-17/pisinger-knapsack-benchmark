import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.stats.diagnostic as smd
import statsmodels.stats.outliers_influence as smoi
from scipy import stats
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any

def ols_diagnostics(model, X, y, model_name, output_dir):
    """Run diagnostics for OLS models."""
    results = {}
    
    # Residuals
    residuals = model.resid
    fitted = model.fittedvalues
    
    # 1. Breusch-Pagan test
    try:
        bp_test = smd.het_breuschpagan(residuals, model.model.exog)
        results['bp_lm_stat'] = bp_test[0]
        results['bp_lm_pval'] = bp_test[1]
        results['bp_f_stat'] = bp_test[2]
        results['bp_f_pval'] = bp_test[3]
    except Exception as e:
        results['bp_error'] = str(e)

    # 2. VIF
    vif_data = pd.DataFrame()
    vif_data["predictor"] = X.columns
    vif_values = []
    exog = model.model.exog
    for i in range(exog.shape[1]):
        if i == 0 and np.all(exog[:, 0] == 1):
            vif_values.append(np.nan) # skip constant
        else:
            try:
                vif = smoi.variance_inflation_factor(exog, i)
            except:
                vif = np.nan
            vif_values.append(vif)
    
    # If constant was added to X, vif_data won't match unless we check
    if len(vif_values) == len(X.columns) + 1:
        vif_data["VIF"] = vif_values[1:] # skip const
    else:
        vif_data["VIF"] = vif_values
    
    vif_data.to_csv(output_dir / f"vif_{model_name}.csv", index=False)
    results['max_vif'] = vif_data['VIF'].max()
    
    # 3. Cook's Distance
    try:
        influence = model.get_influence()
        cooks = influence.cooks_distance[0]
        results['max_cooks_d'] = np.max(cooks)
        results['num_cooks_gt_1'] = np.sum(cooks > 1)
        
        plt.figure(figsize=(10, 6))
        plt.stem(cooks, markerfmt=",")
        plt.title(f"Cook's Distance - {model_name}")
        plt.xlabel("Observation")
        plt.ylabel("Cook's d")
        plt.axhline(1, color='r', linestyle='--')
        plt.savefig(output_dir / f"cooks_{model_name}.png", bbox_inches='tight')
        plt.close()
    except Exception as e:
        results['cooks_error'] = str(e)
        
    # 4. Q-Q Plot
    plt.figure(figsize=(8, 8))
    sm.qqplot(residuals, line='45', fit=True)
    plt.title(f"Normal Q-Q - {model_name}")
    plt.savefig(output_dir / f"qq_{model_name}.png", bbox_inches='tight')
    plt.close()
    
    # 5. Residual vs Fitted
    plt.figure(figsize=(10, 6))
    plt.scatter(fitted, residuals, alpha=0.3)
    plt.axhline(0, color='r', linestyle='--')
    plt.xlabel("Fitted Values")
    plt.ylabel("Residuals")
    plt.title(f"Residual vs Fitted - {model_name}")
    plt.savefig(output_dir / f"residual_vs_fitted_{model_name}.png", bbox_inches='tight')
    plt.close()
    
    # 6. Residual histogram
    plt.figure(figsize=(8, 6))
    plt.hist(residuals, bins=30, alpha=0.7, edgecolor='black')
    plt.title(f"Residual Histogram - {model_name}")
    plt.savefig(output_dir / f"residual_hist_{model_name}.png", bbox_inches='tight')
    plt.close()

    # 7. Partial Residual Plots (Top-5 predictors based on t-stat)
    try:
        t_stats = np.abs(model.tvalues)
        if 'const' in t_stats.index:
            t_stats = t_stats.drop('const')
        top5 = t_stats.nlargest(5).index
        for p in top5:
            if p in model.model.exog_names:
                plt.figure(figsize=(8, 6))
                sm.graphics.plot_ccpr(model, p)
                plt.title(f"Partial Residual - {p} ({model_name})")
                plt.savefig(output_dir / f"partial_resid_{model_name}_{p}.png", bbox_inches='tight')
                plt.close()
    except Exception as e:
        results['partial_resid_error'] = str(e)
        
    # 8. Residual Autocorrelation
    try:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        # Autocorrelation requires ordering. We assume X is passed in the original dataset order.
        # Plotting ACF on residuals directly
        sm.graphics.tsa.plot_acf(residuals, lags=40, ax=axes[0])
        axes[0].set_title(f"Residual Autocorrelation - {model_name}")
        # Not explicitly sorting by n or instance_id here because we don't have them in X, 
        # but the original dataframe was already ordered by instance_id, family, n.
        axes[1].plot(residuals.values if hasattr(residuals, 'values') else residuals, alpha=0.5)
        axes[1].set_title("Residuals Sequence")
        plt.savefig(output_dir / f"autocorr_{model_name}.png", bbox_inches='tight')
        plt.close()
    except Exception as e:
        results['autocorr_error'] = str(e)
    
    return results

def fractional_logit_diagnostics(model, X, y, model_name, output_dir):
    """Run diagnostics for Fractional Logit models."""
    results = {}
    
    # 1. Link Test (significance of y_hat^2)
    try:
        fitted = model.predict(model.model.exog)
        fitted_sq = fitted ** 2
        
        X_link = pd.DataFrame({'fitted': fitted, 'fitted_sq': fitted_sq})
        X_link = sm.add_constant(X_link)
        link_model = sm.GLM(y, X_link, family=sm.families.Binomial(), cov_type='HC3').fit()
        
        results['link_test_pval'] = link_model.pvalues['fitted_sq']
        results['link_test_sig'] = bool(link_model.pvalues['fitted_sq'] < 0.05)
    except Exception as e:
        results['link_error'] = str(e)
        
    # 2. Boundary sensitivity (Smithson-Verkuilen transform)
    # y_sv = (y * (n - 1) + 0.5) / n (we assume n is len(y))
    n = len(y)
    y_sv = (y * (n - 1) + 0.5) / n
    try:
        model_sv = sm.GLM(y_sv, model.model.exog, family=sm.families.Binomial(), cov_type='HC3').fit()
        
        # Max absolute percentage difference in coefficients
        coef_diff = np.abs((model.params - model_sv.params) / model.params)
        results['max_coef_diff_sv'] = np.max(coef_diff)
    except Exception as e:
        results['sv_error'] = str(e)
        
    # 3. Sandwich vs Standard SE
    try:
        model_std = sm.GLM(y, model.model.exog, family=sm.families.Binomial()).fit() # non-robust
        se_ratio = model.bse / model_std.bse
        results['max_se_ratio'] = np.max(se_ratio)
    except Exception as e:
        results['se_ratio_error'] = str(e)
        
    return results

def elasticnet_diagnostics(model, X, y, lofo_metrics_df, model_name, output_dir):
    """Run diagnostics for Elastic-Net models."""
    results = {}
    
    # 1. LOFO lambda stability (computed from lofo metrics)
    if lofo_metrics_df is not None:
        try:
            if 'best_c' in lofo_metrics_df:
                lambdas = 1.0 / lofo_metrics_df['best_c']
                log_lambdas = np.log(lambdas)
                results['lambda_sd'] = np.std(log_lambdas)
                results['lambda_min'] = np.min(lambdas)
                results['lambda_max'] = np.max(lambdas)
        except Exception as e:
            results['lambda_error'] = str(e)
            
    # 2. Calibration curve
    try:
        y_prob = model.predict_proba(X)[:, 1]
        from sklearn.calibration import calibration_curve
        prob_true, prob_pred = calibration_curve(y, y_prob, n_bins=10)
        
        plt.figure(figsize=(8, 8))
        plt.plot(prob_pred, prob_true, marker='o', label='Elastic-Net')
        plt.plot([0, 1], [0, 1], linestyle='--', color='k', label='Perfectly Calibrated')
        plt.xlabel('Predicted Probability')
        plt.ylabel('Observed Proportion')
        plt.title(f'Calibration Curve - {model_name}')
        plt.legend()
        plt.savefig(output_dir / f"calibration_curve_{model_name}.png", bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        results['calib_error'] = str(e)
        
    return results

def calculate_smearing_factor(model, y_log, y_orig, families, output_dir, model_name):
    """Calculate Duan's smearing factor for log-transformed models."""
    residuals = model.resid
    
    # Pooled smearing factor
    pooled_phi = np.mean(np.exp(residuals))
    
    # Family-specific smearing factor
    family_phi = {}
    for fam in np.unique(families):
        mask = (families == fam)
        family_phi[fam] = np.mean(np.exp(residuals[mask]))
        
    # Predictions
    fitted_log = model.fittedvalues
    pred_orig_pooled = np.exp(fitted_log) * pooled_phi
    
    pred_orig_family = np.zeros_like(fitted_log)
    for fam in np.unique(families):
        mask = (families == fam)
        pred_orig_family[mask] = np.exp(fitted_log[mask]) * family_phi[fam]
        
    # RMSE
    rmse_pooled = np.sqrt(np.mean((y_orig - pred_orig_pooled)**2))
    rmse_family = np.sqrt(np.mean((y_orig - pred_orig_family)**2))
    
    results = {
        'pooled_phi': pooled_phi,
        'rmse_pooled': rmse_pooled,
        'rmse_family': rmse_family,
        'rmse_diff_pct': (rmse_pooled - rmse_family) / rmse_family * 100
    }
    
    return results
