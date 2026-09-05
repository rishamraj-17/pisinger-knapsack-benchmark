from typing import Optional

import numpy as np
import pandas as pd

from config import (
    ALGO_BB, ALGO_DP, ALGO_GREEDY,
    ALGORITHM_CANONICAL, EPS, RANDOM_SEED,
)


def load_canonical(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected_rows = 18000
    expected_cols = 110
    if df.shape[0] != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} rows, got {df.shape[0]}"
        )
    if df.shape[1] != expected_cols:
        raise ValueError(
            f"Expected {expected_cols} columns, got {df.shape[1]}"
        )
    return df


def compute_optimality_gap(df: pd.DataFrame) -> pd.DataFrame:
    greedy_mask = df["algorithm"] == ALGO_GREEDY
    greedy_rows = df[greedy_mask].copy()
    greedy_rows = greedy_rows.reset_index(drop=True)

    dp_rows = df[df["algorithm"] == ALGO_DP][
        ["instance_id", "capacity_mode", "solution_value"]
    ].copy()
    dp_rows = dp_rows.rename(
        columns={"solution_value": "dp_optimal_value"}
    )

    greedy_joined = greedy_rows.merge(
        dp_rows, on=["instance_id", "capacity_mode"], how="left"
    )

    dp_opt = greedy_joined["dp_optimal_value"].values.astype(float)
    greedy_sol = greedy_joined["solution_value"].values.astype(float)

    gap = np.where(
        dp_opt > 0, (dp_opt - greedy_sol) / dp_opt, np.nan
    )

    df.loc[greedy_mask, "optimality_gap"] = gap

    n_missing = int(np.isnan(gap).sum())
    if n_missing > 0:
        raise ValueError(
            f"{n_missing} Greedy rows could not be matched to a DP "
            f"row by (instance_id, capacity_mode)"
        )

    return df


def compute_solution_gap(df: pd.DataFrame) -> pd.DataFrame:
    bb_mask = df["algorithm"] == ALGO_BB

    dp_opt = (
        df[df["algorithm"] == ALGO_DP][
            ["instance_id", "capacity_mode", "solution_value"]
        ]
        .rename(columns={"solution_value": "dp_optimal_value"})
    )

    bb_rows = df[bb_mask][
        ["instance_id", "capacity_mode", "solution_value"]
    ].copy()

    merged = bb_rows.merge(
        dp_opt, on=["instance_id", "capacity_mode"], how="left"
    )

    dp_opt_vals = merged["dp_optimal_value"].values.astype(float)
    bb_sol_vals = merged["solution_value"].values.astype(float)

    gap = np.where(
        dp_opt_vals > 0,
        (dp_opt_vals - bb_sol_vals) / dp_opt_vals,
        np.nan,
    )

    df.loc[bb_mask, "solution_gap"] = gap

    n_missing = int(np.isnan(gap).sum())
    if n_missing > 0:
        raise ValueError(
            f"{n_missing} B&B rows could not be matched to a DP "
            f"row by (instance_id, capacity_mode)"
        )

    return df


def filter_algorithm(
    df: pd.DataFrame, algo: str
) -> pd.DataFrame:
    if algo not in ALGORITHM_CANONICAL:
        raise ValueError(
            f"Unknown algorithm '{algo}'. "
            f"Must be one of {ALGORITHM_CANONICAL}"
        )
    subset = df[df["algorithm"] == algo].copy()
    n_expected = 6000
    if len(subset) != n_expected:
        raise ValueError(
            f"Expected {n_expected} rows for {algo}, "
            f"got {len(subset)}"
        )
    return subset.reset_index(drop=True)
