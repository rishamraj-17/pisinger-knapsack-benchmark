import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.anova import anova_lm
from sklearn.metrics import r2_score

def compute_vif(X):
    X_const = sm.add_constant(X)
    vif_data = pd.DataFrame()
    vif_data['feature'] = X_const.columns
    vif_data['VIF'] = [variance_inflation_factor(X_const.values, i) for i in range(X_const.shape[1])]
    return vif_data

def main():
    print("--- Loading Data ---")
    instances = pd.read_csv('data/instrumentation/instances.csv')
    bb = pd.read_csv('data/instrumentation/bb_instrumentation.csv')
    shapes = pd.read_csv('data/instrumentation/shape_features.csv')
    
    df = instances.merge(bb, on='instance_id', suffixes=('', '_bb'))
    df = df.merge(shapes, on='instance_id')
    
    df = df[df['nodes_explored'] > 0].copy()
    df['log_nodes_explored'] = np.log(df['nodes_explored'])
    
    m1_cols = ['total_weight', 'total_profit', 'capacity_ratio', 'profit_density', 'slack',
               'n', 'n_log_n', 'n_squared']
    m2_cols = ['max_depth', 'mean_depth', 'median_depth', 'min_depth', 
               'max_queue_size', 'mean_queue_size', 'final_queue_size',
               'mean_bound', 'bound_variance', 'min_bound', 'max_bound',
               'mean_bound_gap', 'bound_gap_variance',
               'pruned_by_bound', 'pruned_by_cap',
               'explored_children', 'skipped_children', 'skipped_infeasible', 'skipped_by_cap',
               'improvement_count', 'mean_improvement_amount', 'explored_generated_ratio',
               'avg_branching_factor']
               
    shape_features = ['depth_p10', 'depth_p50', 'depth_p90', 'depth_entropy', 'depth_skew', 'queue_entropy']
    
    for col in m1_cols + m2_cols + shape_features:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            
    available_m1_m2 = [c for c in m1_cols + m2_cols if c in df.columns]
    
    print("\n--- Step 1: VIF Check ---")
    # Standardize for VIF
    X_shape = df[shape_features].dropna()
    X_shape_std = (X_shape - X_shape.mean()) / (X_shape.std() + 1e-9)
    vif_data = compute_vif(X_shape_std)
    print("Initial VIF:")
    print(vif_data)
    
    trimmed_features = shape_features.copy()
    
    # Priority for dropping: quantiles before entropy/skew
    drop_priority = ['depth_p50', 'depth_p90', 'depth_p10', 'depth_skew', 'depth_entropy', 'queue_entropy']
    
    while True:
        max_vif = vif_data[vif_data['feature'] != 'const']['VIF'].max()
        if max_vif <= 10:
            break
            
        # Find feature to drop
        vif_ex_const = vif_data[vif_data['feature'] != 'const']
        problem_features = vif_ex_const[vif_ex_const['VIF'] > 10]['feature'].tolist()
        
        # Drop the lowest priority one that has VIF > 10
        to_drop = None
        for p in drop_priority:
            if p in problem_features:
                to_drop = p
                break
                
        if to_drop is None:
            break
            
        print(f"\nDropping {to_drop} due to high VIF.")
        trimmed_features.remove(to_drop)
        X_shape_std = X_shape_std[trimmed_features]
        vif_data = compute_vif(X_shape_std)
        print(vif_data)
        
    print("\nFinal Trimmed Shape Features:", trimmed_features)
    
    # Drop depth_p90 manually as requested by the user
    if 'depth_p90' in trimmed_features:
        trimmed_features.remove('depth_p90')
        print("Dropped depth_p90 as requested for further robustness check.")
        print("M3 features are now:", trimmed_features)
    
    # Rerun M2 vs M3
    X2 = df[available_m1_m2]
    X3 = df[available_m1_m2 + trimmed_features]
    
    X2_std = (X2 - X2.mean()) / (X2.std() + 1e-9)
    X3_std = (X3 - X3.mean()) / (X3.std() + 1e-9)
    
    X2_const = sm.add_constant(X2_std)
    X3_const = sm.add_constant(X3_std)
    y = df['log_nodes_explored']
    
    model2 = sm.OLS(y, X2_const).fit()
    model3 = sm.OLS(y, X3_const).fit()
    
    print(f"\nM2 Adj R2: {model2.rsquared_adj:.4f}")
    print(f"Trimmed M3 Adj R2: {model3.rsquared_adj:.4f}")
    print(f"Trimmed Delta Adj R2: {model3.rsquared_adj - model2.rsquared_adj:.4f}")
    
    print("\n--- Step 2: Correlation Check ---")
    cols = list(set(trimmed_features + available_m1_m2 + ['n']))
    corr_df = df[cols].copy()
    
    # One-hot family
    family_dummies = pd.get_dummies(df['family'], prefix='family')
    corr_df = pd.concat([corr_df, family_dummies], axis=1)
    
    corr_matrix = corr_df.corr()
    print("Pairs with |correlation| > 0.6:")
    for f in trimmed_features:
        for c in corr_df.columns:
            if f != c:
                corr = corr_matrix.loc[f, c]
                if abs(corr) > 0.6:
                    print(f"  {f} <-> {c}: {corr:.4f}")
                    
    print("\n--- Step 3: Nested F-Test ---")
    anova_results = anova_lm(model2, model3)
    print(anova_results)
    
    print("\n--- Step 4: LOFO Rerun ---")
    families = df['family'].unique()
    for fam in families:
        train_idx = df['family'] != fam
        test_idx = df['family'] == fam
        
        y_train = y[train_idx]
        y_test = y[test_idx]
        
        X2_train = X2_const[train_idx]
        X2_test = X2_const[test_idx]
        
        X3_train = X3_const[train_idx]
        X3_test = X3_const[test_idx]
        
        # Fit on train, predict on test
        m2_lofo = sm.OLS(y_train, X2_train).fit()
        m3_lofo = sm.OLS(y_train, X3_train).fit()
        
        pred2 = m2_lofo.predict(X2_test)
        pred3 = m3_lofo.predict(X3_test)
        
        r2_m2 = r2_score(y_test, pred2)
        r2_m3 = r2_score(y_test, pred3)
        
        print(f"Holdout Family: {fam}")
        print(f"  M2 R2: {r2_m2:.4f}")
        print(f"  M3 R2: {r2_m3:.4f}")
        print(f"  Delta: {r2_m3 - r2_m2:.4f}")
        print()

if __name__ == '__main__':
    main()
