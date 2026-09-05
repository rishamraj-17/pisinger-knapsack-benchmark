# Phase 2.5 — Dataset Integration Governance Report

**Date:** 2026-07-20  
**Phase Lead:** AI Assistant (opencode)  
**Status:** Complete

---

## Objective

Unify the five CSV outputs into a single canonical dataset suitable for statistical analysis. The five source CSVs are:

| Source | Path | Rows | Cols | Content |
|---|---|---|---|---|
| Instances | `results/instances.csv` | 6,000 | 40 | Instance characterization (features) |
| Benchmark | `out/results/full_experiment.csv` | 18,000 | 18 | Per-algorithm run results (profit, weight, time) |
| BB Instrumentation | `results/bb_instrumentation.csv` | 6,000 | 44 | B&B algorithm internal metrics |
| DP Instrumentation | `results/dp_instrumentation.csv` | 6,000 | 22 | DP algorithm internal metrics |
| Greedy Instrumentation | `results/greedy_instrumentation.csv` | 6,000 | 12 | Greedy algorithm internal metrics |

**Target:** `out/results/canonical_dataset.csv` — 18,000 rows × ~110 columns, one row per algorithm run.

---

## Design Decisions

### Join Key Verification

Composite key `(instance_id, capacity_mode)` verified unique within each source CSV (6,000 unique keys, identical across all four pre-existing CSVs). Greedy CSV (generated in Phase 2.5) confirmed identical key set.

### Column Ordering (Deterministic)

7 identifier columns first (ordered list, not set): `algorithm`, `instance_id`, `n`, `family`, `capacity_mode`, `capacity`, `seed`. Followed by: instance features → benchmark metrics → BB instrumentation → DP instrumentation → Greedy instrumentation.

### DP Column Collision Resolution

Two columns exist in both `bb_instrumentation.csv` and `dp_instrumentation.csv` with **different semantics**:

| Column | BB meaning | DP meaning |
|---|---|---|
| `sum_improvement_amount` | Total improvement from branching | Total improvement from DP decisions |
| `mean_improvement_amount` | Mean improvement per branch | Mean improvement per DP decision |

Resolution: DP versions prefixed with `dp_` → `dp_sum_improvement_amount`, `dp_mean_improvement_amount`. Zero data loss.

### Overlap Handling

- `nodes_explored`, `max_queue_size`: exist in both benchmark and BB CSV — kept only from benchmark (first source wins via `putIfAbsent`).
- `optimal_value`: exists in both benchmark and DP CSV — kept only from benchmark.

### Greedy CSV Generation

Greedy instrumentation CSV did not exist. Generated via `GreedyInstrumentationRunner.java` (6,000 instances × 2 capacity modes = 6,000 rows; 15 min runtime). Runner gracefully handles its absence (skips Greedy columns, continues).

---

## Verification Results

| Check | Expected | Actual | Status |
|---|---|---|---|
| Rows | 18,000 | 18,000 | ✅ |
| Columns | ~110 | 110 | ✅ |
| Missing values (excl. optimal columns) | 0 | 0 | ✅ |
| Duplicate `(instance_id, capacity_mode, algorithm)` | 0 | 0 | ✅ |
| Missing identifier values | 0 | 0 | ✅ |
| BB instrumentation columns present | true | true | ✅ |
| DP instrumentation columns present | true | true | ✅ |
| Greedy instrumentation columns present | true | true | ✅ |
| DP collision rename (`dp_sum_improvement_amount`) | true | true | ✅ |
| BB original (`sum_improvement_amount`) | true | true | ✅ |

---

## Files Changed / Created

- **Created** `src/main/java/benchmark/DatasetIntegrationRunner.java` — standalone integration runner
- **Created** `out/results/canonical_dataset.csv` — unified canonical dataset (18,000 × 110)
- **Note:** `results/greedy_instrumentation.csv` generated as prerequisite (6,000 rows × 12 columns)

---

## Audit Log

- **11:18** — Initial `DatasetIntegrationRunner.java` written (3 unfixed issues)
- **11:20** — Fixes applied: ordered identifiers, captured headers at parse time, DP column disambiguation
- **11:21** — Compilation + dry-run: 18,000 × 104 (greedy excluded), all checks pass
- **11:22** — User approved greedy generation
- **11:37** — `GreedyInstrumentationRunner` complete (6,000 rows)
- **11:38** — Final re-run: 18,000 × 110, all checks pass

---

## Conclusion

Phase 2.5 complete. The canonical dataset is ready for statistical analysis. Column naming is deterministic, missing values are zero, DP/BB column collision is resolved, and all three instrumentation sources are fully integrated.
