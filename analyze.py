#!/usr/bin/env python3
"""
Canonical analysis pipeline for the Knapsack Empirical Comparison.

Reads the experimental CSV produced by BenchmarkRunner and generates:
  - LaTeX tables with 95% bootstrap confidence intervals (tables/*.tex)
  - Publication-quality figures in PDF, PNG, and SVG (figures/*)
  - A CSV summary of all results (tables/table_full_summary.csv)

Uses only the Python standard library (no pip dependencies).
The figure generation (figures.py) additionally requires numpy and matplotlib.

Usage:
  python3 analyze.py [path/to/full_experiment.csv]

If no path is given, reads out/results/full_experiment.csv.
"""

import csv
import glob
import math
import os
import sys
import statistics
from collections import defaultdict
import random

# Import figure generation
from figures import generate_all_figures

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

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

# ─── Statistical Helpers ────────────────────────────────────────
def bootstrap_ci(data, n_bootstrap=10000, confidence=0.95, statistic=statistics.mean):
    """Compute bootstrap confidence interval."""
    if len(data) < 2:
        return (data[0], data[0]) if data else (0, 0)
    stats = []
    n = len(data)
    for _ in range(n_bootstrap):
        sample = [data[i] for i in [int(random.random() * n) for _ in range(n)]]
        stats.append(statistic(sample))
    stats.sort()
    alpha = (1 - confidence) / 2
    lower = stats[int(alpha * n_bootstrap)]
    upper = stats[int((1 - alpha) * n_bootstrap)]
    return (lower, upper)

def bootstrap_median_ci(data, n_bootstrap=10000, confidence=0.95):
    """Compute bootstrap confidence interval for the median."""
    if len(data) < 2:
        return (data[0], data[0]) if data else (0, 0)
    medians = []
    n = len(data)
    for _ in range(n_bootstrap):
        sample = [data[i] for i in [int(random.random() * n) for _ in range(n)]]
        sample.sort()
        medians.append(sample[len(sample)//2])
    medians.sort()
    alpha = (1 - confidence) / 2
    lower = medians[int(alpha * n_bootstrap)]
    upper = medians[int((1 - alpha) * n_bootstrap)]
    return (lower, upper)

# ─── Load Data ──────────────────────────────────────────────────
print(f"Loading {CSV_FILE}...")
rows = []
with open(CSV_FILE, 'r') as f:
    reader = csv.DictReader(f)
    for r in reader:
        r['time_ms'] = float(r['time_millis'])
        r['memory_mb'] = float(r['memory_mb'])
        r['solution_value'] = int(r['solution_value'])
        r['optimal_value'] = int(r['optimal_value']) if r['optimal_value'] else None
        r['optimality_gap'] = float(r['optimality_gap']) if r['optimality_gap'] else None
        r['nodes_explored'] = int(r['nodes_explored'])
        r['n'] = int(r['n'])
        r['instance_id'] = int(r['instance_id'])
        rows.append(r)

print(f"Loaded {len(rows)} rows")

# Split by algorithm
greedy_rows = [r for r in rows if r['algorithm'] == 'Greedy']
dp_rows = {r['instance_id']: r for r in rows if r['algorithm'] == 'DynamicProgramming'}
bb_rows = [r for r in rows if r['algorithm'] == 'BranchAndBound']

# Compute greedy gap using DP as ground truth
for r in greedy_rows:
    inst_id = r['instance_id']
    if inst_id in dp_rows:
        opt = dp_rows[inst_id]['solution_value']
        if opt > 0:
            r['gap_pct'] = (opt - r['solution_value']) / opt * 100
        else:
            r['gap_pct'] = 0

ns = sorted(set(r['n'] for r in rows))

# ─── Helper: Write LaTeX Table ─────────────────────────────────
def write_latex_table(filename, header, rows, caption, label):
    with open(os.path.join(TABLES_DIR, filename), 'w') as f:
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

# ─── TABLE 1: Time at n=500 (or max n) with 95% CI ──────────────────────────
max_n = max(ns)
print(f"\nGenerating Table 1: Time at n={max_n}...")
table1_rows = []
for algo in algorithms:
    row = [algo]
    for fam in families:
        subset = [r for r in rows if r['algorithm'] == algo and r['dataset_type'] == fam and r['n'] == max_n]
        if subset:
            times = [r['time_ms'] for r in subset]
            mean_t = statistics.mean(times)
            std_t = statistics.stdev(times) if len(times) > 1 else 0
            ci = bootstrap_ci(times, n_bootstrap=5000)
            row.append(f"{mean_t:.2f} (CI: {ci[0]:.2f}–{ci[1]:.2f})")
        else:
            row.append('---')
    table1_rows.append(row)

write_latex_table('table_time_n500.tex',
    ['Algorithm'] + [family_short[f] for f in families],
    table1_rows,
    f'Mean execution time (ms) at $n={max_n}$ ($W=1000$, 30 seeds) with 95\\% bootstrap CI',
    'tab:time-n500')

# ─── TABLE 2: Greedy Gap Summary with percentiles ────────────────
print("Generating Table 2: Greedy optimality gap...")
table2_rows = []
for fam in families:
    gaps = [r.get('gap_pct', 0) for r in greedy_rows if r['dataset_type'] == fam]
    if gaps:
        gaps_sorted = sorted(gaps)
        med = gaps_sorted[len(gaps_sorted)//2]
        mean = statistics.mean(gaps)
        std = statistics.stdev(gaps) if len(gaps) > 1 else 0
        p95 = gaps_sorted[int(0.95 * len(gaps_sorted))]
        med_ci = bootstrap_median_ci(gaps, n_bootstrap=5000)
        table2_rows.append([family_short[fam], f"{med:.1f} (CI: {med_ci[0]:.1f}–{med_ci[1]:.1f})", f"{mean:.1f} ± {std:.1f}", f"{p95:.1f}", f"{max(gaps):.1f}"])
    else:
        table2_rows.append([family_short[fam], '---', '---', '---', '---'])

write_latex_table('table_greedy_gap.tex',
    ['Family', 'Median Gap (\\%) [95\\% CI]', 'Mean ± Std (\\%)', '95th Pctl (\\%)', 'Max (\\%)'],
    table2_rows,
    'Greedy optimality gap statistics (all $n$ pooled, DP as ground truth)',
    'tab:greedy-gap')

# ─── TABLE 3: B&B Nodes Summary with CI ──────────────────────────
print("Generating Table 3: B&B nodes explored...")
table3_rows = []
for fam in families:
    nodes = [r['nodes_explored'] for r in bb_rows if r['dataset_type'] == fam]
    if nodes:
        nodes_sorted = sorted(nodes)
        med = nodes_sorted[len(nodes_sorted)//2]
        med_ci = bootstrap_median_ci(nodes, n_bootstrap=5000)
        table3_rows.append([family_short[fam], f"{med:.0f} (CI: {med_ci[0]:.0f}–{med_ci[1]:.0f})", f"{min(nodes):.0f}", f"{max(nodes):.0f}"])
    else:
        table3_rows.append([family_short[fam], '---', '---', '---'])

write_latex_table('table_bb_nodes.tex',
    ['Family', 'Median Nodes [95\\% CI]', 'Min', 'Max'],
    table3_rows,
    'Branch $\\&$ Bound nodes explored (all $n$ pooled)',
    'tab:bb-nodes')

# ─── TABLE 4: DP Scaling with n ──────────────────────────────────
print("Generating Table 4: DP time scaling...")
table4_rows = []
for n in ns:
    row = [str(n)]
    for fam in families:
        subset = [r for r in rows if r['algorithm'] == 'DynamicProgramming' and r['dataset_type'] == fam and r['n'] == n]
        if subset:
            times = [r['time_ms'] for r in subset]
            mean_t = statistics.mean(times)
            ci = bootstrap_ci(times, n_bootstrap=5000)
            row.append(f"{mean_t:.2f} (CI: {ci[0]:.2f}–{ci[1]:.2f})")
        else:
            row.append('---')
    table4_rows.append(row)

write_latex_table('table_dp_scaling.tex',
    ['$n$'] + [family_short[f] for f in families],
    table4_rows,
    'DP mean time (ms) by $n$ and family ($W=1000$ fixed) with 95\\% bootstrap CI',
    'tab:dp-scaling')

# ─── TABLE 5: B&B Time at n=500 with CI (highlighting outlier) ──
print("Generating Table 5: B&B time at n=500 with outlier analysis...")
table5_rows = []
for fam in families:
    subset = [r for r in bb_rows if r['dataset_type'] == fam and r['n'] == max_n]
    if subset:
        times = [r['time_ms'] for r in subset]
        mean_t = statistics.mean(times)
        med_t = statistics.median(times)
        std_t = statistics.stdev(times) if len(times) > 1 else 0
        ci_mean = bootstrap_ci(times, n_bootstrap=5000)
        ci_med = bootstrap_median_ci(times, n_bootstrap=5000)
        table5_rows.append([family_short[fam], f"{med_t:.2f} (CI: {ci_med[0]:.2f}–{ci_med[1]:.2f})", f"{mean_t:.2f} ± {std_t:.2f}", f"{ci_mean[0]:.2f}–{ci_mean[1]:.2f}", f"{max(times):.2f}"])
    else:
        table5_rows.append([family_short[fam], '---', '---', '---', '---'])

write_latex_table('table_bb_time_n500.tex',
    ['Family', 'Median [95\\% CI]', 'Mean ± Std', 'Mean 95\\% CI', 'Max'],
    table5_rows,
    'Branch $\\&$ Bound execution time (ms) at $n=500$ with outlier analysis',
    'tab:bb-time-n500')

# ─── TABLE 6: Full Summary ───────────────────────────────────────
print("Generating Table 6: Full summary...")
table6_rows = []
for n in ns:
    for algo in algorithms:
        for fam in families:
            subset = [r for r in rows if r['algorithm'] == algo and r['dataset_type'] == fam and r['n'] == n]
            if subset:
                times = [r['time_ms'] for r in subset]
                mems = [r['memory_mb'] for r in subset]
                time_med = statistics.median(times)
                mem_med = statistics.median(mems)
                if algo == 'Greedy':
                    gaps = [r.get('gap_pct', 0) for r in subset if 'gap_pct' in r]
                    gap_str = f"{statistics.mean(gaps):.2f}" if gaps else '---'
                    nodes_str = '---'
                elif algo == 'BranchAndBound':
                    nodes = [r['nodes_explored'] for r in subset]
                    nodes_str = f"{statistics.median(nodes):.0f}"
                    gap_str = '---'
                else:
                    gap_str = '---'
                    nodes_str = '---'
                table6_rows.append([str(n), algo, family_short[fam], f"{time_med:.2f}", f"{mem_med:.2f}", gap_str, nodes_str])

with open(os.path.join(TABLES_DIR, 'table_full_summary.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['n', 'Algorithm', 'Family', 'Time_ms_median', 'Mem_MB_median', 'Gap_pct_mean', 'Nodes_median'])
    writer.writerows(table6_rows)

# ─── TEXT SUMMARY TABLES ─────────────────────────────────────────
print("\n=== TEXT SUMMARY TABLES ===")

print(f"\n--- Time (ms) at n={max_n} with 95% CI ---")
print(f"{'Algorithm':>20} | " + " | ".join(f"{family_short[f]:>30}" for f in families))
print("-" * 160)
for row in table1_rows:
    print(f"{row[0]:>20} | " + " | ".join(f"{c:>30}" for c in row[1:]))

print("\n--- Greedy Gap (%) with CI ---")
print(f"{'Family':>15} | {'Median [95% CI]':>20} | {'Mean±Std':>12} | {'95th Pctl':>10} | {'Max':>8}")
print("-" * 75)
for row in table2_rows:
    print(f"{row[0]:>15} | {row[1]:>20} | {row[2]:>12} | {row[3]:>10} | {row[4]:>8}")

print("\n--- B&B Nodes with CI ---")
print(f"{'Family':>15} | {'Median [95% CI]':>20} | {'Min':>8} | {'Max':>12}")
print("-" * 65)
for row in table3_rows:
    print(f"{row[0]:>15} | {row[1]:>20} | {row[2]:>8} | {row[3]:>12}")

print("\n--- B&B Time at n=500 with Outlier Analysis ---")
print(f"{'Family':>15} | {'Median [95% CI]':>20} | {'Mean±Std':>14} | {'Mean 95% CI':>18} | {'Max':>10}")
print("-" * 90)
for row in table5_rows:
    print(f"{row[0]:>15} | {row[1]:>20} | {row[2]:>14} | {row[3]:>18} | {row[4]:>10}")

print("\n--- DP Time by n with CI ---")
print(f"{'n':>4} | " + " | ".join(f"{family_short[f]:>28}" for f in families))
print("-" * 160)
for row in table4_rows:
    print(f"{row[0]:>4} | " + " | ".join(f"{c:>28}" for c in row[1:]))

# ─── FIGURE GENERATION ─────────────────────────────────────────────
print("\n=== GENERATING FIGURES ===")
figures_generated = generate_all_figures(
    rows, greedy_rows, bb_rows,
    families, algorithms,
    FIGURES_DIR, max_n, ns, table4_rows
)

print(f"\n✅ Analysis complete!")
print(f"LaTeX tables saved to {TABLES_DIR}/")
print(f"CSV summary saved to {TABLES_DIR}/table_full_summary.csv")
print(f"Figures saved to {FIGURES_DIR}/")
print(f"\nFiles generated:")
for f in sorted(os.listdir(TABLES_DIR)):
    print(f"  {TABLES_DIR}/{f}")
for f in sorted(figures_generated):
    print(f"  {FIGURES_DIR}/{f}")