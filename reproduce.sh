#!/bin/bash
# reproduce.sh -- Full reproduction pipeline.
#
# Regenerates all experimental results, tables, and figures from scratch.
# Requires: Java 17+, Python 3.8+ (numpy, matplotlib).
#
# Usage:
#   ./reproduce.sh

set -e

echo "=== Knapsack Empirical Comparison: Reproduction Pipeline ==="
echo ""

echo "Step 0/4: Cleaning up stale outputs..."
rm -f tables/*.tex tables/*.csv \
    figures/fixed/pdf/*.pdf figures/fixed/png/*.png figures/fixed/svg/*.svg \
    figures/scaled/pdf/*.pdf figures/scaled/png/*.png figures/scaled/svg/*.svg

echo "Step 1/4: Fixed-capacity experiment (n up to 1000, 100 seeds)..."
./build_and_run.sh 20,50,100,200,500,1000 1000 100 42 fixed
cp out/results/full_experiment.csv out/results/fixed_experiment.csv

echo ""
echo "Step 2/4: Scaled-capacity experiment (W = 0.5 * sum_weights, n up to 1000, 100 seeds)..."
./build_and_run.sh 20,50,100,200,500,1000 0 100 42 scaled
cp out/results/full_experiment.csv out/results/scaled_experiment.csv

echo ""
echo "Step 3/4: Combining results..."
# Combine: add a capacity_mode column
python3 -c "
import csv
import os

os.makedirs('out/results', exist_ok=True)

# Read fixed
with open('out/results/fixed_experiment.csv') as f:
    reader = csv.DictReader(f)
    fixed_rows = list(reader)
    fixed_header = reader.fieldnames

# Read scaled
with open('out/results/scaled_experiment.csv') as f:
    reader = csv.DictReader(f)
    scaled_rows = list(reader)
    scaled_header = reader.fieldnames

# Add capacity_mode column (fixed_experiment already has one; replace it to avoid duplicates)
out_header = [h for h in fixed_header if h != 'capacity_mode'] + ['capacity_mode']
out_rows = []
for r in fixed_rows:
    row = [r[h] for h in fixed_header if h != 'capacity_mode'] + ['fixed']
    out_rows.append(row)
for r in scaled_rows:
    row = [r[h] for h in fixed_header if h != 'capacity_mode'] + ['scaled']
    out_rows.append(row)

with open('out/results/full_experiment.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(out_header)
    writer.writerows(out_rows)

print(f'Combined {len(out_rows)} rows ({len(fixed_rows)} fixed + {len(scaled_rows)} scaled)')
"

echo ""
echo "Step 4/4: Generating tables and figures..."
python3 analyze.py out/results/full_experiment.csv

echo ""
echo "=== Reproduction complete ==="
echo "  Raw data:     out/results/full_experiment.csv"
echo "  Fixed data:   out/results/fixed_experiment.csv"
echo "  Scaled data:  out/results/scaled_experiment.csv"
echo "  LaTeX tables: tables/*.tex"
echo "  Figures:      figures/fixed/pdf/*.pdf  figures/fixed/png/*.png  figures/fixed/svg/*.svg"
echo "                figures/scaled/pdf/*.pdf figures/scaled/png/*.png figures/scaled/svg/*.svg"
