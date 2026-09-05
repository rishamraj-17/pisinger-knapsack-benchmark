#!/usr/bin/env python3
"""
Phase 3.1 — Exploratory Data Analysis (EDA)

Reads the canonical dataset (data/raw/canonical_dataset.csv), performs
descriptive-only analysis of all 110 columns, and produces summary tables,
correlation matrices, distribution plots, and boxplots.

This phase is strictly descriptive. No regression, hypothesis testing,
feature importance, or predictive modeling is performed.

Outputs:
  outputs/eda/summary_statistics.csv
  outputs/eda/missing_values.csv
  outputs/eda/duplicate_rows.csv
  outputs/eda/correlation_matrix.csv
  outputs/eda/correlation_heatmap.png
  outputs/eda/histograms/*.png        (one per numeric column)
  outputs/eda/boxplots/*.png          (one per outcome + key metric)
  outputs/eda/column_categories.txt

Usage:
  python3 eda_phase3_1.py
"""

import csv
import math
import os
import sys
import statistics
from collections import defaultdict, Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ─── Project imports (shared styling) ────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_utils import (
    setup_publication_style, FAM_COLORS, ALGO_COLORS,
    get_fam_short, get_algo_color,
)

# ─── Paths ─────────────────────────────────────────────────────────────
CSV_PATH = 'data/raw/canonical_dataset.csv'
OUT_DIR = 'outputs/eda'
HIST_DIR = os.path.join(OUT_DIR, 'histograms')
BOX_DIR  = os.path.join(OUT_DIR, 'boxplots')

os.makedirs(HIST_DIR, exist_ok=True)
os.makedirs(BOX_DIR,  exist_ok=True)

setup_publication_style()

# ═══════════════════════════════════════════════════════════════════════
# 1.  LOAD DATA
# ═══════════════════════════════════════════════════════════════════════
print("=" * 65)
print("  Phase 3.1 — Exploratory Data Analysis")
print("=" * 65)

print(f"\nReading {CSV_PATH} ...")
with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    raw_headers = reader.fieldnames
    raw_rows = list(reader)

n_rows = len(raw_rows)
n_cols = len(raw_headers)
print(f"\n  Rows:     {n_rows}")
print(f"  Columns:  {n_cols}")

# Verify expected dimensions
EXPECTED_ROWS = 18_000
EXPECTED_COLS = 110
assert n_rows == EXPECTED_ROWS, f"Row count mismatch: {n_rows} vs {EXPECTED_ROWS}"
assert n_cols == EXPECTED_COLS, f"Column count mismatch: {n_cols} vs {EXPECTED_COLS}"
print("  Dimensions verified: 18,000 x 110")

# ═══════════════════════════════════════════════════════════════════════
# 2.  CATEGORIZE COLUMNS
# ═══════════════════════════════════════════════════════════════════════
IDENTIFIERS = {
    'algorithm', 'instance_id', 'n', 'family', 'capacity_mode', 'capacity', 'seed',
}

INSTANCE_CHARS = {
    'total_weight', 'total_value', 'mean_weight', 'mean_value',
    'median_weight', 'median_value', 'std_weight', 'std_value',
    'min_weight', 'max_weight', 'min_value', 'max_value',
    'weight_cv', 'value_cv', 'weight_skewness', 'value_skewness',
    'weight_kurtosis', 'value_kurtosis',
    'capacity_ratio', 'slack', 'average_fillable_items',
    'pearson_corr', 'spearman_corr', 'kendall_corr',
    'mean_ratio', 'median_ratio', 'std_ratio', 'ratio_entropy',
    'unique_ratio_count', 'duplicate_ratio_fraction',
    'unique_weights', 'unique_values', 'unique_pairs',
    'duplicate_items', 'duplicate_pairs',
}

BENCHMARK_OUTCOMES = {
    'time_nanos', 'time_millis', 'memory_bytes', 'memory_mb',
    'solution_value', 'optimal_value', 'optimality_gap',
    'nodes_explored', 'nodes_pruned', 'max_queue_size', 'optimal',
}

BB_METRICS = {
    'nodes_generated', 'leaf_nodes', 'internal_nodes',
    'max_depth', 'mean_depth', 'median_depth', 'min_depth',
    'depth_histogram',
    'mean_queue_size', 'final_queue_size', 'queue_histogram',
    'mean_bound', 'bound_variance', 'min_bound', 'max_bound',
    'mean_bound_gap', 'bound_gap_variance',
    'pruned_by_bound', 'pruned_by_cap',
    'left_branches', 'right_branches', 'explored_children', 'skipped_children',
    'skipped_infeasible', 'skipped_by_bound', 'skipped_by_cap',
    'improvement_count', 'sum_improvement_amount', 'mean_improvement_amount',
    'first_improvement_node', 'last_improvement_node',
    'improvement_depths', 'improvement_nodes',
    'explored_generated_ratio', 'pruned_generated_ratio', 'avg_branching_factor',
}

DP_METRICS = {
    'capacity_density', 'cells_allocated', 'total_evaluations',
    'include_count', 'exclude_count', 'tie_count', 'include_ratio',
    'nonzero_value_states', 'zero_value_states', 'fill_rate',
    'mean_cell_value', 'cell_value_variance',
    'dp_sum_improvement_amount', 'dp_mean_improvement_amount',
    'updates_per_cell',
}

GREEDY_METRICS = {
    'selected_count', 'solution_density', 'residual_capacity',
    'capacity_utilization', 'last_selected_position', 'first_skipped_position',
}

# Verify all columns are categorized
all_categorized = (IDENTIFIERS | INSTANCE_CHARS | BENCHMARK_OUTCOMES
                   | BB_METRICS | DP_METRICS | GREEDY_METRICS)
uncategorized = set(raw_headers) - all_categorized
if uncategorized:
    print(f"\n  WARNING: Uncategorized columns: {sorted(uncategorized)}")

# Build reverse lookup
col_category = {}
for c in IDENTIFIERS:        col_category[c] = 'identifier'
for c in INSTANCE_CHARS:     col_category[c] = 'instance_characteristic'
for c in BENCHMARK_OUTCOMES: col_category[c] = 'benchmark_outcome'
for c in BB_METRICS:         col_category[c] = 'bb_metric'
for c in DP_METRICS:         col_category[c] = 'dp_metric'
for c in GREEDY_METRICS:     col_category[c] = 'greedy_metric'

# Save column categories
with open(os.path.join(OUT_DIR, 'column_categories.csv'), 'w') as f:
    w = csv.writer(f)
    w.writerow(['column', 'category'])
    for h in raw_headers:
        w.writerow([h, col_category.get(h, 'unknown')])

print(f"\n  Identifiers:             {len(IDENTIFIERS)}")
print(f"  Instance characteristics: {len(INSTANCE_CHARS)}")
print(f"  Benchmark outcomes:       {len(BENCHMARK_OUTCOMES)}")
print(f"  BB execution metrics:     {len(BB_METRICS)}")
print(f"  DP execution metrics:     {len(DP_METRICS)}")
print(f"  Greedy execution metrics: {len(GREEDY_METRICS)}")

# ═══════════════════════════════════════════════════════════════════════
# 3.  TYPE INFERENCE & PARSING
# ═══════════════════════════════════════════════════════════════════════
def try_float(v):
    if v is None or v.strip() == '':
        return float('nan')
    try:
        return float(v)
    except ValueError:
        return float('nan')

def try_int(v):
    if v is None or v.strip() == '':
        return None
    try:
        return int(v)
    except ValueError:
        return None

# Determine type per column (sample all rows for strings)
numeric_cols = set()
string_cols = set()

for h in raw_headers:
    vals = [r[h] for r in raw_rows[:500]]
    real_vals = [v for v in vals if v and v.strip()]
    if not real_vals:
        string_cols.add(h)
        continue
    can_be_float = True
    for v in real_vals:
        try:
            float(v)
        except ValueError:
            can_be_float = False
            break
    if can_be_float:
        numeric_cols.add(h)
    else:
        string_cols.add(h)

# Parse full data into typed arrays (for numeric) and raw strings (for string)
parsed = {}
for h in raw_headers:
    if h in numeric_cols:
        parsed[h] = [try_float(r[h]) for r in raw_rows]
    else:
        parsed[h] = [r[h] for r in raw_rows]

# Separate columns with histogram/list content (depth_histogram, queue_histogram,
# improvement_depths, improvement_nodes) — keep as strings for now
list_like_cols = {'depth_histogram', 'queue_histogram',
                  'improvement_depths', 'improvement_nodes'}
numeric_cols -= list_like_cols
string_cols |= list_like_cols

print(f"\n  Numeric columns: {len(numeric_cols)}")
print(f"  String columns:  {len(string_cols)}")
print(f"  List-like cols:  {list_like_cols}")

# ═══════════════════════════════════════════════════════════════════════
# 4.  DESCRIPTIVE STATISTICS
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Computing descriptive statistics ---")

def describe(col_data):
    vals = [v for v in col_data if not math.isnan(v)]
    n = len(vals)
    if n == 0:
        return {'n': 0, 'mean': None, 'std': None, 'min': None,
                'p25': None, 'p50': None, 'p75': None, 'max': None,
                'skew': None, 'kurtosis': None, 'n_nonzero': 0, 'n_zero': 0}
    mean = statistics.mean(vals)
    std = statistics.stdev(vals) if n > 1 else 0.0
    sv = sorted(vals)
    p25 = sv[int(0.25 * n)]
    p50 = sv[int(0.50 * n)]
    p75 = sv[int(0.75 * n)]
    nz = sum(1 for v in vals if v != 0)
    zr = n - nz
    # Skewness (Fisher-Pearson)
    if n > 2 and std > 0:
        skew = sum((v - mean) ** 3 for v in vals) / (n * std ** 3)
    else:
        skew = None
    # Excess kurtosis
    if n > 2 and std > 0:
        kurt = sum((v - mean) ** 4 for v in vals) / (n * std ** 4) - 3.0
    else:
        kurt = None
    return {'n': n, 'mean': mean, 'std': std,
            'min': min(vals), 'p25': p25, 'p50': p50, 'p75': p75, 'max': max(vals),
            'skew': skew, 'kurtosis': kurt,
            'n_nonzero': nz, 'n_zero': zr}

stats_rows = []
for h in sorted(numeric_cols):
    d = describe(parsed[h])
    d['column'] = h
    d['cat'] = col_category.get(h, '')
    stats_rows.append(d)

with open(os.path.join(OUT_DIR, 'summary_statistics.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['column', 'category', 'n', 'mean', 'std', 'min', 'p25', 'p50',
                'p75', 'max', 'skew', 'kurtosis', 'n_nonzero', 'n_zero'])
    for r in stats_rows:
        w.writerow([r['column'], r['cat'], r['n'],
                    f"{r['mean']:.6f}" if r['mean'] is not None else '',
                    f"{r['std']:.6f}" if r['std'] is not None else '',
                    f"{r['min']:.6f}" if r['min'] is not None else '',
                    f"{r['p25']:.6f}" if r['p25'] is not None else '',
                    f"{r['p50']:.6f}" if r['p50'] is not None else '',
                    f"{r['p75']:.6f}" if r['p75'] is not None else '',
                    f"{r['max']:.6f}" if r['max'] is not None else '',
                    f"{r['skew']:.6f}" if r['skew'] is not None else '',
                    f"{r['kurtosis']:.6f}" if r['kurtosis'] is not None else '',
                    r['n_nonzero'], r['n_zero']])

print(f"  Summary statistics saved to {OUT_DIR}/summary_statistics.csv")
print(f"  Numeric columns analyzed: {len(stats_rows)}")

# Print key summary for major outcomes
for outcome_col in ['time_millis', 'memory_mb', 'solution_value', 'optimality_gap',
                    'nodes_explored', 'nodes_pruned']:
    if outcome_col in numeric_cols:
        d = describe(parsed[outcome_col])
        print(f"  {outcome_col}: n={d['n']}, mean={d['mean']:.4f}, "
              f"sd={d['std']:.4f}, median={d['p50']:.4f}, "
              f"min={d['min']:.4f}, max={d['max']:.4f}")

# ═══════════════════════════════════════════════════════════════════════
# 5.  MISSING VALUE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Missing value analysis ---")

def is_missing(val):
    if val is None or (isinstance(val, str) and val.strip() == ''):
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    return False

missing_rows = []
for h in raw_headers:
    if h in numeric_cols:
        miss_count = sum(1 for v in parsed[h] if math.isnan(v))
    else:
        miss_count = sum(1 for v in parsed[h] if is_missing(v))
    if miss_count > 0:
        missing_rows.append({'column': h, 'missing_count': miss_count,
                             'missing_pct': 100.0 * miss_count / n_rows,
                             'cat': col_category.get(h, '')})

with open(os.path.join(OUT_DIR, 'missing_values.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['column', 'category', 'missing_count', 'missing_pct'])
    for r in missing_rows:
        w.writerow([r['column'], r['cat'], r['missing_count'],
                    f"{r['missing_pct']:.4f}"])
    # Also write zero-missing columns for completeness
    for h in raw_headers:
        if h not in {r['column'] for r in missing_rows}:
            w.writerow([h, col_category.get(h, ''), 0, '0.0000'])

if missing_rows:
    print(f"  Columns with missing values: {len(missing_rows)}")
    for r in missing_rows:
        print(f"    {r['column']:35s}  ({r['cat']:25s})  "
              f"{r['missing_count']:6d}  ({r['missing_pct']:.2f}%)")
else:
    print("  No missing values detected in any column.")

# ═══════════════════════════════════════════════════════════════════════
# 6.  DUPLICATE ROW ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Duplicate row analysis ---")

# Check exact duplicates across all columns
seen = {}
dup_indices = []
for idx, r in enumerate(raw_rows):
    row_tuple = tuple(r[h] for h in raw_headers)
    if row_tuple in seen:
        dup_indices.append(idx)
    else:
        seen[row_tuple] = idx

# Check duplicates excluding identifiers (for same algorithm+instance duplicates)
seen_no_id = {}
dup_no_id = []
for idx, r in enumerate(raw_rows):
    key_cols = tuple(r[h] for h in raw_headers if h not in IDENTIFIERS)
    if key_cols in seen_no_id:
        dup_no_id.append(idx)
    else:
        seen_no_id[key_cols] = idx

with open(os.path.join(OUT_DIR, 'duplicate_rows.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['check_type', 'duplicate_count'])
    w.writerow(['exact_all_columns', len(dup_indices)])
    w.writerow(['excluding_identifiers', len(dup_no_id)])

if dup_indices:
    print(f"  Exact duplicate rows (all columns): {len(dup_indices)}")
else:
    print("  Exact duplicate rows (all columns): 0")
if dup_no_id:
    print(f"  Rows with duplicate data (excluding identifiers): {len(dup_no_id)}")
else:
    print("  Rows with duplicate data (excluding identifiers): 0")

# ═══════════════════════════════════════════════════════════════════════
# 7.  OUTLIER DETECTION (IQR method, descriptive only)
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Outlier detection (IQR method, descriptive only) ---")

outlier_rows = []
for h in sorted(numeric_cols):
    vals = [v for v in parsed[h] if not math.isnan(v)]
    if len(vals) < 4:
        continue
    sv = sorted(vals)
    n = len(sv)
    q1 = sv[int(0.25 * n)]
    q3 = sv[int(0.75 * n)]
    iqr = q3 - q1
    if iqr == 0:
        continue
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outlier_count = sum(1 for v in vals if v < lower or v > upper)
    outlier_pct = 100.0 * outlier_count / n
    outlier_rows.append({
        'column': h, 'cat': col_category.get(h, ''),
        'n': n, 'q1': q1, 'q3': q3, 'iqr': iqr,
        'lower_fence': lower, 'upper_fence': upper,
        'outlier_count': outlier_count, 'outlier_pct': outlier_pct,
    })

# Write outlier summary
with open(os.path.join(OUT_DIR, 'outlier_summary.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['column', 'category', 'n', 'q1', 'q3', 'iqr',
                'lower_fence', 'upper_fence', 'outlier_count', 'outlier_pct'])
    for r in sorted(outlier_rows, key=lambda x: -x['outlier_pct']):
        w.writerow([r['column'], r['cat'], r['n'],
                    f"{r['q1']:.6f}", f"{r['q3']:.6f}", f"{r['iqr']:.6f}",
                    f"{r['lower_fence']:.6f}", f"{r['upper_fence']:.6f}",
                    r['outlier_count'], f"{r['outlier_pct']:.2f}"])

# Top 10 columns by outlier fraction
top_outliers = sorted(outlier_rows, key=lambda x: -x['outlier_pct'])[:10]
print(f"  Columns with highest outlier fraction (IQR):")
for r in top_outliers:
    print(f"    {r['column']:35s}  ({r['cat']:25s})  "
          f"{r['outlier_count']:6d} / {r['n']:6d}  ({r['outlier_pct']:.1f}%)")

# ═══════════════════════════════════════════════════════════════════════
# 8.  DISTRIBUTION ANALYSIS (Skewness)
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Distribution analysis ---")

high_skew = [r for r in stats_rows
             if r['skew'] is not None and abs(r['skew']) > 2.0]
moderate_skew = [r for r in stats_rows
                 if r['skew'] is not None and 1.0 < abs(r['skew']) <= 2.0]
print(f"  Highly skewed (|skew| > 2):  {len(high_skew)}")
print(f"  Moderately skewed (1-2):     {len(moderate_skew)}")
print(f"  Approximately symmetric:     "
      f"{len(stats_rows) - len(high_skew) - len(moderate_skew)}")

# Recommend log-transform candidates (positive, highly-skewed)
log_candidates = [r for r in high_skew
                  if r['min'] is not None and r['min'] >= 0]
print("\n  Candidates for log transformation (positive, |skew|>2):")
for r in sorted(log_candidates, key=lambda x: -abs(x['skew']))[:15]:
    print(f"    {r['column']:35s}  skew={r['skew']:.2f}  "
          f"range=[{r['min']:.2e}, {r['max']:.2e}]")

# ═══════════════════════════════════════════════════════════════════════
# 9.  CORRELATION MATRIX (Pearson, numeric columns only)
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Correlation matrix (Pearson) ---")

# Select numeric columns for correlation (exclude identifiers, list-like strings)
corr_cols = sorted(
    c for c in numeric_cols
    if col_category.get(c) not in ('identifier',)
    and c not in list_like_cols
)
n_corr = len(corr_cols)
print(f"  Including {n_corr} numeric columns")

corr_matrix = np.full((n_corr, n_corr), np.nan)
for i, c1 in enumerate(corr_cols):
    v1 = np.array(parsed[c1])
    for j, c2 in enumerate(corr_cols):
        if j < i:
            continue
        # Pairwise complete
        mask = ~(np.isnan(v1) | np.isnan(np.array(parsed[c2])))
        s1 = v1[mask]
        s2 = np.array(parsed[c2])[mask]
        if len(s1) > 2:
            r_val = np.corrcoef(s1, s2)[0, 1]
            corr_matrix[i, j] = r_val
            corr_matrix[j, i] = r_val

# Write CSV
with open(os.path.join(OUT_DIR, 'correlation_matrix.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow([''] + corr_cols)
    for i, c1 in enumerate(corr_cols):
        row = [c1]
        for j in range(n_corr):
            val = corr_matrix[i, j]
            row.append(f"{val:.6f}" if not math.isnan(val) else '')
        w.writerow(row)

# Identify high correlations
high_corr_pairs = []
for i in range(n_corr):
    for j in range(i + 1, n_corr):
        val = corr_matrix[i, j]
        if not math.isnan(val) and abs(val) > 0.95:
            high_corr_pairs.append((corr_cols[i], corr_cols[j], val))

print(f"  Highly correlated pairs (|r| > 0.95): {len(high_corr_pairs)}")
for c1, c2, r_val in high_corr_pairs[:20]:
    print(f"    {c1:35s}  ↔  {c2:35s}  r={r_val:.4f}")

# ═══════════════════════════════════════════════════════════════════════
# 10. CORRELATION HEATMAP
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Generating correlation heatmap ---")

# Create a reduced set for the heatmap (key columns only for readability)
heatmap_cols = [
    'n', 'capacity',
    'time_millis', 'memory_mb', 'solution_value', 'optimality_gap',
    'nodes_explored', 'nodes_pruned', 'max_queue_size',
    'total_weight', 'total_value', 'mean_weight', 'mean_value',
    'std_weight', 'weight_cv', 'value_cv',
    'capacity_ratio', 'slack', 'average_fillable_items',
    'pearson_corr', 'spearman_corr',
    'mean_ratio', 'ratio_entropy', 'duplicate_ratio_fraction',
    'nodes_generated', 'leaf_nodes', 'internal_nodes',
    'max_depth', 'mean_depth',
    'mean_bound', 'bound_variance',
    'pruned_by_bound', 'pruned_by_cap',
    'left_branches', 'right_branches',
    'improvement_count', 'sum_improvement_amount',
    'explored_generated_ratio', 'avg_branching_factor',
    'capacity_density', 'cells_allocated', 'total_evaluations',
    'include_count', 'exclude_count', 'include_ratio',
    'nonzero_value_states', 'fill_rate',
    'selected_count', 'solution_density', 'capacity_utilization',
]

# Ensure all selected columns exist and are numeric
heatmap_cols = [c for c in heatmap_cols if c in corr_cols]
n_hm = len(heatmap_cols)
print(f"  Heatmap includes {n_hm} columns")

hm_matrix = np.full((n_hm, n_hm), np.nan)
for i, c1 in enumerate(heatmap_cols):
    v1 = np.array(parsed[c1])
    for j, c2 in enumerate(heatmap_cols):
        if j < i:
            continue
        mask = ~(np.isnan(v1) | np.isnan(np.array(parsed[c2])))
        s1 = v1[mask]
        s2 = np.array(parsed[c2])[mask]
        if len(s1) > 2:
            hm_matrix[i, j] = np.corrcoef(s1, s2)[0, 1]
            hm_matrix[j, i] = hm_matrix[i, j]

fig, ax = plt.subplots(figsize=(20, 18))
im = ax.imshow(hm_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

ax.set_xticks(range(n_hm))
ax.set_yticks(range(n_hm))
ax.set_xticklabels(heatmap_cols, rotation=90, fontsize=5)
ax.set_yticklabels(heatmap_cols, fontsize=5)

cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label('Pearson r', fontsize=8)
cbar.ax.tick_params(labelsize=6)

ax.set_title('Pearson Correlation Matrix — Key Variables', fontsize=10, pad=10)

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'correlation_heatmap.png'),
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f"  Heatmap saved to {OUT_DIR}/correlation_heatmap.png")

# ═══════════════════════════════════════════════════════════════════════
# 11. HISTOGRAMS
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Generating histograms ---")

for h in sorted(numeric_cols):
    if h in list_like_cols:
        continue
    vals = [v for v in parsed[h] if not math.isnan(v)]
    if not vals:
        continue
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.hist(vals, bins=80, color='#0072B2', edgecolor='white', alpha=0.85)
    ax.set_xlabel(h, fontsize=8)
    ax.set_ylabel('Frequency', fontsize=8)
    ax.set_title(f'{h}  [{col_category.get(h, "")}]', fontsize=9)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(HIST_DIR, f'{h}.png'), dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close(fig)

print(f"  Histograms saved to {HIST_DIR}/  ({len(os.listdir(HIST_DIR))} files)")

# ═══════════════════════════════════════════════════════════════════════
# 12. BOXPLOTS (key outcome and metric variables)
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Generating boxplots ---")

boxplot_vars = [
    'time_millis', 'memory_mb', 'solution_value', 'optimality_gap',
    'nodes_explored', 'nodes_pruned', 'max_queue_size',
    'selected_count', 'solution_density', 'capacity_utilization',
    'capacity_density', 'fill_rate', 'include_ratio',
    'mean_bound', 'bound_variance', 'avg_branching_factor',
    'explored_generated_ratio', 'pruned_generated_ratio',
    'improvement_count', 'sum_improvement_amount',
    'total_evaluations', 'nonzero_value_states',
    'mean_cell_value', 'updates_per_cell',
]

algorithms_list = ['Greedy', 'DynamicProgramming', 'BranchAndBound']
algo_short = {'Greedy': 'Greedy', 'DynamicProgramming': 'DP', 'BranchAndBound': 'B&B'}

for var in boxplot_vars:
    if var not in numeric_cols:
        continue
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for mode_idx, mode in enumerate(['fixed', 'scaled']):
        ax = axes[mode_idx]
        positions = []
        data_groups = []
        labels = []
        pos = 0
        for algo in algorithms_list:
            subset = [parsed[var][i] for i in range(n_rows)
                      if raw_rows[i]['algorithm'] == algo
                      and raw_rows[i]['capacity_mode'] == mode
                      and not math.isnan(parsed[var][i])]
            if subset:
                positions.append(pos)
                data_groups.append(subset)
                labels.append(algo_short[algo])
                pos += 1.5
        if data_groups:
            bp = ax.boxplot(data_groups, positions=positions, widths=0.5,
                            patch_artist=True)
            for patch, algo in zip(bp['boxes'], [a for a in algorithms_list
                                     if any(raw_rows[i]['algorithm'] == a
                                            for i in range(n_rows))]):
                patch.set_facecolor(get_algo_color(algo))
                patch.set_alpha(0.5)
            ax.set_xticks(positions)
            ax.set_xticklabels(labels, fontsize=8)
            ax.set_title(f'{mode.capitalize()} capacity', fontsize=9)
            ax.set_ylabel(var, fontsize=8)
            ax.tick_params(labelsize=7)
            ax.grid(True, alpha=0.3)
            # Add count annotation
            for p, d in zip(positions, data_groups):
                ax.text(p, ax.get_ylim()[1] * 0.95, f'n={len(d)}',
                        ha='center', fontsize=6, alpha=0.7)
        else:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
    fig.suptitle(f'{var} by Algorithm and Capacity Mode', fontsize=10, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(BOX_DIR, f'{var}.png'), dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close(fig)

# Also produce boxplots by family for key outcome variables
fam_vars = ['time_millis', 'nodes_explored', 'solution_value', 'optimality_gap']
for var in fam_vars:
    if var not in numeric_cols:
        continue
    for algo in algorithms_list:
        fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
        for mode_idx, mode in enumerate(['fixed', 'scaled']):
            ax = axes[mode_idx]
            families_list = ['Uncorrelated', 'WeaklyCorrelated', 'StronglyCorrelated',
                             'InverseCorrelated', 'AlmostEqualRatios']
            positions = []
            data_groups = []
            labels = []
            for pos_idx, fam in enumerate(families_list):
                subset = [parsed[var][i] for i in range(n_rows)
                          if raw_rows[i]['algorithm'] == algo
                          and raw_rows[i]['capacity_mode'] == mode
                          and raw_rows[i]['family'] == fam
                          and not math.isnan(parsed[var][i])]
                if subset:
                    positions.append(pos_idx)
                    data_groups.append(subset)
                    labels.append(get_fam_short(fam))
            if data_groups:
                bp = ax.boxplot(data_groups, positions=positions, widths=0.5,
                                patch_artist=True)
                for patch, fam in zip(bp['boxes'], families_list):
                    patch.set_facecolor(FAM_COLORS.get(fam, '#333333'))
                    patch.set_alpha(0.5)
                ax.set_xticks(positions)
                ax.set_xticklabels(labels, fontsize=8)
                ax.set_title(f'{mode.capitalize()} capacity', fontsize=9)
                ax.set_ylabel(var, fontsize=8)
                ax.tick_params(labelsize=7)
                ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                        transform=ax.transAxes)
        fig.suptitle(f'{algo} — {var} by Family', fontsize=10, y=1.02)
        fig.tight_layout()
        safe_var = var.replace('_', '').replace('.', '')
        fig.savefig(os.path.join(BOX_DIR, f'{algo}_{var}_by_family.png'),
                    dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

print(f"  Boxplots saved to {BOX_DIR}/  ({len(os.listdir(BOX_DIR))} files)")

# ═══════════════════════════════════════════════════════════════════════
# 13. ALGORITHM-SPECIFIC MISSING METRICS
# ═══════════════════════════════════════════════════════════════════════
print("\n--- Algorithm-specific metric availability ---")

# For each algorithm, count how many of its specific metrics are populated
algo_metrics = {
    'BranchAndBound': BB_METRICS,
    'DynamicProgramming': DP_METRICS,
    'Greedy': GREEDY_METRICS,
}

for algo, metrics in algo_metrics.items():
    total_metric_cells = 0
    populated = 0
    for h in metrics:
        for i in range(n_rows):
            if raw_rows[i]['algorithm'] == algo:
                total_metric_cells += 1
                if h in numeric_cols:
                    if not math.isnan(parsed[h][i]):
                        populated += 1
                else:
                    if not is_missing(raw_rows[i][h]):
                        populated += 1
    if total_metric_cells > 0:
        pct = 100.0 * populated / total_metric_cells
        print(f"  {algo:20s}: {populated}/{total_metric_cells} metric cells "
              f"populated ({pct:.1f}%)")

# ═══════════════════════════════════════════════════════════════════════
# 14. OPTIMALITY GAP ANALYSIS (B&B incomplete searches)
# ═══════════════════════════════════════════════════════════════════════
print("\n--- B&B optimality / completeness analysis ---")

bb_optimal_false = sum(1 for i in range(n_rows)
                       if raw_rows[i]['algorithm'] == 'BranchAndBound'
                       and raw_rows[i].get('optimal', '').strip() == 'false')
bb_total = sum(1 for i in range(n_rows)
               if raw_rows[i]['algorithm'] == 'BranchAndBound')
print(f"  B&B total rows:        {bb_total}")
print(f"  B&B optimal=false:     {bb_optimal_false}")
if bb_total > 0:
    print(f"  B&B incomplete pct:    {100.0 * bb_optimal_false / bb_total:.2f}%")

# ═══════════════════════════════════════════════════════════════════════
# 15. SUMMARY
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  EDA Complete")
print("=" * 65)
print(f"\nOutput directory: {OUT_DIR}/")
for f in sorted(os.listdir(OUT_DIR)):
    fpath = os.path.join(OUT_DIR, f)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath)
        print(f"  {f:40s}  {size:>8,} bytes")
for sub in ['histograms', 'boxplots']:
    subpath = os.path.join(OUT_DIR, sub)
    if os.path.isdir(subpath):
        nf = len(os.listdir(subpath))
        print(f"  {sub + '/':40s}  {nf} files")
print(f"\nTotal columns analyzed: {n_cols}")
print(f"Total rows:             {n_rows}")
print(f"Numeric columns:        {len(numeric_cols)}")
print(f"String columns:         {len(string_cols)}")
print(f"Missing values:         {sum(r['missing_count'] for r in missing_rows)}")
print(f"Exact duplicate rows:   {len(dup_indices)}")
print(f"High-correlation pairs: {len(high_corr_pairs)}")
print(f"Highly skewed columns:  {len(high_skew)}")
print(f"\nDone.")
