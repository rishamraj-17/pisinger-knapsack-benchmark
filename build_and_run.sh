#!/bin/bash
# Build and run script for Knapsack Empirical Comparison
# Usage: ./build_and_run.sh [n-values] [capacity] [instances-per-config] [seed]
# Example: ./build_and_run.sh 20,50,100,200,500 1000 30 42

set -e

SRC_DIR="src/main/java"
LIB_DIR="lib"
OUT_DIR="out"
JAR_NAME="knapsack.jar"

mkdir -p "$LIB_DIR" "$OUT_DIR" "results"

# Download dependency if needed
if [ ! -f "$LIB_DIR/commons-csv-1.10.0.jar" ]; then
    echo "Downloading commons-csv..."
    curl -L -o "$LIB_DIR/commons-csv-1.10.0.jar" \
        "https://repo1.maven.org/maven2/org/apache/commons/commons-csv/1.10.0/commons-csv-1.10.0.jar"
fi

echo "Compiling..."
javac -d "$OUT_DIR" -cp "$LIB_DIR/commons-csv-1.10.0.jar" \
    $(find "$SRC_DIR" -name "*.java")

echo "Running experiment..."
cd "$OUT_DIR"
java -cp ".:../$LIB_DIR/commons-csv-1.10.0.jar" Main "$@"

echo ""
echo "Experiment complete. Results in results/full_experiment.csv"