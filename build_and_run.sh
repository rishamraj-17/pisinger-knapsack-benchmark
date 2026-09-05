#!/bin/bash
# Build and run the knapsack benchmark experiment.
#
# Usage:
#   ./build_and_run.sh [n-values] [capacity] [instances-per-config] [seed] [mode]
#
# Defaults: n={20,50,100,200,500}, capacity=1000, instances=30, seed=42, mode=fixed
# Example (fixed):   ./build_and_run.sh 20,50,100,200,500 1000 30 42 fixed
# Example (scaled):  ./build_and_run.sh 20,50,100,200,500,1000 0 100 42 scaled

set -e

SRC_DIR="src/main/java"
LIB_DIR="lib"
OUT_DIR="target"
JAR_NAME="knapsack.jar"

mkdir -p "$LIB_DIR" "data/raw"

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
java -Xmx2g -cp "$OUT_DIR:$LIB_DIR/commons-csv-1.10.0.jar" Main "$@"

echo ""
echo "Done. Results in data/raw/full_experiment.csv"
