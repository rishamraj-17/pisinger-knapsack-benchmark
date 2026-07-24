import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from config import (
    ALGO_BB, ALGO_DP, ALGO_GREEDY,
    ALGORITHM_CANONICAL,
    ALGORITHM_LABEL_MAP,
    CORRELATION_BLOCK_DROPS,
    EPS,
    GROUP_A_INSTANCE_CHARACTERISTICS,
    LOG_EPS_RESPONSE,
    RANDOM_SEED,
)
from utils.data import (
    load_canonical,
    compute_optimality_gap,
    compute_solution_gap,
    filter_algorithm,
)
from utils.preprocessing import (
    add_log_n,
    apply_block_filter,
    apply_global_exclusions,
    arctanh_transform,
    check_dp_composition,
    compute_per_algorithm_correlation,
    encode_capacity_mode,
    encode_family,
    log_transform,
)

RNG = np.random.default_rng(RANDOM_SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

def main():
    print("=" * 60)
    print("Phase 3.3.1 — Data Preparation Pipeline")
    print("=" * 60)

    # ── 1. LOAD ────────────────────────────────────────────────
    print("\n[1/12] Loading canonical dataset...")
    canonical_path = Path(
        __file__).resolve().parent.parent.parent / "out" / "results" / "canonical_dataset.csv"
    if not canonical_path.exists():
        print(f"  ERROR: Dataset not found at {canonical_path}")
        sys.exit(1)
    df = load_canonical(str(canonical_path))
    print(f"  Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    # ── 2. COMPUTE GREEDY OPTIMALITY GAP ────────────────────────
    print("\n[2/12] Computing Greedy optimality_gap (DP join)...")
    df = compute_optimality_gap(df)
    greedy_gap = df.loc[
        df["algorithm"] == "Greedy", "optimality_gap"
    ].values.astype(float)
    print(
        f"  Greedy optimality_gap range: "
        f"[{greedy_gap.min():.6f}, {greedy_gap.max():.6f}]"
    )

    # ── 3. COMPUTE B&B SOLUTION GAP ─────────────────────────────
    print("\n[3/12] Computing B&B solution_gap (via DP join)...")
    df = compute_solution_gap(df)
    bb_gap = df.loc[
        df["algorithm"] == ALGO_BB, "solution_gap"
    ].values.astype(float)
    complete_bb = bb_gap == 0
    n_gt = int((~complete_bb).sum())
    print(
        f"  B&B solution_gap: {int(complete_bb.sum())} rows = 0, "
        f"{n_gt} rows > 0"
    )
    if n_gt > 0:
        print(f"    max gap = {bb_gap.max():.8f}")

    # ── 4. GLOBAL EXCLUSIONS ────────────────────────────────────
    print("\n[4/12] Applying global exclusions...")
    excluded_before = set(df.columns)
    df = apply_global_exclusions(df)
    excluded_after = set(df.columns)
    dropped = excluded_before - excluded_after
    print(f"  Dropped {len(dropped)} columns: {sorted(dropped)}")

    # ── 5. PER-ALGORITHM FILTERING ─────────────────────────────
    print("\n[5/12] Filtering by algorithm...")
    algo_dfs = {}
    for algo in ALGORITHM_CANONICAL:
        algo_df = filter_algorithm(df, algo)
        algo_dfs[algo] = algo_df
        print(f"  {algo}: {algo_df.shape[0]} rows × {algo_df.shape[1]} columns")

    # ── 6. RESPONSE TRANSFORMS ──────────────────────────────────
    print("\n[6/12] Creating transformed response columns...")
    for algo in ALGORITHM_CANONICAL:
        algo_df = algo_dfs[algo]
        if algo == ALGO_GREEDY:
            if "time_millis" in algo_df.columns:
                vals = algo_df["time_millis"].values.astype(float)
                algo_df["log_time_millis"] = np.log(vals + LOG_EPS_RESPONSE)
        elif algo == ALGO_DP:
            if "time_millis" in algo_df.columns:
                vals = algo_df["time_millis"].values.astype(float)
                algo_df["log_time_millis"] = np.log(vals + LOG_EPS_RESPONSE)
            if "memory_mb" in algo_df.columns:
                vals = algo_df["memory_mb"].values.astype(float)
                algo_df["log_memory_mb"] = np.log(vals + LOG_EPS_RESPONSE)
        elif algo == ALGO_BB:
            if "time_millis" in algo_df.columns:
                vals = algo_df["time_millis"].values.astype(float)
                algo_df["log_time_millis"] = np.log(vals + LOG_EPS_RESPONSE)
            if "nodes_explored" in algo_df.columns:
                vals = algo_df["nodes_explored"].values.astype(float)
                algo_df["log_nodes_explored"] = np.log(vals + 1.0)
            if "optimal" in algo_df.columns:
                algo_df["optimal"] = (
                    algo_df["optimal"].astype(str).str.lower() == "true"
                ).astype(int)
        algo_dfs[algo] = algo_df
    print("  Response columns created: log_time_millis, log_memory_mb, "
          "log_nodes_explored, optimal (int)")

    # ── 7. PREDICTOR TRANSFORMS ─────────────────────────────────
    print("\n[7/12] Applying predictor transforms...")
    for algo in ALGORITHM_CANONICAL:
        algo_df = algo_dfs[algo]
        algo_df = log_transform(algo_df)
        algo_df = arctanh_transform(algo_df)
        algo_dfs[algo] = algo_df
    print("  Log and arctanh transforms applied")

    # ── 8. CATEGORICAL ENCODING ─────────────────────────────────
    print("\n[8/12] Encoding categorical variables...")
    for algo in ALGORITHM_CANONICAL:
        algo_df = algo_dfs[algo]
        algo_df = encode_family(algo_df)
        algo_df = encode_capacity_mode(algo_df)
        algo_df = add_log_n(algo_df)
        algo_dfs[algo] = algo_df
    print("  Family (one-hot), capacity_mode (dummy), log_n created")

    # ── 9. PER-ALGORITHM CORRELATION VERIFICATION ──────────────
    print("\n[9/12] Computing per-algorithm correlation verification...")
    diag_dir = OUTPUT_DIR / "diagnostics"
    diag_dir.mkdir(parents=True, exist_ok=True)
    all_corr = []
    for algo in ALGORITHM_CANONICAL:
        algo_df = algo_dfs[algo]
        corr_df = compute_per_algorithm_correlation(algo_df, algo)
        if not corr_df.empty:
            all_corr.append(corr_df)
        corr_path = diag_dir / f"correlation_verification_{algo}.csv"
        corr_df.to_csv(corr_path, index=False)
        print(f"  Saved {corr_path.name} ({len(corr_df)} pairs)")
    if all_corr:
        combined_corr = pd.concat(all_corr, ignore_index=True)
        high_corr = combined_corr[
            combined_corr["correlation"].abs() > 0.95
        ]
        print(f"  High-correlation pairs (|r| > 0.95): {len(high_corr)}")

    # ── 10. DP COMPOSITIONAL CHECK ──────────────────────────────
    print("\n[10/12] DP compositional check...")
    dp_df = algo_dfs[ALGO_DP]
    comp_result = check_dp_composition(dp_df)
    comp_path = diag_dir / "dp_composition_check.txt"
    with open(comp_path, "w") as f:
        f.write("DP Compositional Check\n")
        f.write("=" * 50 + "\n")
        f.write(f"Check performed: {comp_result['check_performed']}\n")
        if comp_result["check_performed"]:
            f.write(
                f"Rows checked: {comp_result['n_rows_checked']}\n"
            )
            f.write(
                f"Exact matches: {comp_result['n_exact_match']}\n"
            )
            f.write(
                f"All exact: {comp_result['all_exact']}\n"
            )
            f.write(
                f"Exact fraction: {comp_result['exact_fraction']:.4f}\n"
            )
            if comp_result["all_exact"]:
                f.write(
                    "STATUS: include_count + exclude_count + tie_count "
                    "EXACTLY equals total_evaluations\n"
                )
            else:
                f.write(
                    "STATUS: Relationship is approximate, not exact\n"
                )
    print(f"  Saved {comp_path.name}")
    print(f"  All exact: {comp_result.get('all_exact', 'N/A')}")

    # ── 11. CORRELATION-BLOCK PRE-FILTER ────────────────────────
    print("\n[11/12] Applying correlation-block pre-filter...")
    from utils.preprocessing import CORRELATION_BLOCK_PRE_FILTER_DROPS
    for algo in ALGORITHM_CANONICAL:
        algo_df = algo_dfs[algo]
        before_cols = set(algo_df.columns)
        algo_df = apply_block_filter(algo_df)
        after_cols = set(algo_df.columns)
        dropped = [
            c for c in CORRELATION_BLOCK_PRE_FILTER_DROPS
            if c in before_cols and c not in after_cols
        ]
        if dropped:
            print(f"  {algo}: block-filter dropped {dropped}")
        block4_present = [
            c for c in
            ["mean_bound", "max_bound", "min_bound"]
            if c in before_cols
        ]
        if block4_present:
            print(
                f"  {algo}: Block 4 columns retained for "
                f"per-model exclusion: {block4_present}"
            )
        algo_dfs[algo] = algo_df

    # ── 12. SAVE PREPARED DATAFRAMES ────────────────────────────
    print("\n[12/12] Saving prepared dataframes...")
    prepared_dir = OUTPUT_DIR / "prepared"
    prepared_dir.mkdir(parents=True, exist_ok=True)
    for algo in ALGORITHM_CANONICAL:
        label = ALGORITHM_LABEL_MAP[algo]
        path = prepared_dir / f"{label}.pkl"
        algo_dfs[algo].to_pickle(path)
        n_cols = algo_dfs[algo].shape[1]
        print(
            f"  Saved {path.name}: "
            f"{len(algo_dfs[algo])} rows × {n_cols} columns"
        )

    # ── SUMMARY ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PREPARATION COMPLETE")
    print("=" * 60)
    print("\nOutput files:")
    print(f"  {prepared_dir}/")
    for algo in ALGORITHM_CANONICAL:
        label = ALGORITHM_LABEL_MAP[algo]
        print(f"    {label}.pkl")
    print(f"  {diag_dir}/")
    for algo in ALGORITHM_CANONICAL:
        print(f"    correlation_verification_{algo}.csv")
    print(f"    dp_composition_check.txt")

    # Column verification
    print("\nColumn verification per algorithm:")
    for algo in ALGORITHM_CANONICAL:
        algo_df = algo_dfs[algo]
        label = ALGORITHM_LABEL_MAP[algo]
        print(f"\n  {label} ({algo_df.shape[1]} columns):")
        group_a_present = [
            c for c in GROUP_A_INSTANCE_CHARACTERISTICS
            if c in algo_df.columns
        ]
        print(f"    Group A present: {len(group_a_present)}/{len(GROUP_A_INSTANCE_CHARACTERISTICS)}")
        essential = ["n", "log_n", "cap_mode"]
        for fam in ["WeaklyCorrelated", "StronglyCorrelated",
                     "InverseCorrelated", "AlmostEqualRatios"]:
            essential.append(fam)
        missing = [c for c in essential if c not in algo_df.columns]
        if missing:
            print(f"    MISSING essential columns: {missing}")
        else:
            print(f"    All essential columns present")


if __name__ == "__main__":
    main()
