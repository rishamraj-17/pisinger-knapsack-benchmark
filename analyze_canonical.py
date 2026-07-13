#!/usr/bin/env python3
"""
Canonical analysis pipeline for Knapsack Empirical Comparison.

Pipeline:
  1. Run Main.java -> generates results/full_experiment.csv
  2. Run this script -> generates figures/ and tables/
  3. Use tables/*.tex in paper

Usage:
  python3 analyze_canonical.py [results/full_experiment.csv]
"""

import sys
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ─── Configuration ──────────────────────────────────────────────
CSV_FILE = sys.argv[1] if len(sys.argv) > 1 else 'out/results/full_experiment.csv'
FIGURES_DIR = 'figures'
TABLES_DIR = 'tables'

families = ['Uncorrelated', 'WeaklyCorrelated', 'StronglyCorrelated', 'InverseCorrelated', 'AlmostEqualRatios']
family_short = {
    'Uncorrelated': 'Uncorr.',
    'WeaklyCorrelated': 'WeakCorr.',
    'StronglyCorrelated': 'StrongCorr.',
    'InverseCorrelated': 'InverseCorr.',
    'AlmostEqualRatios': 'EqualRatios'
}
algorithms = ['Greedy', 'DynamicProgramming', 'BranchAndBound']
colors = {'Greedy': '#2E86AB', 'DynamicProgramming': '#A23B72', 'BranchAndBound': '#F18F01'}
markers = {'Greedy': 'o', 'DynamicProgramming': 's', 'BranchAndBound': '^'}

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

# ─── Load Data ──────────────────────────────────────────────────
print(f"Loading {CSV_FILE}...")
df = pd.read_csv(CSV_FILE)
print(f"Loaded {len(df)} rows")

# Compute greedy optimality gap (DP is ground truth)
greedy = df[df['algorithm'] == 'Greedy'].copy()
dp = df[df['algorithm'] == 'DynamicProgramming'][['instance_id', 'solution_value']].rename(
    columns={'solution_value': 'opt_value'})
greedy = greedy.merge(dp, on='instance_id', how='left')
greedy['gap_pct'] = (greedy['opt_value'] - greedy['solution_value']) / greedy['opt_value'] * 100

# ─── Style ──────────────────────────────────────────────────────
sns.set_style("whitegrid")
plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'legend.fontsize': 10, 'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'figure.dpi': 300, 'savefig.dpi': 300, 'savefig.bbox': 'tight'
})

# ══════════════════════════════════════════════════════════════════
# FIGURE 1: Time vs n (log-log) - 5 subplots, one per family
# ══════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharey=True)
axes = axes.flatten()

for idx, fam in enumerate(families):
    ax = axes[idx]
    sub = df[df['dataset_type'] == fam]
    
    for algo in algorithms:
        data = sub[sub['algorithm'] == algo].groupby('n')['time_millis'].agg(['mean', 'std']).reset_index()
        if len(data) == 0:
            continue
        ax.plot(data['n'], data['mean'], marker=markers[algo], color=colors[algo],
                label=algo, linewidth=1.5, markersize=5)
        ax.fill_between(data['n'], data['mean'] - data['std'], data['mean'] + data['std'],
                        color=colors[algo], alpha=0.15)
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('n')
    if idx % 3 == 0:
        ax.set_ylabel('Time (ms)')
    ax.set_title(family_short[fam], fontweight='bold')
    ax.grid(True, which='both', alpha=0.3)

fig.delaxes(axes[5])
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.02),
           ncol=3, frameon=True, fontsize=10)
fig.suptitle('Execution Time vs Problem Size (n) by Instance Family', y=1.05, fontsize=14)
plt.tight_layout()
plt.savefig(f'{FIGURES_DIR}/time_vs_n.png')
plt.close()

# ══════════════════════════════════════════════════════════════════
# FIGURE 2: Greedy Optimality Gap - Boxplot
# ══════════════════════════════════════════════════════════════════
plt.figure(figsize=(9, 5))
gap_data = [greedy[greedy['dataset_type'] == fam]['gap_pct'].values for fam in families]
bp = plt.boxplot(gap_data, labels=[family_short[f] for f in families],
                 patch_artist=True, showfliers=True, flierprops={'markersize': 3})
for patch, fam in zip(bp['boxes'], families):
    patch.set_facecolor(colors['Greedy'])
    patch.set_alpha(0.6)
plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
plt.ylabel('Optimality Gap (%)')
plt.title('Greedy Optimality Gap by Instance Family\n(Lower = Better; Negative = Better than DP*)', fontsize=12)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{FIGURES_DIR}/greedy_gap.png')
plt.close()

# ══════════════════════════════════════════════════════════════════
# FIGURE 3: B&B Nodes Explored - Boxplot (log scale)
# ══════════════════════════════════════════════════════════════════
bb = df[df['algorithm'] == 'BranchAndBound']
plt.figure(figsize=(9, 5))
node_data = [bb[bb['dataset_type'] == fam]['nodes_explored'].values for fam in families]
bp = plt.boxplot(node_data, labels=[family_short[f] for f in families],
                 patch_artist=True, showfliers=True, flierprops={'markersize': 3})
for patch in bp['boxes']:
    patch.set_facecolor(colors['BranchAndBound'])
    patch.set_alpha(0.6)
plt.yscale('log')
plt.ylabel('Nodes Explored (log scale)')
plt.title('Branch & Bound Search Effort by Instance Family', fontsize=12)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{FIGURES_DIR}/bb_nodes.png')
plt.close()

# ══════════════════════════════════════════════════════════════════
# FIGURE 4: Time at max n - Grouped Bar Chart
# ══════════════════════════════════════════════════════════════════
max_n = df['n'].max()
nmax = df[df['n'] == max_n]
x = np.arange(len(families))
width = 0.25

fig, ax = plt.subplots(figsize=(10, 5))
for i, algo in enumerate(algorithms):
    means = [nmax[(nmax['algorithm'] == algo) & (nmax['dataset_type'] == fam)]['time_millis'].mean() for fam in families]
    stds = [nmax[(nmax['algorithm'] == algo) & (nmax['dataset_type'] == fam)]['time_millis'].std() for fam in families]
    bars = ax.bar(x + i*width, means, width, label=algo, color=colors[algo],
                  edgecolor='white', linewidth=0.5, yerr=stds, capsize=3)

ax.set_yscale('log')
ax.set_ylabel('Time (ms, log scale)')
ax.set_title(f'Execution Time at n={max_n} by Algorithm and Instance Family')
ax.set_xticks(x + width)
ax.set_xticklabels([family_short[f] for f in families])
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{FIGURES_DIR}/time_n{max_n}.png')
plt.close()

# ══════════════════════════════════════════════════════════════════
# FIGURE 5: Greedy Gap vs n - Line plot per family
# ══════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharey=True)
axes = axes.flatten()

for idx, fam in enumerate(families):
    ax = axes[idx]
    sub = greedy[greedy['dataset_type'] == fam].groupby('n')['gap_pct'].agg(['mean', 'std']).reset_index()
    if len(sub) == 0:
        continue
    ax.plot(sub['n'], sub['mean'], 'o-', color=colors['Greedy'], linewidth=2, markersize=6)
    ax.fill_between(sub['n'], sub['mean'] - sub['std'], sub['mean'] + sub['std'],
                    color=colors['Greedy'], alpha=0.2)
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    ax.set_xscale('log')
    ax.set_xlabel('n')
    if idx % 3 == 0:
        ax.set_ylabel('Gap (%)')
    ax.set_title(family_short[fam], fontweight='bold')
    ax.grid(True, alpha=0.3)

fig.delaxes(axes[5])
fig.suptitle('Greedy Optimality Gap vs Problem Size by Instance Family', y=1.02, fontsize=14)
plt.tight_layout()
plt.savefig(f'{FIGURES_DIR}/gap_vs_n.png')
plt.close()

# ══════════════════════════════════════════════════════════════════
# FIGURE 6: Memory Usage at max n
# ══════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))
for i, algo in enumerate(algorithms):
    means = [nmax[(nmax['algorithm'] == algo) & (nmax['dataset_type'] == fam)]['memory_mb'].mean() for fam in families]
    bars = ax.bar(x + i*width, means, width, label=algo, color=colors[algo],
                  edgecolor='white', linewidth=0.5)

ax.set_ylabel('Memory (MB)')
ax.set_title(f'Memory Usage at n={max_n} by Algorithm and Instance Family')
ax.set_xticks(x + width)
ax.set_xticklabels([family_short[f] for f in families])
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{FIGURES_DIR}/memory_n{max_n}.png')
plt.close()

# ══════════════════════════════════════════════════════════════════
# LATEX TABLES
# ══════════════════════════════════════════════════════════════════
def write_latex_table(filename, header, rows, caption, label):
    with open(f'{TABLES_DIR}/{filename}', 'w') as f:
        f.write('\\begin{table}[tb]\n')
        f.write('\\centering\n')
        f.write(f'\\caption{{{caption}}}\n')
        f.write(f'\\label{{{label}}}\n')
        f.write(f'\\begin{{tabular}}{{{"l" + "c" * len(header)}}}\n')
        f.write('\\toprule\n')
        f.write(' & '.join(header) + ' \\\\\n')
        f.write('\\midrule\n')
        for row in rows:
            f.write(' & '.join(str(c) for c in row) + ' \\\\\n')
        f.write('\\bottomrule\n')
        f.write('\\end{tabular}\n')
        f.write('\\end{table}\n')

# Table 1: Time at max n
rows = []
for algo in algorithms:
    row = [algo]
    for fam in families:
        vals = nmax[(nmax['algorithm'] == algo) & (nmax['dataset_type'] == fam)]['time_millis']
        row.append(f"{vals.mean():.2f} $\\pm$ {vals.std():.2f}")
    rows.append(row)
write_latex_table('table_time_nmax.tex',
    ['Algorithm'] + [family_short[f] for f in families],
    rows,
    f'Mean execution time (ms) at $n={max_n}$ ($W=1000$)',
    'tab:time-nmax')

# Table 2: Greedy Gap Summary
rows = []
for fam in families:
    gaps = greedy[greedy['dataset_type'] == fam]['gap_pct']
    med = gaps.median()
    mean = gaps.mean()
    std = gaps.std()
    rows.append([family_short[fam], f"{med:.1f}", f"{mean:.1f} $\\pm$ {std:.1f}"])
write_latex_table('table_greedy_gap.tex',
    ['Family', 'Median Gap (\%)', 'Mean $\\pm$ Std'],
    rows,
    'Greedy optimality gap statistics (DP as ground truth)',
    'tab:greedy-gap')

# Table 3: B&B Nodes Summary
rows = []
for fam in families:
    nodes = bb[bb['dataset_type'] == fam]['nodes_explored']
    rows.append([family_short[fam], f"{nodes.median():.0f}", f"{nodes.min():.0f}", f"{nodes.max():.0f}"])
write_latex_table('table_bb_nodes.tex',
    ['Family', 'Median', 'Min', 'Max'],
    rows,
    'Branch \\& Bound nodes explored (all $n$ pooled)',
    'tab:bb-nodes')

# Table 4: DP Scaling (shows pseudo-polynomial O(nW))
rows = []
for n in sorted(df['n'].unique()):
    row = [str(n)]
    for fam in families:
        vals = df[(df['algorithm'] == 'DynamicProgramming') & 
                  (df['dataset_type'] == fam) & (df['n'] == n)]['time_millis']
        row.append(f"{vals.mean():.2f}")
    rows.append(row)
write_latex_table('table_dp_scaling.tex',
    ['$n$'] + [family_short[f] for f in families],
    rows,
    'DP mean time (ms) by $n$ and family ($W=1000$ fixed)',
    'tab:dp-scaling')

# Table 5: Overall Summary (all n, median)
rows = []
for algo in algorithms:
    for fam in families:
        vals = df[(df['algorithm'] == algo) & (df['dataset_type'] == fam)]['time_millis']
        if len(vals) > 0:
            rows.append([algo, family_short[fam], f"{vals.median():.3f}"])
write_latex_table('table_summary.tex',
    ['Algorithm', 'Family', 'Median Time (ms)'],
    rows,
    'Median execution time (ms) across all problem sizes',
    'tab:summary')

print(f"\n✅ Analysis complete!")
print(f"Figures saved to {FIGURES_DIR}/")
print(f"Tables saved to {TABLES_DIR}/")
print(f"\nFiles:")
for d in [FIGURES_DIR, TABLES_DIR]:
    for f in sorted(os.listdir(d)):
        print(f"  {d}/{f}")