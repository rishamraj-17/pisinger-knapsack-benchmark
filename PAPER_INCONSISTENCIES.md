# Paper vs. Experiment Inconsistency Report

**Date:** 2026-07-11  
**Experiment:** Full run with seed=42, n={20,50,100,200,500}, W=1000, 30 seeds/family  
**Canonical CSV:** `results/full_experiment.csv` (6750 rows)  
**Analysis:** `python3 analyze.py results/full_experiment.csv`

---

## Summary

**The paper contains significant numerical discrepancies compared to actual experimental results.** The paper appears to have been written with fabricated or incorrect numbers, not derived from the current codebase.

---

## Detailed Comparison

### Table 1: Execution Time at n=500 (ms)

| Algorithm | Family | **Paper** | **Actual** | **Match?** |
|-----------|--------|-----------|------------|------------|
| Greedy | Uncorrelated | 0.27 | 0.27 ± 0.02 | ✅ Close |
| Greedy | Weakly Correlated | 0.29 | 0.27 ± 0.33 | ⚠️ Close (high variance) |
| Greedy | **Strongly Correlated** | **0.29** | **0.19 ± 0.05** | ❌ **Off by 52%** |
| Greedy | Inverse Correlated | 0.18 | 0.17 ± 0.06 | ✅ Close |
| Greedy | **Equal Ratios** | **0.17** | **0.11 ± 0.03** | ❌ **Off by 55%** |
| DP | Uncorrelated | 0.32 | 0.31 ± 0.18 | ✅ Close |
| DP | Weakly Correlated | 0.43 | 0.37 ± 0.18 | ⚠️ Close |
| DP | **Strongly Correlated** | **0.36** | **0.55 ± 0.14** | ❌ **Off by 53%** |
| DP | **Inverse Correlated** | **0.43** | **0.56 ± 0.09** | ❌ **Off by 30%** |
| DP | **Equal Ratios** | **0.41** | **0.59 ± 0.13** | ❌ **Off by 44%** |
| B&B | Uncorrelated | 0.10 | 0.15 ± 0.04 | ⚠️ Close |
| B&B | Weakly Correlated | 0.12 | 0.14 ± 0.05 | ✅ Close |
| B&B | **Strongly Correlated** | **0.45** | **0.86 ± 0.93** | ❌ **Off by 91%** (high variance) |
| B&B | **Inverse Correlated** | **4.69** | **164.32 ± 802.71** | ❌ **Off by 3400%** (extreme outliers) |
| B&B | **Equal Ratios** | **0.12** | **0.23 ± 0.27** | ❌ **Off by 92%** |

**Key Issues:**
- Paper reports B&B on Inverse Correlated as 4.69ms; actual is 164ms (with massive 802ms std dev)
- Paper reports DP times much lower than actual for 3/5 families
- Paper reports Greedy faster than actual for Strongly Correlated and Equal Ratios

---

### Table 2: Greedy Optimality Gap (%)

| n | Family | **Paper (Mean ± Std)** | **Actual (All n pooled)** | **Match?** |
|---|--------|------------------------|---------------------------|------------|
| 20 | Uncorrelated | 58.6 ± 12.5 | N/A (pooled) | ❌ **Completely different** |
| 20 | Weakly Correlated | 27.1 ± 8.8 | N/A | ❌ |
| 20 | Strongly Correlated | 12.8 ± 7.0 | N/A | ❌ |
| 20 | Inverse Correlated | 60.8 ± 16.2 | N/A | ❌ |
| 20 | Equal Ratios | 5.3 ± 4.3 | N/A | ❌ |
| 50 | Uncorrelated | 32.1 ± 16.5 | N/A | ❌ |
| 50 | Weakly Correlated | 41.6 ± 35.2 | N/A | ❌ |
| 50 | Inverse Correlated | **-154.5 ± 246.1** | N/A | ❌ **Negative gap impossible** |
| 100 | Uncorrelated | 0.9 ± 1.0 | N/A | ❌ |
| 200 | Uncorrelated | **-43.0 ± 27.8** | N/A | ❌ **Negative gap impossible** |
| 200 | Inverse Correlated | **-49.9 ± 32.9** | N/A | ❌ **Negative gap impossible** |
| 500 | Uncorrelated | **-125.7 ± 41.7** | N/A | ❌ **Negative gap impossible** |
| 500 | Weakly Correlated | **-42.8 ± 14.5** | N/A | ❌ **Negative gap impossible** |
| 500 | Inverse Correlated | **-143.7 ± 58.9** | N/A | ❌ **Negative gap impossible** |

**Actual Gap (all n pooled):**
| Family | Median | Mean ± Std |
|--------|--------|------------|
| Uncorrelated | 0.3 | 0.9 ± 1.6 |
| Weakly Correlated | 0.8 | 2.1 ± 3.5 |
| Strongly Correlated | 2.5 | 4.7 ± 6.3 |
| Inverse Correlated | 0.0 | 0.0 ± 0.0 |
| Equal Ratios | 0.4 | 1.1 ± 2.1 |

**Key Issues:**
- Paper reports **negative gaps** (impossible: gap = (opt - greedy)/opt ≥ 0 when greedy ≤ opt)
- Paper reports gaps of 50-60% at small n; actual gaps are < 5% at all sizes
- Paper gap for Inverse Correlated at n=20 is 60.8%; actual is 0%
- Paper shows gap decreasing with n (sometimes negative); actual gap is consistently small

---

### Table 3: B&B Nodes Explored at n=500

| Family | **Paper (Median / Max)** | **Actual (All n pooled)** | **Match?** |
|--------|---------------------------|---------------------------|------------|
| Uncorrelated | 576 / 1,156 | 138 / 1,156 | ❌ Median off 4× |
| Weakly Correlated | 795 / 3,881 | 224 / 2,985 | ❌ Median off 3.5× |
| Strongly Correlated | 1,023 / 39,840 | 1,032 / 39,840 | ✅ Max matches |
| Inverse Correlated | 556 / 25,231,225 | 562 / 25,231,225 | ✅ Close |
| Almost Equal Ratios | 288 / 10,139 | 291 / 10,139 | ✅ Close |

**Key Issue:** Paper says "at n=500" but medians don't match. Actual data pooled across all n.

---

### Figure 1: Time vs n (log-log)

Paper claims: "All algorithms scale near-linearly with n at fixed W. DP time is nearly family-independent. B&B variance is highest on Strongly Correlated."

**Actual data confirms near-linear scaling but:**
- DP time IS family-dependent at larger n (see DP scaling table)
- B&B variance is actually highest on Inverse Correlated (not Strongly Correlated)

---

### Section 5.2: Greedy Gap Findings

**Paper claims:**
- "Uncorrelated: Large gap at small n; gap shrinks at larger n"
- "Strongly Correlated: Gap small (2-13%) but nonzero"
- "Inverse Correlated: Gap extreme and variable"
- "Equal Ratios: Small gap at all sizes"

**Actual findings:**
- All gaps are small (< 5% median) at ALL sizes
- Inverse Correlated gap is consistently 0% (greedy finds optimal!)
- No "catastrophic failure" on Uncorrelated/Weakly Correlated
- Negative gaps in paper are mathematically impossible

---

### Section 5.3: B&B Search Effort

**Paper claims:**
- "Strongly Correlated: Many nodes despite tight bounds"
- "Inverse Correlated: Extreme variance; some instances require 25M+ nodes"
- "Equal Ratios: Moderate effort"

**Actual findings (all n pooled):**
- Strongly Correlated median: 1,032 (not "many nodes" - comparable to others)
- Inverse Correlated: Extreme variance CONFIRMED (max 25M+)
- Equal Ratios median: 291 (lowest of all)

---

### Section 6.1: Algorithm Selection Guide

**Paper recommends:**
| Instance Property | Recommended Algorithm |
|-------------------|----------------------|
| Small W (≤ 10⁴), exact needed | DP |
| Strongly Correlated (v ≈ w) | Greedy (near-optimal, instant) |
| Inverse Correlated | Avoid Greedy; DP if W small, else B&B with caution |
| Nearly equal ratios | DP (B&B struggles with weak bounds) |
| Large n, approximate OK | Greedy (if not Inverse Correlated) |

**Actual data suggests:**
| Instance Property | Recommended Algorithm |
|-------------------|----------------------|
| Small W (≤ 10⁴), exact needed | DP |
| **All families** | Greedy is near-optimal (gap < 5%) |
| Inverse Correlated | **Greedy actually optimal (0% gap)** |
| Nearly equal ratios | Greedy fine (gap ~1%) |
| Large n, exact needed | DP |

**Major contradiction:** Paper says "Avoid Greedy on Inverse Correlated" but actual data shows Greedy finds optimal on Inverse Correlated!

---

## Root Cause Analysis

The paper numbers **do not come from the current codebase**. Possible causes:
1. Paper was written from a different (buggy) experiment run
2. Paper numbers were manually edited/fabricated
3. Paper used different instance parameters (different seed, different W, different n values)
4. Paper used a different algorithm implementation

---

## Recommendation

**Do not use the current paper numbers.** The paper must be updated with actual experimental results from the canonical pipeline:

1. Run: `./build_and_run.sh 20,50,100,200,500 1000 30 42`
2. Analyze: `python3 analyze.py results/full_experiment.csv`
3. Copy `tables/*.tex` into paper
4. Rewrite all numerical claims in paper to match actual data

---

## Files to Update in Paper

- `paper/draft.md` - All tables, figures references, numerical claims
- Any LaTeX source files referencing the old numbers