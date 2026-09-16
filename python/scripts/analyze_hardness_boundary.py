"""
python/scripts/analyze_hardness_boundary.py

Logistic regression modeling P(solved) as a function of structural features
to formally model the zero-event problem (Task 15).
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modeling.config import GROUP_A_INSTANCE_CHARACTERISTICS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "data" / "instrumentation"
RESULTS_DIR = BASE_DIR.parent / "results" / "revision-2"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("Zero-Event Analysis: Logistic Regression on P(solved)")
    print("=" * 60)
    
    df_path = BASE_DIR / "modeling" / "output" / "prepared" / "BandB.pkl"
    if not df_path.exists():
        print(f"Data file not found: {df_path}")
        return
        
    df = pd.read_pickle(str(df_path))
    
    if 'optimal' not in df.columns:
        print("Column 'optimal' not found. Cannot run.")
        return
        
    y = df['optimal'].astype(int).values
    
    # Check for complete separation by family
    print("\nCompletion rates by family:")
    family_rates = df.groupby('family')['optimal'].mean()
    print(family_rates)
    
    # We predict P(solved == 0) i.e. P(timeout)
    # Let's just predict P(solved == False) so it's a "hardness" model
    y_hard = 1 - y
    print(f"\nTotal instances: {len(y_hard)}")
    print(f"Total timeouts/unsolved: {y_hard.sum()} ({y_hard.sum() / len(y_hard):.1%})")
    
    # Features: use instance characteristics
    features = [f for f in GROUP_A_INSTANCE_CHARACTERISTICS if f in df.columns]
    X = df[features].fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Using L1 regularization to do feature selection and handle complete separation
    clf = LogisticRegression(penalty='l1', solver='liblinear', C=1.0, random_state=42)
    clf.fit(X_scaled, y_hard)
    
    y_pred = clf.predict(X_scaled)
    y_prob = clf.predict_proba(X_scaled)[:, 1]
    
    print("\nModel Performance on Full Data:")
    print(f"AUC: {roc_auc_score(y_hard, y_prob):.4f}")
    print(classification_report(y_hard, y_pred, target_names=["Solved", "Unsolved"]))
    
    # Extract coefficients
    coef_df = pd.DataFrame({
        'feature': features,
        'coefficient': clf.coef_[0],
        'abs_coef': np.abs(clf.coef_[0])
    })
    
    coef_df = coef_df[coef_df['abs_coef'] > 1e-4]
    coef_df = coef_df.sort_values('abs_coef', ascending=False).reset_index(drop=True)
    
    print("\nTop Predictors of Hardness (P(timeout)):")
    print(coef_df.head(15))
    
    out_path = RESULTS_DIR / "hardness_boundary_coefs.csv"
    coef_df.to_csv(out_path, index=False)
    print(f"\nSaved coefficients to {out_path}")

if __name__ == "__main__":
    main()
