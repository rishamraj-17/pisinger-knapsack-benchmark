#!/bin/bash
# reproduce.sh -- Full reproduction pipeline.
#
# Regenerates all experimental results, tables, and figures from scratch.
# Requires: Java 17+, Python 3.8+ (standard library only, no pip dependencies).
#
# Usage:
#   ./reproduce.sh

set -e

echo "=== Knapsack Empirical Comparison: Reproduction Pipeline ==="
echo ""

echo "Step 1/2: Building and running experiment (2,250 runs)..."
./build_and_run.sh 20,50,100,200,500 1000 30 42

echo ""
echo "Step 2/2: Generating tables and figures..."
python3 analyze.py out/results/full_experiment.csv

echo ""
echo "=== Reproduction complete ==="
echo "  Raw data:     out/results/full_experiment.csv"
echo "  LaTeX tables: tables/*.tex"
echo "  Figures:      figures/*.pdf  figures/*.png  figures/*.svg"
