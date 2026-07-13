# Quick Start Guide
## Empirical Comparison of Knapsack Algorithms

### Prerequisites
- Java 17+ (or OpenJDK 17+)
- Python 3.7+ (for analysis only, stdlib only)
- ~100MB disk space for results

### Fastest Setup (2 minutes)

```bash
# 1. Navigate to project
cd /home/risham-raj-byahut/IdeaProjects/Emperical_Comparision

# 2. Build and run QUICK test
./build_and_run.sh 20,50 1000 5 42

# This will:
# - Compile all Java files
# - Generate 50 test instances (2 sizes × 5 seeds × 5 families)
# - Run all 3 algorithms
# - Export results to out/results/full_experiment.csv
```

### Output
```
=== Knapsack Empirical Comparison ===
ns: [20, 50]
capacity: 1000, instances/config: 5, seed: 42
Total instances: 50
Total runs: 150
Generated 50 instances
Running Greedy...
Running DynamicProgramming...
Running BranchAndBound...
Exported 150 results to results/full_experiment.csv
Done! Results: 150 rows
Output: /home/.../out/results/full_experiment.csv
```

### Full Experiment (~2 minutes)

```bash
# Run all 5 sizes with 30 seeds each (2,250 results)
./build_and_run.sh 20,50,100,200,500 1000 30 42
```

### Analysis (Python - stdlib only, no dependencies)

```bash
# Generate LaTeX tables and CSV summary
python3 analyze.py out/results/full_experiment.csv

# Outputs:
# - tables/table_time_n500.tex       - Time at n=500 with 95% CI
# - tables/table_greedy_gap.tex      - Greedy gap with 95% CI
# - tables/table_bb_nodes.tex        - B&B nodes with 95% CI
# - tables/table_bb_time_n500.tex    - B&B time at n=500 with outlier analysis
# - tables/table_dp_scaling.tex      - DP time by n and family with CI
# - tables/table_full_summary.csv    - Complete summary (all n, algos, families)
```

### Expected Results Location
- `out/results/full_experiment.csv` - Raw data (2,250 rows for full run)
- `tables/*.tex` - 6 LaTeX tables ready for paper
- `tables/table_full_summary.csv` - Complete summary for verification

### Key Files to Review

| File | Purpose | Time |
|------|---------|------|
| `paper/draft.md` | Full research paper (updated from data) | 10 min read |
| `PIPELINE.md` | Complete reproducibility pipeline | 5 min read |
| `tables/*.tex` | LaTeX tables for paper | 2 min read |

### Customization

**Change problem size**:
```bash
./build_and_run.sh 50,100 2000 10 42
# n: {50, 100}, W: 2000, 10 seeds
```

**Different random seed**:
```bash
./build_and_run.sh 20 1000 5 99
```

**Reproduce exact results** (fixed seed 42):
```bash
./build_and_run.sh 20,50,100,200,500 1000 30 42
```

### Troubleshooting

**"javac: command not found"**
- Install Java 17+: `sudo apt-get install openjdk-17-jdk`

**Out of memory**
- Increase heap: `java -Xmx4g -cp ...` (use 4GB max heap)

**Slow performance**
- Reduce instances: Use `20,50` instead of `20,50,100,200,500`
- Reduce seeds: Use `10` instead of `30`

**Results not generated**
- Check permissions: `chmod +x build_and_run.sh`
- Check results directory: `mkdir -p out/results`

### Troubleshooting Analysis

**"ModuleNotFoundError: pandas/matplotlib"**
- The analysis script uses ONLY Python standard library
- No external dependencies required
- Run: `python3 analyze.py out/results/full_experiment.csv`

### Next Steps

1. ✅ Run quick test: `./build_and_run.sh 20,50 1000 5 42`
2. ✅ Review paper: `cat paper/draft.md`
3. ✅ Run full experiment: `./build_and_run.sh 20,50,100,200,500 1000 30 42`
4. ✅ Generate tables: `python3 analyze.py out/results/full_experiment.csv`
5. ✅ Submit paper with `tables/*.tex`!

### Support

- **Code**: All source in `src/main/java/`
- **Algorithms**: `src/main/java/algorithms/`
- **Data Generators**: `src/main/java/dataset/`
- **Results**: `out/results/` directory
- **Paper**: `paper/draft.md`
- **Pipeline**: `PIPELINE.md`

---

**Last Updated**: July 11, 2026  
**Status**: ✅ Ready to run