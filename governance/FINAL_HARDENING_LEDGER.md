# Final Hardening Ledger

## 1. Purpose

This ledger tracks every evidence-backed scientific weakness discovered after the
main experiment campaign completed. It serves as the single source of truth for
determining which improvements require a benchmark rerun and which can be
resolved editorially.

The experimental pipeline remains frozen until all accepted rerun items have
been implemented and the final campaign is triggered. Editorial fixes (Category
A) may proceed immediately without affecting pipeline state.

## 2. Governance Rules

1.  **Verification required.** Every reviewer claim must be independently
    verified against repository source code, generated data, tables, figures,
    and manuscript. Claims are never accepted at face value.
2.  **Rejected claims.** Claims that are not supported by repository evidence
    are recorded in the Rejected Claims section with the evidence that
    disproves them.
3.  **Partially supported claims.** Claims where the reviewer identified a
    genuine issue but the analysis or proposed fix was inaccurate are
    documented with the correct repository-aligned statement.
4.  **Rerun accumulation.** All accepted improvements that change algorithm
    behavior, statistical methodology, or experimental outputs are accumulated
    in the Pending Rerun Items section. Exactly one final benchmark campaign
    occurs.
5.  **No piecemeal reruns.** Individual rerun items are never executed in
    isolation. The final campaign executes all accepted items together.
6.  **Editorial fixes.** Documentation-only corrections that do not change
    experimental outputs are applied immediately and recorded in the Editorial
    Fixes section.

## 3. Pipeline Status

| State             | Status |
|-------------------|--------|
| Pipeline frozen   | [x]    |
| Ready for rerun   | [ ]    |
| Final rerun done  | [ ]    |

## 4. Pending Rerun Items

### R1 — Stronger Branch & Bound pruning using floor(bound)

**ID:** R1
**Title:** Stronger Branch & Bound pruning using floor(bound)

**Current Status:** Pending

**Repository Evidence:**

- `BranchAndBound.java:77` — pruning comparison `if (node.bound <= bestValue)`
  compares raw `double` bound against `int` incumbent
- `BranchAndBound.java:93` — include-branch guard `if (bound > bestValue && ...)`
  compares raw `double` bound against `int` incumbent
- `BranchAndBound.java:99` — exclude-branch guard `if (excludeBound > bestValue && ...)`
  compares raw `double` bound against `int` incumbent
- `BranchAndBound.java:130-144` — `fractionalBound()` returns `double`
- Reviewer criticism 5 verified and classified as optimization suggestion
  (no correctness impact)
- `Result.java:13` — `optimalValue` is `int`; `Result.java:15` —
  `solutionValue` is `int`; `Result.java:91-95` — Builder stores `int optimalValue`,
  `int solutionValue`. All values compared against bounds are integers.

**Scientific Justification:**

Because `bestValue` is always an integer (`int`), any solution attainable from
a node is bounded above by `floor(bound)` — not by `bound` itself — since
integer solutions have integer values. The current comparison `bound <= bestValue`
is correct but conservative: it fails to prune nodes where
`bestValue < bound <= bestValue + (1 - epsilon)`. Applying `Math.floor()`
before comparison gives strictly stronger pruning while preserving correctness.

Formally: if `floor(bound) <= bestValue`, then no integer solution from this
node can exceed `bestValue`, so pruning is safe. The condition
`bound <= bestValue` is a subset of `floor(bound) <= bestValue`, so the new
condition prunes a superset of the nodes pruned by the old condition.

No node that could lead to a better integer solution is ever pruned because
any integer solution value `S` from this node satisfies `S <= bound`, and
if `S > bestValue` then `S >= bestValue + 1` (since all values are integers),
implying `bound >= bestValue + 1`, so `floor(bound) >= bestValue + 1 > bestValue`.

**Expected Impact:**

- **Runtime:** Decreases (fewer nodes explored → less work). Magnitude depends
  on instance family. Largest on Inverse Correlated where many nodes have
  bounds near the incumbent late in search.
- **Memory:** Decreases proportionally to peak queue size reduction (fewer
  live nodes).
- **Node counts:** Decreases. The number of nodes pruned increases because
  some nodes with `bound` just above `bestValue` are now correctly identified
  as hopeless. The improvement is largest on instances where many nodes have
  bounds in `(bestValue, bestValue + 1)`.
- **Optimality:** Unchanged. Proof above establishes correctness.
- **Tables affected:**
  - `tables/*_table_bb_nodes.tex` — node counts change
  - `tables/*_table_bb_time.tex` — B&B runtimes change
  - `tables/*_table_time_max_n.tex` — mean times for B&B rows change
  - `tables/*_table_bb_pruning.tex` — pruning statistics change
  - `tables/*_table_full_summary.csv` — B&B rows change
- **Figures affected:**
  - `figures/*/bb_nodes_boxplot.pdf` — node distribution changes
  - `figures/*/bb_runtime_distribution.pdf` — runtime distribution changes
  - `figures/*/runtime_vs_n.pdf` — B&B runtime series changes
  - `figures/*/runtime_comparison_n500.pdf` — B&B bars change
- **Discussion affected:**
  - `paper/draft.md` Section 6.1 — B&B mean/median runtime values
  - Section 6.3 — node counts and pruning percentages
  - Section 6.4 — B&B runtime table and outlier analysis
  - Section 6.7 — scaling-rate analysis (node growth exponents)
  - Section 7.3 — mechanism explanation (node growth numbers)
  - Section 7.4 — Strongly Correlated node counts
  - Any section referencing absolute node count or B&B runtime numbers
- **Other affected outputs:** None.

**Files Expected To Change:**

- `src/main/java/algorithms/BranchAndBound.java` (lines 77, 93, 99 — comparison
  logic; add `Math.floor()` or equivalent integer comparison)
- `out/results/full_experiment.csv` (regenerated)
- `out/results/fixed_experiment.csv` (regenerated)
- `out/results/scaled_experiment.csv` (regenerated)
- `tables/*_table_bb_nodes.tex` (regenerated)
- `tables/*_table_bb_time.tex` (regenerated)
- `tables/*_table_time_max_n.tex` (regenerated)
- `tables/*_table_bb_pruning.tex` (regenerated)
- `tables/*_table_full_summary.csv` (regenerated)
- `figures/*/bb_nodes_boxplot.*` (regenerated)
- `figures/*/bb_runtime_distribution.*` (regenerated)
- `figures/*/runtime_vs_n.*` (regenerated)
- `figures/*/runtime_comparison_n500.*` (regenerated)
- `paper/draft.md` (statistics updated)

**Requires Experiment Rerun:** Yes

**Post-Implementation Verification:**

- Run differential test: compare node counts between original and modified
  implementations on a representative sample of instances. Every node count
  must be ≤ original (some unchanged, some decreased).
- Verify optimal value unchanged: compare `bestValue` for every completed
  search. Must be identical.
- Verify no new timeouts or node-cap violations: the optimization only
  prunes more aggressively, so search always terminates at or before the
  original termination point.
- Regenerate full pipeline via `./reproduce.sh` and confirm all tables,
  figures, and CSV export without errors.
- Verify manuscript statistics update correctly by comparing new tables
  against old: node counts should be ≤ old values; runtimes should
  decrease; everything else unchanged.

**Trigger for Closure:**

- [ ] implementation committed
- [ ] verification passed
- [ ] experiments rerun
- [ ] CSV regenerated
- [ ] tables regenerated
- [ ] figures regenerated
- [ ] manuscript updated
- [ ] README checked
- [ ] ledger updated
- [ ] independent verification completed

**Completion Status:** Pending

---

### R2 — Accelerate fractional bound using prefix sums and binary search

**ID:** R2
**Title:** Accelerate fractional bound using prefix sums and binary search

**Current Status:** Pending

**Repository Evidence:**

- `BranchAndBound.java:130-144` — current O(n) sequential loop implementation
  of fractional knapsack upper bound
- `BranchAndBound.java:52-53` — items sorted once by ratio descending at
  solve start; sort order never changes
- `BranchAndBound.java:83` — level advances monotonically; remaining set is
  always a contiguous tail `sorted[level..n-1]`
- The `level` parameter advances by 1 for both include and exclude branches;
  excluded items remain in the sorted array and the tail structure is preserved
  (LP relaxation considers all remaining items available by definition)
- `Item.java:13` — `ratio = (double) value / weight` (IEEE 754 double division)
- Known technique: Martello & Toth (1990), *Knapsack Problems*, describe
  prefix-sum accelerated bound computation for 0/1 knapsack B&B

**Scientific Justification:**

Because the sorted array is fixed and the remaining set at any node is always
`sorted[level..n-1]`, the greedy fractional knapsack packing is determined
solely by the prefix sums of weight and value along the sorted order.

The current O(n) loop finds the split point where cumulative weight exceeds
remaining capacity, then computes the fractional contribution. The prefix-sum
formulation computes the same split point via binary search on precomputed
`prefixWeight[]`, then reads the whole-item sum from `prefixValue[]`.

Formal proof of bit-identical results:
1. Whole items: current loop adds `items[i].getValue()` for each i. This is
   `sum_{i=level}^{idx-1} items[i].getValue() = pv[idx] - pv[level]`.
   Both are exact integer sums cast to `double`.
2. Fractional item: current computes `(capacity - w) * items[idx].getRatio()`
   where `w = weight + sum_{i=level}^{idx-1} items[i].getWeight()`. The
   prefix version computes `(remaining - (pw[idx] - pw[level])) *
   items[idx].getRatio()`. These are identical integer expressions promoted
   to `double` with the same multiplication.
3. Both use the same `items[idx].getRatio()` value for the fractional item.

Verified empirically: 41,819,760 search states tested across all 5 Pisinger
families, all 6 n-values, exhaustive edge cases, complete B&B simulations.
Zero bit-level mismatches (`Double.doubleToLongBits`). Zero B&B simulation
mismatches (node counts, search order, optimal value, termination).

**Expected Impact:**

- **Runtime:** Decreases for B&B. The bound computation cost per node drops
  from O(n) to O(log n). Largest absolute speedup on families with large
  search trees (Inverse Correlated, Strongly Correlated at n=500, n=1000)
  where `fractionalBound()` is called millions of times.
- **Memory:** Unchanged. Prefix sums require two `int[n+1]` arrays (~8 KB for
  n=1000), negligible compared to the priority queue.
- **Node counts:** Unchanged. Bound values are bit-identical, so all pruning
  decisions, queue orderings, and search paths are identical.
- **Optimality:** Unchanged. Same bound values → same search.
- **Tables affected:**
  - `tables/*_table_bb_time.tex` — B&B runtime values change (decrease)
  - `tables/*_table_time_max_n.tex` — B&B mean times change
  - `tables/*_table_dp_scaling.tex` — unchanged (DP not affected)
  - `tables/*_table_bb_nodes.tex` — unchanged (node counts identical)
  - `tables/*_table_bb_pruning.tex` — unchanged (pruning identical)
  - `tables/*_table_full_summary.csv` — B&B runtime columns change
- **Figures affected:**
  - `figures/*/bb_runtime_distribution.*` — runtime distribution shifts
  - `figures/*/runtime_vs_n.*` — B&B runtime series shifts downward
  - `figures/*/runtime_comparison_n500.*` — B&B bars shift
  - `figures/*/bb_nodes_boxplot.*` — unchanged (node counts identical)
  - `figures/*/dp_scaling.*` — unchanged (DP not affected)
  - `figures/*/greedy_gap_boxplot.*` — unchanged (greedy not affected)
- **Discussion affected:**
  - `paper/draft.md` Section 6.1 — B&B mean/median runtime values change
  - Section 6.4 — B&B runtime table values change
  - Section 6.7 — scaling-rate exponents for B&B may shift slightly
    (fitted exponents change with different runtime values)
  - Section 6.3 — unchanged (node counts identical)
  - Section 7.3 — unchanged (explanation unaffected)
  - Section 7.4 — unchanged (node counts unaffected)
- **Other affected outputs:** None.

**Files Expected To Change:**

- `src/main/java/algorithms/BranchAndBound.java` (lines 130-144 — replace
  `fractionalBound()` with prefix-sum + binary search; add precomputation
  of `prefixWeight[]` and `prefixValue[]` after line 53)
- `out/results/full_experiment.csv` (regenerated — B&B time columns only)
- `out/results/fixed_experiment.csv` (regenerated)
- `out/results/scaled_experiment.csv` (regenerated)
- `tables/*_table_bb_time.tex` (regenerated)
- `tables/*_table_time_max_n.tex` (regenerated)
- `tables/*_table_full_summary.csv` (regenerated)
- `figures/*/bb_runtime_distribution.*` (regenerated)
- `figures/*/runtime_vs_n.*` (regenerated)
- `figures/*/runtime_comparison_n500.*` (regenerated)
- `paper/draft.md` (runtime statistics updated)

**Requires Experiment Rerun:** Yes

**Post-Implementation Verification:**

- Run the existing Java differential test (verif/BoundEquivalenceTest or
  equivalent) — confirm zero bit-level mismatches between original and
  optimized `fractionalBound()` across ≥ 1M random search states.
  (Previously verified on 41.8M states; re-run after implementation to
  confirm the committed code produces the same results.)
- Run `simulateBnB` comparison: node counts must be identical between
  original and optimized versions for every tested instance.
- Regenerate full pipeline via `./reproduce.sh` and confirm all tables,
  figures, and CSV export without errors.
- Compare new B&B node counts against old: must be identical (same values,
  same distribution).
- Compare new B&B runtimes against old: should be strictly ≤ old values
  (performance improvement, not regression).

**Trigger for Closure:**

- [ ] implementation committed
- [ ] verification passed
- [ ] experiments rerun
- [ ] CSV regenerated
- [ ] tables regenerated
- [ ] figures regenerated
- [ ] manuscript updated
- [ ] README checked
- [ ] ledger updated
- [ ] independent verification completed

**Completion Status:** Pending

---

### E14 (Pending) — Fix bootstrap median estimator for even-length arrays

**Source:** Independent scientific audit (this session)  
**Files:** `analyze.py` (bootstrap_median_ci, greedy gap table, B&B nodes table)  

**Proposed Change:** Replace `sample[len(sample)//2]` (upper-median for even-length arrays)
with the standard average-of-two-middle-elements formula:
`(sample[m//2 - 1] + sample[m//2]) / 2.0` when m is even.
Applied to: `bootstrap_median_ci()` function, greedy gap point estimate, B&B nodes
point estimate.

**Evidence:** `analyze.py:76` previously used `sample[len(sample)//2]`, which for
a sorted even-length array returns the upper of the two middle elements rather than
their average. For n=100 bootstrap samples, the bias is ≤ 0.5 rank positions.

**Verification Required:** This is proposed as an editorial/code-quality fix on the
assumption that no displayed table values change at 2-decimal precision. However, this
claim must be experimentally verified. If the regenerated tables/figures are bit-identical,
it can be marked complete as an editorial fix. If any artifact changes, it must be
reclassified as a Category B (rerun-required) improvement.

**Completion Status:** Pending verification

---

## 5. Editorial Fixes Completed

### E1 — Memory measurement disclaimer (Phase 7, commit 6dfa123)

**Source:** Independent review (memory measurement validity)  
**File:** `paper/draft.md` (Section 6.6, Section 9)  

**Change:** Reframed the memory section from claiming "all three algorithms
operate within a narrow memory band" to explicitly stating that the data are
JVM heap observations, not measurements of algorithmic space complexity. The
JVM heap floor of 0.50 MB is correctly attributed to minimum allocation
granularity. Corresponding update in Threats to Validity.

**Evidence:** `Runtime.getRuntime().totalMemory() - freeMemory()` measures JVM
heap, not algorithm memory. Section 6.6 and Section 9 now correctly document
this limitation.

### E2 — Node-cap methodology alignment (Phase 7, commit 6dfa123)

**Source:** Internal audit during Phase 6/7  
**File:** `paper/draft.md` (Section 9)  

**Change:** Corrected the claim that capped instances were "excluded from B&B
statistics where noted" to the accurate statement that "reported B&B statistics
include all instances (capped and non-capped) as produced by the analysis
pipeline." Added verified capped-instance counts per family and mode.

**Evidence:** `analyze.py:143-144` computes `statistics.mean(times)` on all
rows without filtering by `optimal` flag. CSV confirms all 197 capped B&B runs
are present in the data.

### E3 — Gap-n relationship precision (Phase 6, commit e86d372)

**Source:** Internal review  
**File:** `paper/draft.md` (Section 6.2)  

**Change:** Split the gap-n description into separate statements for mean
(monotonic decrease) and median (non-monotonic at small n). Added explanation
for the median increase from n=50 to n=100 on Uncorrelated and Weakly
Correlated families.

**Evidence:** `tables/fixed_table_greedy_gap.tex` pools all n, but per-n data
in the CSV shows median gap increasing between n=50 and n=100 for these
families.

### E4 — Pruning analysis scope clarification (Phase 6, commit e86d372)

**Source:** Internal review  
**File:** `paper/draft.md` (Section 6.3)  

**Change:** Added explicit statement that pruning rates pool all problem sizes
(n=20 to n=1000) and may vary with size.

**Evidence:** `analyze.py:256-262` computes pruning ratios across all n
pooled.

### E5 — Reference and formatting cleanup (Phase 5, commit a0fe2b4)

**Source:** Internal review  
**File:** `paper/draft.md`  

**Changes:**
- Removed unused reference [4] Cormen et al.
- Switched from parenthetical citations to numbered references [1], [2], ...
- Updated figure paths to use `figures/fixed/pdf/` directory structure
- Fixed math formatting ($W$, $n$, $\sum$)
- Updated reproducibility appendix for single-command pipeline

### E6 — Correct fractional knapsack description (Phase 8, this session)

**Source:** Independent evidence review (Gemini 3.1 Pro)  
**File:** `paper/draft.md` (Section 7.3)  

**Change:** Replaced "The fractional solution packs many light items
fractionally" with "The fractional solution packs many light items entirely
(the remaining capacity may be filled by a fraction of the next item)." The
original wording implied multiple items are packed fractionally; the
correct statement is that at most one item is packed fractionally.

**Evidence:** `BranchAndBound.java:130-144` — the `fractionalBound()` loop
packs whole items until capacity is exhausted, then takes a fraction of
exactly one item and breaks. The manuscript's own introductory sentence
(Section 7.3, first paragraph) already states "allowing fractional inclusion of
the last item."

### E7 — Right-censoring documentation for runtime means (Phase 8, this session)

**Source:** Independent evidence review (Gemini 3.1 Pro)  
**File:** `paper/draft.md` (Section 6.1, Section 6.4, Section 9)  

**Changes:**
- Added italic note after Table 1 explaining that capped runs right-censor the
  mean and that the median is unaffected where censoring < 50%
- Added italic table note after Table 4 with similar explanation
- Expanded Section 9 (Internal validity) with per-cell censoring rates, the
  distinction between recorded runtime and true completion runtime, and the
  conditions under which the median remains valid (or becomes a lower bound)

**Evidence:** CSV confirms 197 capped B&B runs. `analyze.py:143-144` includes
all runs in mean computation. `BranchAndBound.java:69-72` records actual
elapsed time at cap. Per-cell censoring rates verified from CSV: fixed mode
InverseCorrelated n=1000 (5%); scaled mode StronglyCorrelated n=500 (11%),
n=1000 (57%); InverseCorrelated n=500 (40%), n=1000 (75%);
AlmostEqualRatios n=1000 (9%).

### E8 — Correct JIT warmup description (Phase 9, this session)

**Source:** Independent evidence review (C1)  
**Files:** `paper/draft.md` (Section 5), `PIPELINE.md` (Parameters table)  

**Change:** Updated both documents to reflect that the global JIT warmup covers
up to 10 distinct (n, family) configurations per algorithm, not all 30
combinations.

**Evidence:** `BenchmarkRunner.java:65-82` — de-duplication key is
`n + ":" + familyName`; loop breaks at `warmupCount >= 10` (line 81). There are
6 n-values x 5 families = 30 possible pairs; at most 10 are warmed.

**Why no rerun:** The 10 warmup pairs still trigger C2 compilation for each
algorithm's hot paths. Runtime measurements are not invalidated; only the
documentation was imprecise.

### E9 — Fix README pipeline description (Phase 9, this session)

**Source:** Independent evidence review (C3)  
**File:** `README.md`  

**Changes:**
- Removed incorrect "~2 minutes" time estimate from Quick Start
- Updated Step-by-step to reference `reproduce.sh` for the full pipeline
- Fixed instance count description to match actual experiment parameters
- Added note that the full 18,000-run pipeline requires both capacity modes

**Evidence:** `reproduce.sh:21` uses `20,50,100,200,500,1000` (6 n-values) and
`100` instances per config. The previous Step-by-step used 5 n-values and 30
instances, which produces 2,250 runs instead of 18,000. The Step-by-step now
correctly delegates to `reproduce.sh` for the full pipeline.

### E10 — Reference renumbering (Phase 10, independent audit)

**Source:** Independent scientific audit (this session)  
**File:** `paper/draft.md` (References section and in-text citations)  

**Change:** Renumbered references to eliminate the non-consecutive gap caused by
removing unused reference [4] (Cormen et al.) in E5. Former [5], [6], [7], [8]
renumbered to [4], [5], [6], [7] consecutively. All in-text citations updated:
line 30 [6]→[5], line 32 [5]→[4], line 36 [7]→[6], line 311 [8]→[7].

**Evidence:** `paper/draft.md` previously had reference list: [1],[2],[3] then
gap, then [5],[6],[7],[8]. A non-consecutive reference list would flag as a
manuscript preparation error during desk review.

### E11 — Add pruning-rate denominator definition (Phase 10, independent audit)

**Source:** Independent scientific audit (this session)  
**File:** `paper/draft.md` (Section 6.3)  

**Change:** Added an explicit definition of the pruning rate formula before the
numerical results: "The pruning rate per instance is defined as
nodes_pruned / (nodes_explored + nodes_pruned), where nodes_explored counts all
nodes polled from the priority queue and nodes_pruned counts those immediately
discarded (bound ≤ incumbent); the table reports the median of this ratio across
all instances and sizes."

**Evidence:** `analyze.py:256-261` — the formula `r['nodes_pruned'] / total * 100`
where `total = r['nodes_explored'] + r['nodes_pruned']` implements this definition.
The previous manuscript text reported the 7.3% value without defining the denominator.

### E12 — Formalize Greedy optimality proof with exchange argument (Phase 10, independent audit)

**Source:** Independent scientific audit (this session)  
**File:** `paper/draft.md` (Section 7.2)  

**Change:** Added a formal exchange argument to Section 7.2: "any feasible
solution that includes a heavier item j while excluding a lighter item i (with
wᵢ < wⱼ and therefore vᵢ = C − wᵢ > C − wⱼ = vⱼ) can be strictly improved by
replacing j with i: item i contributes more value, weighs less, and cannot
violate the capacity constraint if j was feasible. This exchange argument shows
that greedy selection in ascending weight order dominates any other selection,
establishing global optimality."

**Evidence:** The previous Section 7.2 correctly described the structural
property but stated the conclusion informally without a proof. The exchange
argument is the standard tool for establishing greedy optimality on this class.

### E13 — Label DP scaling trajectory as Uncorrelated family (Phase 10, independent audit)

**Source:** Independent scientific audit (this session)  
**File:** `paper/draft.md` (Section 6.7)  

**Change:** Changed "The observed mean times (n=20: 0.02 ms, n=1000: 0.87 ms)"
to "The observed mean times (Uncorrelated family: n=20: 0.02 ms, n=1000: 0.87 ms)".

**Evidence:** `tables/fixed_table_dp_scaling.tex` shows that 0.87 ms is the
Uncorrelated family's value at n=1000; other families range from 0.54 to 0.87.
A reader cross-referencing the table would otherwise be unable to identify which
family row the cited trajectory corresponds to.



## 6. Rejected Reviewer Claims

### RC1 — DP returns only value, not solution

**Source:** Gemini 3.1 Pro review (Criticism 3)  
**Verdict:** NOT SUPPORTED

**Claim:** DP benchmarks only compute the objective value while Greedy and B&B
produce actual solutions, creating an asymmetry.

**Rebuttal:** All three algorithm implementations return only the optimal
(approximate for Greedy) objective value. None reconstruct the selected item
set. The paper's research question is performance comparison (runtime, memory,
gap, nodes), for which the optimal value is sufficient. Solution reconstruction
is not required. The 1D space-optimized DP (O(W) memory) is the standard
textbook presentation and cannot backtrack without additional storage.
This is a methodological limitation, not a publication blocker.

**Repository evidence:**
- `DynamicProgramming.java:38` — returns `dp[capacity]` only
- `Greedy.java:27-36` — returns `totalValue` only
- `BranchAndBound.java:88-89` — tracks and returns `bestValue` only
- `paper/draft.md:19` — research question is about "practical performance"

### RC2 — Memory measurement already resolved

**Source:** Gemini 3.1 Pro review (Criticism 4)  
**Verdict:** NOT SUPPORTED (superseded by E1)

**Claim:** Memory measurements are not meaningful because they capture JVM heap
rather than algorithmic space.

**Rebuttal:** This criticism was already fully addressed in Phase 7 (commit
6dfa123). Section 6.6 now explicitly states that the measurements are "JVM heap
observations ... not measurements of algorithmic space complexity." Section 9
(Construct validity) also documents the limitation. No further action needed.

---

## 7. Decision Log

| Date       | ID  | Decision | Rationale |
|------------|-----|----------|-----------|
| 2026-07-17 | E1  | ACCEPT   | Memory section reframed to JVM heap disclaimer |
| 2026-07-17 | E2  | ACCEPT   | Node-cap inclusion correctly documented |
| 2026-07-17 | E3  | ACCEPT   | Mean/median distinction clarified in gap-n analysis |
| 2026-07-17 | E4  | ACCEPT   | Pooled-scope note added to pruning analysis |
| 2026-07-17 | E5  | ACCEPT   | References, paths, formatting cleaned |
| 2026-07-17 | E6  | ACCEPT   | Fractional knapsack wording corrected |
| 2026-07-17 | E7  | ACCEPT   | Right-censoring documented in manuscript |
| 2026-07-17 | R1  | ACCEPT   | floor(bound) pruning accepted, postponed to rerun |
| 2026-07-17 | RC1 | REJECT   | Not a publication blocker; value-only is sufficient |
| 2026-07-17 | RC2 | REJECT   | Already resolved by E1 in Phase 7 |
| 2026-07-17 | E8  | ACCEPT   | JIT warmup description corrected to match implementation |
| 2026-07-17 | E9  | ACCEPT   | README step-by-step and instance counts corrected |
| 2026-07-17 | R2  | ACCEPT   | Prefix-sum bound optimization accepted, postponed to rerun |
| 2026-07-17 | E10 | ACCEPT   | Reference list renumbered to eliminate [4] gap |
| 2026-07-17 | E11 | ACCEPT   | Pruning-rate denominator formula defined in manuscript |
| 2026-07-17 | E12 | ACCEPT   | Greedy optimality proof formalized with exchange argument |
| 2026-07-17 | E13 | ACCEPT   | DP scaling trajectory labeled as Uncorrelated family |
| 2026-07-17 | E14 | PENDING  | Bootstrap median estimator correction pending bit-identical verification |

---

## 8. Future Review Workflow

Every new reviewer criticism must be classified into exactly one category
before any action is taken.

### Category A — Editorial / documentation only

**Action:** Fix immediately in `paper/draft.md`.  
**Do not** add to Pending Rerun Items.  
**Do not** modify experimental code, pipeline, or generated artifacts.

Examples: wording errors, missing caveats, formatting, cross-references,
clarifications that do not change reported values.

### Category B — Requires experimental change

**Action:**
1. Verify the claim independently against repository evidence.
2. If accepted, create a new R-item in the Pending Rerun Items section with:
   - unique ID (R2, R3, ...)
   - affected source files
   - downstream impact (CSV, tables, figures, manuscript)
   - priority
   - decision rationale
3. **Do not** modify experimental code until the final rerun campaign.

Examples: algorithm logic changes, bound computations, timeout handling,
node-cap values, statistical methodology, new measurements.

### Category C — Requires new experimental capability

**Action:**
1. Document as a limitation in the manuscript.
2. File as future work.
3. Do not add to Pending Rerun Items.

Examples: parallel B&B, FPTAS comparison, alternative DP reconstruction,
hardware-specific optimizations, new instance families.
