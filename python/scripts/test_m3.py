import pandas as pd
import numpy as np
import statsmodels.api as sm

def main():
    # Load data
    instances = pd.read_csv('data/instrumentation/instances.csv')
    bb = pd.read_csv('data/instrumentation/bb_instrumentation.csv')
    shapes = pd.read_csv('data/instrumentation/shape_features.csv')
    
    # Merge
    df = instances.merge(bb, on='instance_id', suffixes=('', '_bb'))
    df = df.merge(shapes, on='instance_id')
    
    # Filter only valid outcomes
    df = df[df['nodes_explored'] > 0].copy()
    df['log_nodes_explored'] = np.log(df['nodes_explored'])
    
    # M1 predictors (approximating from the paper)
    m1_cols = ['total_weight', 'total_profit', 'capacity_ratio', 'profit_density', 'slack',
               'n', 'n_log_n', 'n_squared']
    
    # M2 predictors (internal execution metrics)
    m2_cols = ['max_depth', 'mean_depth', 'median_depth', 'min_depth', 
               'max_queue_size', 'mean_queue_size', 'final_queue_size',
               'mean_bound', 'bound_variance', 'min_bound', 'max_bound',
               'mean_bound_gap', 'bound_gap_variance',
               'pruned_by_bound', 'pruned_by_cap',
               'explored_children', 'skipped_children', 'skipped_infeasible', 'skipped_by_cap',
               'improvement_count', 'mean_improvement_amount', 'explored_generated_ratio',
               'avg_branching_factor']
               
    # M3 predictors
    m3_cols = ['depth_p10', 'depth_p50', 'depth_p90', 'depth_entropy', 'depth_skew', 'queue_entropy']
    
    # Impute missing with 0 and take numeric columns
    for col in m1_cols + m2_cols + m3_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            
    # Check what is actually available
    available_m1 = [c for c in m1_cols if c in df.columns]
    available_m2 = [c for c in m2_cols if c in df.columns]
    
    # Prepare X, Y
    X2 = df[available_m1 + available_m2]
    X3 = df[available_m1 + available_m2 + m3_cols]
    
    # Standardize
    X2 = (X2 - X2.mean()) / (X2.std() + 1e-9)
    X3 = (X3 - X3.mean()) / (X3.std() + 1e-9)
    
    # Add constant
    X2 = sm.add_constant(X2)
    X3 = sm.add_constant(X3)
    y = df['log_nodes_explored']
    
    # Fit OLS
    model2 = sm.OLS(y, X2).fit()
    model3 = sm.OLS(y, X3).fit()
    
    print(f"M2 Adj R2: {model2.rsquared_adj:.4f}")
    print(f"M3 Adj R2: {model3.rsquared_adj:.4f}")
    print(f"Delta Adj R2: {model3.rsquared_adj - model2.rsquared_adj:.4f}")
    
    print("\nShape Feature Standardized Beta Coefficients:")
    for col in m3_cols:
        if col in model3.params:
            print(f"  {col}: {model3.params[col]:.4f} (p={model3.pvalues[col]:.4f})")

if __name__ == '__main__':
    main()
