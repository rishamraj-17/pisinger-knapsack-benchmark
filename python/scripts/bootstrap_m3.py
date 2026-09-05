import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import r2_score

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
               
    shape_features = ['depth_p10', 'depth_entropy', 'depth_skew', 'queue_entropy']
    
    for col in m1_cols + m2_cols + shape_features:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            
    available_m1_m2 = [c for c in m1_cols + m2_cols if c in df.columns]
    
    X2 = df[available_m1_m2]
    X3 = df[available_m1_m2 + shape_features]
    
    X2_std = (X2 - X2.mean()) / (X2.std() + 1e-9)
    X3_std = (X3 - X3.mean()) / (X3.std() + 1e-9)
    
    X2_const = sm.add_constant(X2_std)
    X3_const = sm.add_constant(X3_std)
    y = df['log_nodes_explored']
    
    print("\n--- Step 4: LOFO Bootstrap CI ---")
    families = df['family'].unique()
    n_boot = 1000
    np.random.seed(42)
    
    for fam in families:
        train_idx = df['family'] != fam
        test_idx = df['family'] == fam
        
        y_train = y[train_idx]
        y_test = y[test_idx].values
        
        X2_train = X2_const[train_idx]
        X2_test = X2_const[test_idx]
        
        X3_train = X3_const[train_idx]
        X3_test = X3_const[test_idx]
        
        # Fit on train, predict on test
        m2_lofo = sm.OLS(y_train, X2_train).fit()
        m3_lofo = sm.OLS(y_train, X3_train).fit()
        
        pred2 = m2_lofo.predict(X2_test).values
        pred3 = m3_lofo.predict(X3_test).values
        
        r2_m2 = r2_score(y_test, pred2)
        r2_m3 = r2_score(y_test, pred3)
        delta_actual = r2_m3 - r2_m2
        
        # Bootstrap
        n_samples = len(y_test)
        deltas = []
        
        for _ in range(n_boot):
            boot_idx = np.random.randint(0, n_samples, n_samples)
            boot_y = y_test[boot_idx]
            boot_p2 = pred2[boot_idx]
            boot_p3 = pred3[boot_idx]
            
            # Prevent perfectly constant boot_y in small extreme samples
            if len(np.unique(boot_y)) > 1:
                b_r2_2 = r2_score(boot_y, boot_p2)
                b_r2_3 = r2_score(boot_y, boot_p3)
                deltas.append(b_r2_3 - b_r2_2)
                
        if len(deltas) > 0:
            ci_lower = np.percentile(deltas, 2.5)
            ci_upper = np.percentile(deltas, 97.5)
            mean_delta = np.mean(deltas)
            
            print(f"Holdout Family: {fam}")
            print(f"  M2 R2: {r2_m2:.4f}")
            print(f"  M3 R2: {r2_m3:.4f}")
            print(f"  Delta R2 (actual): {delta_actual:.4f}")
            print(f"  Bootstrap Mean Delta: {mean_delta:.4f}")
            print(f"  95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
            if ci_lower > 0:
                print("  => CI excludes zero (Statistically Significant Improvement)")
            elif ci_upper < 0:
                print("  => CI completely negative (Statistically Significant Degradation)")
            else:
                print("  => CI includes zero (Not statistically distinguishable from zero)")
            print()

if __name__ == '__main__':
    main()
