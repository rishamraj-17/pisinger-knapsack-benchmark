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

echo "Step 0/6: Cleaning up stale outputs..."
rm -f outputs/tables/*.tex outputs/tables/*.csv \
    outputs/figures/fixed/pdf/*.pdf outputs/figures/fixed/png/*.png outputs/figures/fixed/svg/*.svg \
    outputs/figures/scaled/pdf/*.pdf outputs/figures/scaled/png/*.png outputs/figures/scaled/svg/*.svg

echo "Step 1/6: Fixed-capacity experiment (n up to 1000, 100 seeds)..."
./build_and_run.sh 20,50,100,200,500,1000 1000 100 42 fixed
cp data/raw/full_experiment.csv data/raw/fixed_experiment.csv

echo ""
echo "Step 2/6: Scaled-capacity experiment (W = 0.5 * sum_weights, n up to 1000, 100 seeds)..."
./build_and_run.sh 20,50,100,200,500,1000 0 100 42 scaled
cp data/raw/full_experiment.csv data/raw/scaled_experiment.csv

echo ""
echo "Step 3/6: Combining results..."
# Combine: add a capacity_mode column
python/venv/bin/python -c "
import csv
import os

os.makedirs('data/raw', exist_ok=True)

# Read fixed
with open('data/raw/fixed_experiment.csv') as f:
    reader = csv.DictReader(f)
    fixed_rows = list(reader)
    fixed_header = reader.fieldnames

# Read scaled
with open('data/raw/scaled_experiment.csv') as f:
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

with open('data/raw/full_experiment.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(out_header)
    writer.writerows(out_rows)

print(f'Combined {len(out_rows)} rows ({len(fixed_rows)} fixed + {len(scaled_rows)} scaled)')
"

echo ""
echo "Step 4/6: Generating EDA tables and figures..."
python/venv/bin/python python/scripts/analyze.py data/raw/full_experiment.csv

echo ""
echo "Step 5/6: Generating regression tables from model results..."
python/venv/bin/python python/scripts/build_regression_tables.py

echo ""
echo "Step 6/6: Recompiling manuscript PDF..."
(cd manuscript && ./tectonic main.tex)

echo ""
echo "=== Reproduction complete ==="
echo "  Raw data:     data/raw/full_experiment.csv"
echo "  Fixed data:   data/raw/fixed_experiment.csv"
echo "  Scaled data:  data/raw/scaled_experiment.csv"
echo "  LaTeX tables: outputs/tables/*.tex"
echo "  Figures:      outputs/figures/fixed/pdf/*.pdf  outputs/figures/fixed/png/*.png  outputs/figures/fixed/svg/*.svg"
echo "                outputs/figures/scaled/pdf/*.pdf outputs/figures/scaled/png/*.png outputs/figures/scaled/svg/*.svg"
