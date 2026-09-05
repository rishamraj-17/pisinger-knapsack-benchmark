import pandas as pd
import numpy as np
from scipy.stats import entropy
import ast

def extract_shape_features():
    print("Reading BB instrumentation...")
    df = pd.read_csv('results/bb_instrumentation.csv')
    
    # We will build a new dataframe with shape features
    shape_df = pd.DataFrame()
    shape_df['instance_id'] = df['instance_id']
    
    # Parse depth histograms
    print("Parsing depth histograms...")
    p10_list, p50_list, p90_list = [], [], []
    depth_entropy, depth_skew = [], []
    
    for idx, row in df.iterrows():
        # Parse the string array, handle empty or malformed
        try:
            hist = np.array([int(x) for x in str(row['depth_histogram']).split(',')])
        except:
            hist = np.zeros(1)
            
        nodes = hist.sum()
        if nodes == 0:
            p10_list.append(0)
            p50_list.append(0)
            p90_list.append(0)
            depth_entropy.append(0)
            depth_skew.append(0)
            continue
            
        # Normalize
        pmf = hist / nodes
        
        # Calculate quantiles
        cdf = np.cumsum(pmf)
        p10_list.append(np.argmax(cdf >= 0.10))
        p50_list.append(np.argmax(cdf >= 0.50))
        p90_list.append(np.argmax(cdf >= 0.90))
        
        # Entropy
        depth_entropy.append(entropy(pmf, base=2))
        
        # Skewness
        depths = np.arange(len(hist))
        mean_depth = np.sum(depths * pmf)
        var_depth = np.sum((depths - mean_depth)**2 * pmf)
        if var_depth > 0:
            skew_depth = np.sum(((depths - mean_depth)/np.sqrt(var_depth))**3 * pmf)
        else:
            skew_depth = 0
        depth_skew.append(skew_depth)
        
    shape_df['depth_p10'] = p10_list
    shape_df['depth_p50'] = p50_list
    shape_df['depth_p90'] = p90_list
    shape_df['depth_entropy'] = depth_entropy
    shape_df['depth_skew'] = depth_skew
    
    # Parse queue histograms
    print("Parsing queue histograms...")
    queue_entropy = []
    for idx, row in df.iterrows():
        try:
            hist = np.array([int(x) for x in str(row['queue_histogram']).split(',')])
        except:
            hist = np.zeros(1)
            
        samples = hist.sum()
        if samples == 0:
            queue_entropy.append(0)
        else:
            pmf = hist / samples
            queue_entropy.append(entropy(pmf, base=2))
            
    shape_df['queue_entropy'] = queue_entropy
    
    # Save
    out_path = 'results/shape_features.csv'
    shape_df.to_csv(out_path, index=False)
    print(f"Saved {len(shape_df)} rows to {out_path}")

if __name__ == '__main__':
    extract_shape_features()
