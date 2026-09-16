"""
python/scripts/plot_generalization_space.py

PCA visualization of the instance feature space, colored by:
  (a) structural family
  (b) LOFO generalization outcome (R² group: good / moderate / poor)

Output:
  results/revision-2/generalization-space/instance_pca_family.png
  results/revision-2/generalization-space/instance_pca_lofo_r2.png
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modeling.config import GROUP_A_INSTANCE_CHARACTERISTICS

BASE_DIR = Path(__file__).resolve().parent.parent
PREPARED_DIR = BASE_DIR / "modeling" / "output" / "prepared"
RESULTS_DIR = BASE_DIR.parent / "results" / "revision-2" / "generalization-space"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# LOFO R² values from the paper's Table 3 / RQ3 analysis (B&B log_nodes_explored, M2)
LOFO_R2_BY_FAMILY = {
    "Uncorrelated":      -0.109,   # partial failure (from shape-analysis table)
    "WeaklyCorrelated":   0.119,   # partial success
    "StronglyCorrelated": 0.599,   # success
    "InverseCorrelated": -1.895,   # failure
    "AlmostEqualRatios": -152.18,  # catastrophic failure
}

FAMILY_COLORS = {
    "Uncorrelated":      "#4C72B0",
    "WeaklyCorrelated":  "#DD8452",
    "StronglyCorrelated":"#55A868",
    "InverseCorrelated": "#C44E52",
    "AlmostEqualRatios": "#8172B2",
}

def r2_to_group(r2: float) -> str:
    """Bin LOFO R² into generalisation quality groups."""
    if r2 > 0.3:
        return "Good (R² > 0.3)"
    elif r2 > -0.5:
        return "Moderate (−0.5 < R² ≤ 0.3)"
    else:
        return "Poor (R² ≤ −0.5)"

GROUP_COLORS = {
    "Good (R² > 0.3)":            "#2ecc71",
    "Moderate (−0.5 < R² ≤ 0.3)": "#f39c12",
    "Poor (R² ≤ −0.5)":           "#e74c3c",
}


def main():
    print("=" * 60)
    print("Phase 3: Generalization Space Visualization")
    print("=" * 60)

    bb_path = PREPARED_DIR / "BandB.pkl"
    if not bb_path.exists():
        print(f"Prepared data not found: {bb_path}")
        return

    df = pd.read_pickle(str(bb_path))
    print(f"Loaded {len(df)} instances.")

    static_features = [f for f in GROUP_A_INSTANCE_CHARACTERISTICS if f in df.columns]
    X = df[static_features].fillna(0).values
    families = df["family"].values

    # PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    var_explained = pca.explained_variance_ratio_ * 100
    print(f"PCA variance explained: PC1={var_explained[0]:.1f}%, PC2={var_explained[1]:.1f}%")

    # ---- Plot A: colored by family ----
    fig, ax = plt.subplots(figsize=(9, 7))
    for fam in sorted(FAMILY_COLORS.keys()):
        mask = families == fam
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
                   c=FAMILY_COLORS[fam], label=fam, alpha=0.4, s=10, linewidths=0)
    ax.set_xlabel(f"PC1 ({var_explained[0]:.1f}% variance)", fontsize=12)
    ax.set_ylabel(f"PC2 ({var_explained[1]:.1f}% variance)", fontsize=12)
    ax.set_title("Instance Feature Space (PCA)\nColored by Structural Family", fontsize=13)
    ax.legend(title="Family", fontsize=9, markerscale=2)
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    out_a = RESULTS_DIR / "instance_pca_family.png"
    plt.savefig(str(out_a), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_a}")

    # ---- Plot B: colored by LOFO generalization quality ----
    lofo_groups = np.array([
        r2_to_group(LOFO_R2_BY_FAMILY[fam]) for fam in families
    ])

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Left: scatter by generalization group
    ax = axes[0]
    for group in sorted(GROUP_COLORS.keys()):
        mask = lofo_groups == group
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
                   c=GROUP_COLORS[group], label=group, alpha=0.35, s=10, linewidths=0)
    ax.set_xlabel(f"PC1 ({var_explained[0]:.1f}%)", fontsize=11)
    ax.set_ylabel(f"PC2 ({var_explained[1]:.1f}%)", fontsize=11)
    ax.set_title("Instance Space Colored by\nLOFO Generalisation Quality", fontsize=12)
    ax.legend(title="LOFO R² Group\n(B&B log-nodes M2)", fontsize=8, markerscale=2,
              loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.3)

    # Right: annotation showing LOFO R² per family on a log scale
    ax2 = axes[1]
    fam_list = sorted(LOFO_R2_BY_FAMILY.keys())
    r2_vals = [LOFO_R2_BY_FAMILY[f] for f in fam_list]
    colors = [FAMILY_COLORS[f] for f in fam_list]
    bars = ax2.barh(fam_list, r2_vals, color=colors, alpha=0.8)
    ax2.axvline(0, color="black", linewidth=1.2, linestyle="--")
    ax2.axvline(0.3, color="#2ecc71", linewidth=1, linestyle=":", label="R²=0.3 (good threshold)")
    for bar, val in zip(bars, r2_vals):
        x = val - 2 if val < -5 else val + 1
        ax2.text(x, bar.get_y() + bar.get_height()/2,
                 f"{val:.2f}", va="center", fontsize=9,
                 color="white" if val < -5 else "black")
    ax2.set_xlabel("LOFO $R^2$ (B&B log-nodes explored, M2)", fontsize=11)
    ax2.set_title("LOFO Generalisation $R^2$\nby Held-Out Family", fontsize=12)
    ax2.legend(fontsize=8)
    ax2.grid(axis="x", linestyle="--", alpha=0.3)
    # Clip to readable range (AlmostEqualRatios is -152 which compresses everything)
    ax2.set_xlim(-20, 1.5)
    note = "Note: AlmostEqualRatios R²=−152 (clipped)"
    ax2.text(0.02, 0.02, note, transform=ax2.transAxes, fontsize=8, color="grey", style="italic")

    plt.tight_layout()
    out_b = RESULTS_DIR / "instance_pca_lofo_r2.png"
    plt.savefig(str(out_b), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_b}")

    print("\nGeneralization space visualization complete.")


if __name__ == "__main__":
    main()
