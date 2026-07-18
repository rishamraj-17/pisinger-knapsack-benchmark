#!/usr/bin/env python3
"""
Canonical analysis pipeline for the Knapsack Empirical Comparison.

Reads the experimental CSV produced by BenchmarkRunner and generates:
  - LaTeX tables with 95% bootstrap confidence intervals (tables/*.tex)
  - Publication-quality figures in PDF, PNG, and SVG (figures/fixed/pdf/, figures/fixed/png/, figures/fixed/svg/, figures/scaled/pdf/, figures/scaled/png/, figures/scaled/svg/)
  - A CSV summary of all results (tables/table_full_summary.csv)

Table generation uses only the Python standard library.
Figure generation (figures.py) requires numpy and matplotlib.

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

# --- Configuration ---
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

random.seed(42)

# --- Statistical Helpers ---
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
        m = len(sample)
        if m % 2 == 0:
            medians.append((sample[m // 2 - 1] + sample[m // 2]) / 2.0)
        else:
            medians.append(sample[m // 2])
    medians.sort()
    alpha = (1 - confidence) / 2
    lower = medians[int(alpha * n_bootstrap)]
    upper = medians[int((1 - alpha) * n_bootstrap)]
    return (lower, upper)

# --- Load Data ---
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
        r['nodes_pruned'] = int(r.get('nodes_pruned', 0) or 0)
        r['max_queue_size'] = int(r.get('max_queue_size', 0) or 0)
        r['capacity_mode'] = r.get('capacity_mode', 'fixed')
        rows.append(r)

print(f"Loaded {len(rows)} rows")

# Split by capacity mode
fixed_rows = [r for r in rows if r['capacity_mode'] == 'fixed']
scaled_rows = [r for r in rows if r['capacity_mode'] == 'scaled']

print(f"  Fixed capacity: {len(fixed_rows)} rows")
print(f"  Scaled capacity: {len(scaled_rows)} rows")

def analyze_dataset(dataset_rows, label, output_prefix):
    """Run full analysis on a dataset (fixed or scaled)."""
    print(f"\n{'='*60}")
    print(f"  Analyzing: {label} ({len(dataset_rows)} rows)")
    print(f"{'='*60}")

    # Split by algorithm
    greedy_rows = [r for r in dataset_rows if r['algorithm'] == 'Greedy']
    dp_rows = {r['instance_id']: r for r in dataset_rows if r['algorithm'] == 'DynamicProgramming'}
    bb_rows = [r for r in dataset_rows if r['algorithm'] == 'BranchAndBound']

    # Compute greedy gap using DP as ground truth
    for r in greedy_rows:
        inst_id = r['instance_id']
        if inst_id in dp_rows:
            opt = dp_rows[inst_id]['solution_value']
            if opt > 0:
                r['gap_pct'] = (opt - r['solution_value']) / opt * 100
            else:
                r['gap_pct'] = 0

    ns = sorted(set(r['n'] for r in dataset_rows))
    max_n = max(ns)

    # --- TABLE 1: Time at max_n with 95% CI ---
    print(f"\nGenerating {output_prefix}_table1: Time at n={max_n}...")
    table1_rows = []
    for algo in algorithms:
        row = [algo]
        for fam in families:
            subset = [r for r in dataset_rows if r['algorithm'] == algo and r['dataset_type'] == fam and r['n'] == max_n]
            if subset:
                times = [r['time_ms'] for r in subset]
                mean_t = statistics.mean(times)
                ci = bootstrap_ci(times, n_bootstrap=5000)
                row.append(f"{mean_t:.2f} (CI: {ci[0]:.2f}–{ci[1]:.2f})")
            else:
                row.append('---')
        table1_rows.append(row)

    write_latex_table(f'{output_prefix}_table_time_max_n.tex',
        ['Algorithm'] + [family_short[f] for f in families],
        table1_rows,
        f'Mean execution time (ms) at $n={max_n}$ ({label}) with 95\\% bootstrap CI',
        f'tab:{output_prefix}-time-max-n')

    # --- TABLE 2: Greedy Gap Summary ---
    print(f"Generating {output_prefix}_table2: Greedy optimality gap...")
    table2_rows = []
    for fam in families:
        gaps = [r.get('gap_pct', 0) for r in greedy_rows if r['dataset_type'] == fam]
        if gaps:
            gaps_sorted = sorted(gaps)
            m = len(gaps_sorted)
            if m % 2 == 0:
                med = (gaps_sorted[m // 2 - 1] + gaps_sorted[m // 2]) / 2.0
            else:
                med = gaps_sorted[m // 2]
            mean = statistics.mean(gaps)
            std = statistics.stdev(gaps) if len(gaps) > 1 else 0
            p95 = gaps_sorted[int(0.95 * len(gaps_sorted))]
            med_ci = bootstrap_median_ci(gaps, n_bootstrap=5000)
            table2_rows.append([family_short[fam], f"{med:.1f} (CI: {med_ci[0]:.1f}–{med_ci[1]:.1f})", f"{mean:.1f} ± {std:.1f}", f"{p95:.1f}", f"{max(gaps):.1f}"])
        else:
            table2_rows.append([family_short[fam], '---', '---', '---', '---'])

    write_latex_table(f'{output_prefix}_table_greedy_gap.tex',
        ['Family', 'Median Gap (\\%) [95\\% CI]', 'Mean ± Std (\\%)', '95th Pctl (\\%)', 'Max (\\%)'],
        table2_rows,
        f'Greedy optimality gap statistics ({label}, all $n$ pooled, DP as ground truth)',
        f'tab:{output_prefix}-greedy-gap')

    # --- TABLE 3: B&B Nodes Summary ---
    print(f"Generating {output_prefix}_table3: B&B nodes explored...")
    table3_rows = []
    for fam in families:
        nodes = [r['nodes_explored'] for r in bb_rows if r['dataset_type'] == fam]
        if nodes:
            nodes_sorted = sorted(nodes)
            m = len(nodes_sorted)
            if m % 2 == 0:
                med = (nodes_sorted[m // 2 - 1] + nodes_sorted[m // 2]) / 2.0
            else:
                med = nodes_sorted[m // 2]
            med_ci = bootstrap_median_ci(nodes, n_bootstrap=5000)
            table3_rows.append([family_short[fam], f"{med:.0f} (CI: {med_ci[0]:.0f}–{med_ci[1]:.0f})", f"{min(nodes):.0f}", f"{max(nodes):.0f}"])
        else:
            table3_rows.append([family_short[fam], '---', '---', '---'])

    write_latex_table(f'{output_prefix}_table_bb_nodes.tex',
        ['Family', 'Median Nodes [95\\% CI]', 'Min', 'Max'],
        table3_rows,
        f'Branch $\\&$ Bound nodes explored ({label}, all $n$ pooled)',
        f'tab:{output_prefix}-bb-nodes')

    # --- TABLE 4: DP Scaling with n ---
    print(f"Generating {output_prefix}_table4: DP time scaling...")
    table4_rows = []
    for n in ns:
        row = [str(n)]
        for fam in families:
            subset = [r for r in dataset_rows if r['algorithm'] == 'DynamicProgramming' and r['dataset_type'] == fam and r['n'] == n]
            if subset:
                times = [r['time_ms'] for r in subset]
                mean_t = statistics.mean(times)
                ci = bootstrap_ci(times, n_bootstrap=5000)
                row.append(f"{mean_t:.2f} (CI: {ci[0]:.2f}–{ci[1]:.2f})")
            else:
                row.append('---')
        table4_rows.append(row)

    write_latex_table(f'{output_prefix}_table_dp_scaling.tex',
        ['$n$'] + [family_short[f] for f in families],
        table4_rows,
        f'DP mean time (ms) by $n$ and family ({label}) with 95\\% bootstrap CI',
        f'tab:{output_prefix}-dp-scaling')

    # --- TABLE 5: B&B Time at max_n with outlier analysis ---
    print(f"Generating {output_prefix}_table5: B&B time at n={max_n}...")
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

    write_latex_table(f'{output_prefix}_table_bb_time.tex',
        ['Family', 'Median [95\\% CI]', 'Mean ± Std', 'Mean 95\\% CI', 'Max'],
        table5_rows,
        f'Branch $\\&$ Bound execution time (ms) at $n={max_n}$ ({label})',
        f'tab:{output_prefix}-bb-time')

    # --- TABLE 6: B&B Pruning Analysis ---
    print(f"Generating {output_prefix}_table6: B&B pruning analysis...")
    table6_rows = []
    for fam in families:
        fam_bb = [r for r in bb_rows if r['dataset_type'] == fam]
        if fam_bb:
            total_explored = [r['nodes_explored'] for r in fam_bb]
            total_pruned = [r['nodes_pruned'] for r in fam_bb]
            max_queue = [r['max_queue_size'] for r in fam_bb]

            med_explored = statistics.median(total_explored)
            med_pruned = statistics.median(total_pruned)
            med_queue = statistics.median(max_queue)

            # Pruning ratio: pruned / (explored + pruned) for each instance
            pruning_ratios = []
            for r in fam_bb:
                total = r['nodes_explored'] + r['nodes_pruned']
                if total > 0:
                    pruning_ratios.append(r['nodes_pruned'] / total * 100)
            med_pruning = statistics.median(pruning_ratios) if pruning_ratios else 0

            table6_rows.append([
                family_short[fam],
                f"{med_explored:.0f}",
                f"{med_pruned:.0f}",
                f"{med_pruning:.1f}%",
                f"{med_queue:.0f}"
            ])
        else:
            table6_rows.append([family_short[fam], '---', '---', '---', '---'])

    write_latex_table(f'{output_prefix}_table_bb_pruning.tex',
        ['Family', 'Median Explored', 'Median Pruned', 'Median Pruning \\%', 'Median Max Queue'],
        table6_rows,
        f'Branch $\\&$ Bound pruning analysis ({label}, all $n$ pooled)',
        f'tab:{output_prefix}-bb-pruning')

    # --- TABLE 7: Full Summary CSV ---
    print(f"Generating {output_prefix}_table7: Full summary...")
    table7_rows = []
    for n in ns:
        for algo in algorithms:
            for fam in families:
                subset = [r for r in dataset_rows if r['algorithm'] == algo and r['dataset_type'] == fam and r['n'] == n]
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
                    table7_rows.append([str(n), algo, family_short[fam], f"{time_med:.2f}", f"{mem_med:.2f}", gap_str, nodes_str])

    with open(os.path.join(TABLES_DIR, f'{output_prefix}_table_full_summary.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n', 'Algorithm', 'Family', 'Time_ms_median', 'Mem_MB_median', 'Gap_pct_mean', 'Nodes_median'])
        writer.writerows(table7_rows)

    # --- TEXT SUMMARY ---
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

    print("\n--- B&B Pruning Analysis ---")
    print(f"{'Family':>15} | {'Med Explored':>12} | {'Med Pruned':>12} | {'Pruning %':>10} | {'Max Queue':>10}")
    print("-" * 65)
    for row in table6_rows:
        print(f"{row[0]:>15} | {row[1]:>12} | {row[2]:>12} | {row[3]:>10} | {row[4]:>10}")

    return {
        'max_n': max_n,
        'ns': ns,
        'table4_rows': table4_rows,
        'greedy_rows': greedy_rows,
        'bb_rows': bb_rows,
    }


# --- Write LaTeX Table ---
def write_latex_table(filename, header, rows, caption, label):
    with open(os.path.join(TABLES_DIR, filename), 'w') as f:
        f.write('\\begin{table}[tb]\n')
        f.write('\\centering\n')
        f.write(f'\\caption{{{caption}}}\n')
        f.write(f'\\label{{{label}}}\n')
        f.write(f'\\begin{{tabular}}{{{"l" + "c" * (len(header) - 1)}}}\n')
        f.write('\\toprule\n')
        f.write(' & '.join(header) + ' \\\\\n')
        f.write('\\midrule\n')
        for row in rows:
            f.write(' & '.join(str(c) for c in row) + ' \\\\\n')
        f.write('\\bottomrule\n')
        f.write('\\end{tabular}\n')
        f.write('\\end{table}\n')


# --- Run analysis for each capacity mode ---
fixed_results = analyze_dataset(fixed_rows, 'Fixed Capacity (W=1000)', 'fixed')
scaled_results = analyze_dataset(scaled_rows, 'Scaled Capacity (W=0.5*sum)', 'scaled')

# --- FIGURE GENERATION ---
print("\n=== GENERATING FIGURES ===")

# Generate figures for fixed capacity
print("\n--- Fixed capacity figures ---")
figures_fixed = generate_all_figures(
    fixed_rows,
    fixed_results['greedy_rows'],
    fixed_results['bb_rows'],
    families, algorithms,
    os.path.join(FIGURES_DIR, 'fixed'),
    fixed_results['max_n'],
    fixed_results['ns'],
    fixed_results['table4_rows']
)

# Generate figures for scaled capacity
print("\n--- Scaled capacity figures ---")
figures_scaled = generate_all_figures(
    scaled_rows,
    scaled_results['greedy_rows'],
    scaled_results['bb_rows'],
    families, algorithms,
    os.path.join(FIGURES_DIR, 'scaled'),
    scaled_results['max_n'],
    scaled_results['ns'],
    scaled_results['table4_rows']
)

print(f"\n{'='*60}")
print(f"Analysis complete!")
print(f"{'='*60}")
print(f"LaTeX tables saved to {TABLES_DIR}/")
print(f"Figures saved to {FIGURES_DIR}/fixed/ and {FIGURES_DIR}/scaled/")
print(f"\nFiles generated:")
for f in sorted(os.listdir(TABLES_DIR)):
    print(f"  {TABLES_DIR}/{f}")
