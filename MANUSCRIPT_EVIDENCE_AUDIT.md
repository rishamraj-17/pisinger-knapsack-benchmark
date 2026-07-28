# Manuscript Evidence Audit

## Scope

Two manuscripts exist in this repository:

| Manuscript | Path | Focus |
|---|---|---|
| **Narrative draft** | `paper/draft.md` | Classical 0/1 Knapsack empirical comparison (Greedy, DP, B&B) |
| **Submission manuscript** | `Submission_Package/manuscript.tex` | ML/statistical modeling of algorithmic performance |

The issue list primarily concerns the **Submission Package** (`manuscript.tex`), but some items apply to both.

---

## P0 — Must resolve before submission

### P0-1: MKP → 0/1 Knapsack

**Evidence:** The manuscript.tex uses "multidimensional knapsack problem" (MKP) in:
- Title: "The Predictive Value of Internal Execution Metrics **in the Multidimensional Knapsack Problem**"
- Abstract (lines 18, 36)
- Introduction (line 42)
- Conclusion (line 187)
- Keywords (line 36)

The benchmark uses **single-dimension 0/1 Knapsack** (Pisinger's 5 families, single capacity constraint W). The Java source code at `src/main/java/algorithms/` implements standard 0/1 Knapsack DP, Greedy, and B&B — no multiple dimensions.

**Verdict: VERIFIED — Terminology error**

**Root cause:** The Submission_Package manuscript appears to have been written assuming a Multidimensional Knapsack Problem framing, but the experimental benchmark is exclusively the 0/1 (single-dimension) Knapsack. Pisinger families are defined for the 0/1 Knapsack.

**Files requiring modification:** `Submission_Package/manuscript.tex` — Title, abstract, keywords, introduction, conclusion, and all occurrences of "multidimensional knapsack"

**Impact: Affects scientific framing.** The paper claims to study MKP but actually studies 0/1 Knapsack. This changes the scope and generalizability claims.

---

### P0-2: Dataset size (6,000 vs 18,000+)

**Evidence:**

| Source | Claim | Actual |
|---|---|---|
| `paper/draft.md` line 22 | "5 families × 6 sizes × 100 seeds = 3,000 instances per mode (6,000 total) (18,000 algorithm runs)" | ✅ **Confirmed** |
| `manuscript.tex` line 24 | "benchmark of 6,000 knapsack instances" | ✅ **Confirmed** |
| `manuscript.tex` line 76 | "6,000 knapsack instances" | ✅ **Confirmed** |
| `manuscript.tex` line 77 | "six distinct structural classes (1,000 instances each)" | ❌ **FALSE** |

Verified from `results/instances.csv`:
- 3,000 `instance_id`s (unique seed × family × n combinations)
- 6,000 rows (3,000 × 2 capacity modes: fixed and scaled)
- 5 families (Uncorrelated, WeaklyCorrelated, StronglyCorrelated, InverseCorrelated, AlmostEqualRatios)
- 1,200 rows per family (5 × 1200 = 6,000)
- `out/results/full_experiment.csv`: 18,001 lines = 1 header + 18,000 data rows (6,000 instances × 3 algorithms)

**Verdict: PARTIALLY CORRECT** — 6,000 total instances and 18,000 algorithm runs are correct, but manuscript.tex incorrectly claims **6 families** of 1,000 each (should be **5 families** of 1,200 each).

**Root cause:** The manuscript.tex describes a "subset_sum" family that does not exist in the data. The actual Pisinger generator produces 5 families.

**Files requiring modification:**
- `Submission_Package/manuscript.tex` line 77: "six families" → "five families", correct family names
- `paper/draft.md` line 22: Already correct

**Impact: Affects scientific accuracy.** Incorrect family count and names misrepresent the dataset.

---

### P0-3: Arithmetic inconsistencies

**Evidence:** All claims verified against `Phase_3_3_Modeling/Phase3_Freeze/output/results/`:

| Claim (manuscript.tex) | Location | Data value | Matches? |
|---|---|---|---|
| DP runtime adj R² M1 = 0.978 | §4.1 | 0.97768 | ✅ ≈0.978 |
| Greedy runtime adj R² M1 = 0.856 | §4.1 | 0.85629 | ✅ |
| B&B runtime adj R² M1 = 0.743 | §4.1 | 0.74345 | ✅ |
| B&B nodes adj R² M1 = 0.735 | §4.1 | 0.73451 | ✅ |
| DP memory adj R² M1 = 0.008 | §4.1 | 0.00818 | ✅ ≈0.008 |
| Greedy gap pseudo-R² M1 = 0.216 | §4.1 | 0.21555 | ✅ ≈0.216 |
| DP fill_rate pseudo-R² M1 = 0.253 | §4.1 | 0.25261 | ✅ ≈0.253 |
| **ΔR²_adj B&B log_nodes = 0.243** | §4.2 | **0.24479** | ❌ **Should be 0.245** |
| **ΔR²_adj B&B log_time = 0.216** | §4.2 | **0.21747** | ❌ **Should be 0.217** |
| **Δpseudo-R² Greedy gap = 0.057** | §4.2 | **0.05752** | ❌ **Should be 0.058** |
| Greedy runtime ΔR²_adj = 0.001 | §4.2 | 0.00140 | ✅ |
| DP runtime ΔR²_adj = 0.001 | §4.2 | 0.00129 | ✅ |
| VIF-thinned ΔR² nodes: 0.243→0.237 | §4.4 | 0.24479→0.237 | Cannot verify (VIF file missing) |

**Verdict: VERIFIED with three minor rounding errors**

**Root cause:** The three ΔR² values (0.243, 0.216, 0.057) appear to have been rounded inconsistently or from a different run.

**Files requiring modification:** `Submission_Package/manuscript.tex` lines 136-137

**Impact: Presentation only.** Changes are at the 0.001 level — no scientific conclusions affected.

---

## P1 — Strong reviewer concerns

### P1-4: RQ1 coverage

**Evidence:** The manuscript.tex defines three research questions:
- RQ1: "How are instance characteristics associated with observed problem hardness across the benchmark dataset?"
- RQ2: "What is the baseline predictability using only instance characteristics?"
- RQ3: "To what extent do internal execution metrics provide additional explanatory power?"

The Results section (§4) has subsections:
- §4.1: "Baseline Performance (RQ2)" — addresses RQ2
- §4.2: "Incremental Contribution" — addresses Sub-RQ3a
- §4.3: "Important Predictors" — addresses Sub-RQ3b
- §4.4: "Model Robustness" — addresses Sub-RQ3c

**There is no dedicated subsection for RQ1.** The conclusion (line 187) briefly mentions "structural dataset characteristics... were strongly associated with observed problem hardness" as the RQ1 finding, but this is not supported by any results section that addresses RQ1 directly.

The paper/draft.md has a single RQ which is addressed by all results sections.

**Verdict: VERIFIED — RQ1 lacks dedicated results coverage.**

**Root cause:** The manuscript structure was designed for RQ2/RQ3 focus, but RQ1 was retained as a research question without dedicated analysis.

**Files requiring modification:** `Submission_Package/manuscript.tex` — Either:
(a) Add an EDA/results subsection addressing RQ1 (recommended), or
(b) Remove RQ1 and renumber to RQ1→RQ2

**Impact: Affects scientific structure.** The research questions must match the results.

---

### P1-5: LOFO vs full-sample reporting

**Evidence:** 
- manuscript.tex §3.2 states: "Evaluation employed **Leave-One-Family-Out (LOFO)** cross-validation"
- However, §4 (Results) reports **full-sample** R² values (Table 2)
- The LOFO R² values are dramatically different from full-sample:
  - DP memory: LOFO R² = **-107.6** (M1), full-sample = **0.015**
  - Greedy runtime: LOFO R² = **-4.66** (M1), full-sample = **0.857**
  - B&B log_time M2: LOFO R² = **-0.174**, full-sample = **0.961**
  - B&B log_nodes M2: LOFO R² = **-0.439**, full-sample = **0.980**

The paper states LOFO is the primary evaluation but **reports full-sample R²** in all key results. The negative LOFO R² values suggest the models fail to generalize to held-out families, but this critical finding is not discussed.

**Verdict: VERIFIED — LOFO vs full-sample reporting is contradictory.**

**Root cause:** The methodology section describes LOFO as the evaluation framework, but the Results section defaults to full-sample metrics. The LOFO results are dramatically worse but not reported in the main text.

**Files requiring modification:** `Submission_Package/manuscript.tex` — Need to:
1. Report both LOFO and full-sample metrics, or
2. Use LOFO consistently and explain the discrepancy, or
3. Use full-sample with justification

**Impact: Affects scientific conclusions.** The LOFO results fundamentally contradict the predictive power claims made in the abstract.

---

### P1-6: Abstract wording

**Evidence:** The abstract states: "deterministic runtimes ($R^2_{adj} \ge 0.856$), but substantially lower for heuristic optimality gaps"

DP memory (`log_memory_mb`) is a deterministic runtime outcome with adj R² = 0.008 — **far below 0.856**. The "≥ 0.856" claim excludes the DP memory model.

The paper cites "Greedy and Dynamic Programming runtime" as having ΔR²_adj = 0.001, but B&B is also a deterministic runtime algorithm — its ΔR²_adj is 0.217-0.245, which contradicts "negligible improvement for deterministic runtimes."

**Verdict: PARTIALLY CORRECT** — The abstract over-generalizes by omitting the DP memory counterexample and conflating "deterministic runtime" with "predictable runtime."

**Root cause:** DP memory is classified as a "deterministic runtime" outcome but has near-zero predictability. The abstract's "deterministic runtimes" phrasing implicitly excludes DP memory.

**Files requiring modification:** `Submission_Package/manuscript.tex` abstract (lines 17-33)

**Impact: Affects scientific accuracy.** The abstract claims are broader than the evidence supports.

---

## P2 — Verify before changing

### P2-7: Table 4 / Figure 1 discussion

**Evidence:** Two claims are made about Table 4:

1. **"bound_gap_variance and sum_improvement_amount exhibited the largest absolute standardized β values among the appended execution metrics"** (line 145)
2. Table 4 is described as "Top-10 standardized β coefficients" but:

From `standardized_beta_BandB_log_nodes_explored.csv`, execution metric |β| values:
- final_queue_size: **0.511** (rank 8, in Table 4)
- pruned_by_cap: **0.492** (rank 9, in Table 4)
- bound_gap_variance: **0.419** (rank 10, in Table 4)
- sum_improvement_amount: **0.409** (rank 15, **NOT in Table 4**)
- right_branches: **0.375** (rank 16, NOT in Table 4)

Claim (1) is **incorrect** — bound_gap_variance and sum_improvement_amount are NOT the largest among execution metrics. final_queue_size (0.511) and pruned_by_cap (0.492) are larger.

Claim (2) about `sum_improvement_amount` being in Table 4 is **incorrect** — it's not in the top-10 table.

Note: `sum_improvement_amount` exists in the data and is a valid predictor, but it's not in Table 4.

**Verdict: VERIFIED — Text does not accurately reflect Table 4.**

**Root cause:** The text was written based on a different ranking or draft of the table.

**Files requiring modification:** `Submission_Package/manuscript.tex` lines 145, 148, 163, and `Submission_Package/tables/Table_4.tex`

**Impact: Presentation only.** `sum_improvement_amount` is a valid predictor in the model; its importance is just not in the top-10 table.

---

### P2-8: DP memory result (adj R² ≈ 0.008)

**Evidence:** From `ols_metrics_DP_log_memory_mb.csv` (full_sample):
- M1: R² = 0.0151, adj R² = **0.00818**
- M2: R² = 0.0163, adj R² = **0.00785**
- ΔR²_adj = **-0.00033** (essentially zero)

LOFO results: R² = **-107.6** (M1), **-110.4** (M2) — catastrophic failure.

Delta-R² partitioning for DP log_memory_mb: `delta_r2_partitioning_DP_log_memory_mb.csv`:
```
M1 full R² = 0.01512, M2 full R² = 0.01629, ΔR² = 0.00105 (rank 3)
```

Block 1 (instance characteristics) should explain most of the 0.015 R². Block 3 (DP execution metrics) contributes negligible ΔR².

**Root cause:** DP memory is primarily driven by n × W (table size), which is deterministic from the instance parameters. Instance-level features like `total_weight`, `capacity`, and `n` already capture this structure. The small R² reflects that with `cells_allocated` and `zero_value_states` excluded from M1 (to avoid circularity), the remaining 24 instance-level predictors have only a weak linear relationship with log_memory_mb.

**Verdict: VERIFIED — Expected, not an error.** The near-zero predictability is expected because:
1. DP memory is essentially deterministic (n × W), captured by trivial predictors
2. Circularity exclusions remove the direct table-dimension predictors
3. The remaining 24 instance characteristics are weak proxies for the actual table size

**Impact: No fix needed.** This is a correct finding that should be reported as-is. The manuscript already flags this as "negligible predictive performance."

---

### P2-9: Broken citation

**Evidence:** Searched both manuscripts and all files for `(author?)` pattern:
- `paper/draft.md` — Not found
- `Submission_Package/manuscript.tex` — Not found
- `Submission_Package/references.bib` — All entries have complete author fields

The draft.md reference [4] "Horowitz, E., & Sahni, S. (1974)" is complete and correct. The manuscript.tex uses `\cite{Horowitz1974}`-style citations through natbib.

**Verdict: FALSE POSITIVE** — No broken citation exists in the current codebase.

**Root cause:** The `(author?) [4]` placeholder was likely already fixed in a previous revision.

**Impact: No modification required.**

---

## Family name discrepancies (cross-cutting)

In addition to the above issues, a significant discrepancy exists between the two manuscripts and the data:

| Actual data | `paper/draft.md` | `manuscript.tex` |
|---|---|---|
| Uncorrelated | Uncorrelated | uncorrelated |
| WeaklyCorrelated | Weakly Correlated | weakly_correlated |
| StronglyCorrelated | Strongly Correlated | strongly_correlated |
| InverseCorrelated | Inverse Correlated | **inverse_strongly_correlated** |
| AlmostEqualRatios | Almost Equal Ratios | **almost_strongly_correlated** |
| *(none)* | *(none)* | **subset_sum** (does not exist) |
| 5 families | 5 families | **6 families** (wrong) |

The `manuscript.tex` family names "Inverse Strongly Correlated" and "Almost Strongly Correlated" do not match the data's "InverseCorrelated" and "AlmostEqualRatios". The "subset_sum" family does not exist in the generated instances.

---

## Summary of required modifications

| # | Issue | Verdict | Files | Scientific impact |
|---|---|---|---|---|
| P0-1 | MKP → 0/1 Knapsack | **Verified** | `Submission_Package/manuscript.tex` (title, abstract, intro, kw, conclusion) | **Scientific framing** |
| P0-2 | 6 vs 5 families | **Partially Correct** | `Submission_Package/manuscript.tex` line 77 | **Scientific accuracy** |
| P0-3 | Rounding errors (×3) | **Verified** | `Submission_Package/manuscript.tex` lines 136-137 | Presentation only |
| P1-4 | RQ1 missing coverage | **Verified** | `Submission_Package/manuscript.tex` §4 | **Scientific structure** |
| P1-5 | LOFO vs full-sample | **Verified** | `Submission_Package/manuscript.tex` §3.2, §4 | **Scientific conclusions** |
| P1-6 | Abstract over-generalizes | **Partially Correct** | `Submission_Package/manuscript.tex` abstract | **Scientific accuracy** |
| P2-7 | Table 4 / Figure 1 mismatch | **Verified** | `Submission_Package/manuscript.tex` lines 145,148,163 | Presentation only |
| P2-8 | DP memory adj R² ≈ 0.008 | **Verified (expected)** | None needed | — |
| P2-9 | Broken citation | **False Positive** | None needed | — |

## Cross-cutting issues

- **Family names:** `Submission_Package/manuscript.tex` uses wrong family names (lines 77, 97, 100, 155, 169)
- **Capacity mode descriptions:** Verify that manuscript.tex correctly describes fixed (W=1000) and scaled (W=0.5×sum) modes
- **Two-manuscript alignment:** The `paper/draft.md` and `Submission_Package/manuscript.tex` describe fundamentally different studies — one about algorithm comparison, the other about ML performance prediction
