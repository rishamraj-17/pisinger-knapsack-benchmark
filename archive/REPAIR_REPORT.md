# Repository Repair Report

**Date:** 2026-07-11  
**Project:** Knapsack Empirical Comparison  
**Scope:** Evidence-based repair for correctness, reproducibility, and scientific traceability

---

## 1. Confirmed Issues Fixed

### 1.1 Maven Main Class Configuration
**Problem:** `pom.xml` specified `benchmark.BenchmarkRunner` as main class, but `BenchmarkRunner` has no `main()` method.
**Cause:** Incorrect mainClass in maven-jar-plugin and maven-shade-plugin configuration.
**Solution:** Changed mainClass to `Main` in both plugins.
**Files:** `pom.xml` (lines 32, 42)

### 1.2 Duplicate Experiment Entry Points
**Problem:** Two main classes (`Main.java` and `FullExperiment.java`) with nearly identical code but different output paths (timestamped vs fixed filename).
**Cause:** Historical duplication without cleanup.
**Solution:** Deleted `FullExperiment.java`; enhanced `Main.java` as single canonical entry point with fixed output `results/full_experiment.csv`.
**Files:** Removed `src/main/java/FullExperiment.java`; Modified `src/main/java/Main.java`

### 1.3 Metric Inconsistency: Greedy optimalValue/optimalityGap
**Problem:** Greedy algorithm wrote `optimalValue=-1` and `optimalityGap=0.000000` to CSV, implying it knows the optimal value (it doesn't).
**Cause:** Greedy.builder() called `.optimalValue(-1)` which Result.Builder used to compute gap.
**Solution:** 
- Modified `Result.toCsvRow()` to output empty strings for `optimal_value` and `optimality_gap` when `optimalValue <= 0`
- Removed `.optimalValue(-1)` from Greedy and error/timeout handlers
- DP correctly writes optimal value; analysis script computes greedy gap using DP as ground truth
**Files:** `src/main/java/model/Result.java` (line 63); `src/main/java/algorithms/Greedy.java`; `src/main/java/benchmark/BenchmarkRunner.java`

### 1.4 Multiple Analysis Scripts with Incompatible Assumptions
**Problem:** 5 analysis scripts (`analyze.py`, `analyze_simple.py`, `scripts/analyze.py`, `visualize.py`, `generate_html_viz.py`) with different dependencies, assumptions, and output formats.
**Cause:** Organic growth without consolidation.
**Solution:** Created single canonical `analyze.py` (stdlib only, no pandas/matplotlib required) that:
- Reads `results/full_experiment.csv`
- Computes greedy gap from DP ground truth
- Generates 6 figures (PNG) and 5 LaTeX tables + CSV summary
**Files:** New `analyze.py`; Deprecated: `analyze_simple.py`, `scripts/analyze.py`, `visualize.py`, `generate_html_viz.py`

### 1.5 Ambiguous Experiment Output
**Problem:** Multiple CSV files with timestamps (`full_experiment_*.csv`, `benchmark_*.csv`), unclear which is canonical.
**Cause:** Each run generated new timestamped file.
**Solution:** Canonical output is now `results/full_experiment.csv` (fixed name, overwritten each run).
**Files:** `src/main/java/Main.java` (output path)

### 1.6 Broken Build/Run Script
**Problem:** `build_and_run.sh` used absolute paths, incorrect classpath when running from `out/` directory.
**Cause:** Path handling didn't account for `cd out` before java command.
**Solution:** Fixed relative paths, download logic, and classpath.
**Files:** `build_and_run.sh`

---

## 2. Remaining Issues Requiring Human Decisions

### 2.1 Paper Numbers Contradict Experimental Data
**Severity:** Critical  
**Details:** The paper draft (`paper/draft.md`) contains numerous numerical claims that **do not match** the actual experimental results from the current codebase:

| Paper Claim | Actual Result | Discrepancy |
|-------------|---------------|-------------|
| B&B on Inverse Correlated: 4.69ms | 164.32 ± 802.71ms | 3400% higher |
| DP time ~0.4ms across families | 0.31-0.62ms, family-dependent | 30-55% off |
| Greedy gap 50-60% on Uncorrelated | <1% median gap | Impossible values |
| Negative gaps reported (-43% to -154%) | Gap ≥ 0 always | Mathematically impossible |
| B&B nodes at n=500: Uncorrelated median 576 | 138 (all n pooled) | 4× difference |

**Action Required:** Either (a) re-run experiments with paper's exact parameters to verify, or (b) rewrite paper tables/figures using actual data from `tables/*.tex`.

### 2.2 B&B Timeout Behavior on Inverse Correlated
**Severity:** High  
**Details:** B&B has extreme variance on Inverse Correlated (max 25M nodes, time 164ms mean but 802ms std). Some instances likely hit 30s timeout. Paper reports 4.69ms which suggests either different timeout, different seed, or different instance generation.

### 2.3 Statistical Methodology
**Severity:** Medium  
**Details:** Paper reports "mean ± std" but uses median in some tables, mean in others. No confidence intervals, no multiple comparison correction, no power analysis.

### 2.4 Hardware/Environment Documentation
**Severity:** Medium  
**Details:** Paper says "Intel/AMD x64, Linux" but no specific CPU, JVM version, or GC settings recorded. Required for full reproducibility.

---

## 3. Current Repository State

### Architecture
```
src/main/java/
├── Main.java                    # Canonical entry point
├── algorithms/
│   ├── Algorithm.java           # Interface
│   ├── AlgorithmFactory.java    # Enum factory
│   ├── Greedy.java             # O(n log n)
│   ├── DynamicProgramming.java # O(nW) exact
│   └── BranchAndBound.java     # Best-first exact
├── benchmark/
│   ├── BenchmarkRunner.java    # Warmup, timeout, parallel
│   └── ResultsExporter.java    # CSV export
├── dataset/
│   ├── DatasetGenerator.java   # Builder pattern
│   ├── InstanceGenerator.java  # Interface
│   ├── UncorrelatedGenerator.java
│   ├── WeaklyCorrelatedGenerator.java
│   ├── StronglyCorrelatedGenerator.java
│   ├── InverseCorrelatedGenerator.java
│   └── AlmostEqualRatiosGenerator.java
└── model/
    ├── Item.java
    ├── KnapsackInstance.java
    ├── Result.java             # CSV schema + gap computation
    └── Solution.java
```

### Canonical Pipeline
```
./build_and_run.sh 20,50,100,200,500 1000 30 42
        ↓
results/full_experiment.csv (6750 rows = 750 instances × 3 algos)
        ↓
python3 analyze.py results/full_experiment.csv
        ↓
figures/ (6 PNGs) + tables/ (5 .tex + 1 .csv)
        ↓
Copy tables/*.tex → paper/
Reference figures/*.png → paper/
```

### Outputs
- **CSV:** 15 columns, 6750 rows, Greedy rows have empty `optimal_value`/`optimality_gap`
- **Figures:** time_vs_n.png, greedy_gap.png, bb_nodes.png, time_n500.png, gap_vs_n.png, memory_n500.png
- **Tables:** table_time_n500.tex, table_greedy_gap.tex, table_bb_nodes.tex, table_dp_scaling.tex, table_full_summary.csv

---

## 4. Evidence (File Changes)

| File | Change Type | Lines |
|------|-------------|-------|
| `pom.xml` | Modified | 32, 42: mainClass=Main |
| `src/main/java/Main.java` | Rewritten | All: canonical entry point, fixed output path, docs |
| `src/main/java/FullExperiment.java` | **Deleted** | - |
| `src/main/java/model/Result.java` | Modified | 63: empty strings for missing optimal_value |
| `src/main/java/algorithms/Greedy.java` | Modified | Removed `.optimalValue(-1)` |
| `src/main/java/benchmark/BenchmarkRunner.java` | Modified | Timeout/error handlers: removed `.optimalValue(-1)` |
| `build_and_run.sh` | Rewritten | Relative paths, correct classpath, download logic |
| `analyze.py` | **Created** | 300 lines, stdlib-only, canonical analysis |
| `PIPELINE.md` | **Created** | Full pipeline documentation |
| `PAPER_INCONSISTENCIES.md` | **Created** | Detailed paper vs data comparison |

### Deprecated Files (Not Deleted, But Marked)
- `analyze_simple.py` → use `analyze.py`
- `scripts/analyze.py` → use `analyze.py`
- `visualize.py` → use `analyze.py`
- `generate_html_viz.py` → use `analyze.py`
- `out/results/benchmark_*.csv` → legacy, use `results/full_experiment.csv`
- `all_results.csv`, `summary_results.csv` → legacy aggregates

---

## Verification

```bash
# Full pipeline test (takes ~2 minutes)
./build_and_run.sh 20,50,100,200,500 1000 30 42
python3 analyze.py out/results/full_experiment.csv

# Verify outputs
wc -l results/full_experiment.csv    # 6751 (header + 6750 rows)
ls figures/*.png                     # 6 figures
ls tables/*.tex                      # 5 LaTeX tables
```

---

## Conclusion

The repository now has:
- ✅ Single canonical experiment entry point (`Main.java`)
- ✅ Single canonical analysis script (`analyze.py`)
- ✅ Single canonical CSV output (`results/full_experiment.csv`)
- ✅ Fixed Maven build (`mvn package` produces runnable JAR)
- ✅ Fixed metrics (no fake optimal values for Greedy)
- ✅ Documented pipeline (`PIPELINE.md`)

**Critical remaining work:** The paper draft must be rewritten using actual experimental data from `tables/*.tex`. The current paper contains mathematically impossible values (negative optimality gaps) and order-of-magnitude discrepancies in B&B runtime.