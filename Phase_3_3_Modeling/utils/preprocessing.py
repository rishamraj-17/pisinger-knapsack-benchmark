from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config import (
    ALL_BLOCK_DROP_COLUMNS,
    ALL_GLOBAL_EXCLUSIONS,
    ARCTANH_CLIP,
    CORRELATION_BLOCK_DROPS,
    EPS,
    FAMILIES,
    FAMILY_REFERENCE,
    GROUP_A_INSTANCE_CHARACTERISTICS,
    LOG_EPS_RESPONSE,
    MODEL_SPECIFIC_EXCLUSIONS,
    PREDICTOR_ARCTANH_TRANSFORM,
    PREDICTOR_LOG_TRANSFORM,
)


def apply_global_exclusions(df: pd.DataFrame) -> pd.DataFrame:
    cols_to_drop = [c for c in ALL_GLOBAL_EXCLUSIONS if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    return df


def log_transform(
    df: pd.DataFrame, columns: Optional[List[str]] = None
) -> pd.DataFrame:
    if columns is None:
        columns = PREDICTOR_LOG_TRANSFORM
    existing = [c for c in columns if c in df.columns]
    for col in existing:
        vals = df[col].values.astype(float)
        non_nan_mask = ~np.isnan(vals)
        if non_nan_mask.sum() == 0:
            continue
        df = df.copy()
        transformed = np.full_like(vals, np.nan, dtype=float)
        clipped = np.maximum(vals[non_nan_mask], EPS)
        transformed[non_nan_mask] = np.log(clipped)
        df[col] = transformed
    return df


def arctanh_transform(
    df: pd.DataFrame, columns: Optional[List[str]] = None
) -> pd.DataFrame:
    if columns is None:
        columns = PREDICTOR_ARCTANH_TRANSFORM
    existing = [c for c in columns if c in df.columns]
    for col in existing:
        vals = df[col].values.astype(float)
        non_nan_mask = ~np.isnan(vals)
        if non_nan_mask.sum() == 0:
            continue
        df = df.copy()
        transformed = np.full_like(vals, np.nan, dtype=float)
        clipped = np.clip(
            vals[non_nan_mask], -ARCTANH_CLIP, ARCTANH_CLIP
        )
        transformed[non_nan_mask] = np.arctanh(clipped)
        df[col] = transformed
    return df


def encode_family(df: pd.DataFrame) -> pd.DataFrame:
    for fam in FAMILIES:
        if fam not in df["family"].values:
            raise ValueError(
                f"Family '{fam}' not found in data"
            )
    dummies = pd.get_dummies(
        df["family"], prefix="", prefix_sep="", drop_first=False
    )
    if FAMILY_REFERENCE not in dummies.columns:
        raise ValueError(
            f"Reference family '{FAMILY_REFERENCE}' "
            f"not found in dummies columns: {list(dummies.columns)}"
        )
    dummies = dummies.drop(columns=[FAMILY_REFERENCE])
    dummies = dummies.astype(int)
    df = df.copy()
    for col in dummies.columns:
        df[col] = dummies[col].values
    family_cols = [
        f for f in FAMILIES if f != FAMILY_REFERENCE
    ]
    missing = [f for f in family_cols if f not in df.columns]
    if missing:
        raise ValueError(
            f"Family dummies not created: {missing}"
        )
    return df


def encode_capacity_mode(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["cap_mode"] = (
        df["capacity_mode"]
        .map({"fixed": 0, "scaled": 1})
        .astype(int)
    )
    return df


def add_log_n(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["log_n"] = np.log(df["n"].values.astype(float))
    return df


CORRELATION_BLOCK_PRE_FILTER_DROPS: List[str] = [
    "cells_allocated", "nonzero_value_states",
    "capacity_density", "solution_density",
    "cell_value_variance", "include_count",
]


def apply_block_filter(df: pd.DataFrame) -> pd.DataFrame:
    to_drop = [
        c for c in CORRELATION_BLOCK_PRE_FILTER_DROPS
        if c in df.columns
    ]
    if to_drop:
        df = df.drop(columns=to_drop)
    return df


def _get_group_a_columns(
    df: pd.DataFrame,
) -> List[str]:
    return [c for c in GROUP_A_INSTANCE_CHARACTERISTICS if c in df.columns]


def _get_m1_base_columns(
    df: pd.DataFrame,
) -> List[str]:
    base = ["n", "log_n", "cap_mode"]
    non_ref_families = [
        f for f in FAMILIES if f != FAMILY_REFERENCE
    ]
    return base + non_ref_families


def build_feature_matrices(
    df: pd.DataFrame,
    algo: str,
    response: str,
    model_specs: dict,
    config_module,
) -> Tuple[
    pd.DataFrame, pd.DataFrame, np.ndarray, List[str], List[str]
]:
    group_a = _get_group_a_columns(df)
    m1_base = _get_m1_base_columns(df)
    m1_cols = group_a + m1_base

    for col in m1_cols:
        if col not in df.columns:
            raise ValueError(
                f"M1 column '{col}' not found in prepared "
                f"dataframe for {algo} {response}"
            )

    spec = model_specs[(algo, response)]
    response_transform = spec["response_transform"]

    raw_response_name = response
    if response == "log_time_millis":
        raw_response_name = "time_millis"
    elif response == "log_memory_mb":
        raw_response_name = "memory_mb"
    elif response == "log_nodes_explored":
        raw_response_name = "nodes_explored"

    if raw_response_name not in df.columns:
        y = df.get(response)
        if y is None:
            raise ValueError(
                f"Response '{response}' not found in "
                f"dataframe for {algo}"
            )
    else:
        if response_transform == "log":
            vals = df[raw_response_name].values.astype(float)
            y = np.log(vals + LOG_EPS_RESPONSE)
        elif response_transform == "log1p":
            vals = df[raw_response_name].values.astype(float)
            y = np.log(vals + 1.0)
        else:
            y = pd.to_numeric(
                df[raw_response_name], errors="coerce"
            ).values

    X_m1 = df[m1_cols].copy()
    predictor_names_m1 = list(m1_cols)

    algo_metrics_key = _resolve_m2_label(spec["m2_predictor_label"])
    model_exclusions = spec.get("model_exclusions", [])

    m2_extra = [
        c
        for c in algo_metrics_key
        if c in df.columns
        and c not in model_exclusions
        and c not in m1_cols
    ]

    m2_cols = m1_cols + m2_extra
    for col in m2_cols:
        if col not in df.columns:
            raise ValueError(
                f"M2 column '{col}' not found in prepared "
                f"dataframe for {algo} {response}"
            )

    X_m2 = df[m2_cols].copy()
    predictor_names_m2 = list(m2_cols)

    X_m1 = X_m1.astype(float)
    X_m2 = X_m2.astype(float)

    return X_m1, X_m2, y, predictor_names_m1, predictor_names_m2


def _resolve_m2_label(label: str) -> List[str]:
    from config import M2_PREDICTOR_LABELS
    if label in M2_PREDICTOR_LABELS:
        return M2_PREDICTOR_LABELS[label]
    raise ValueError(f"Unknown M2 predictor label '{label}'")


def compute_per_algorithm_correlation(
    df: pd.DataFrame, algo: str
) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_patterns = ["family_", "cap_mode"]
    corr_cols = [
        c
        for c in numeric_cols
        if not any(p in c for p in exclude_patterns)
    ]
    if len(corr_cols) < 2:
        return pd.DataFrame()
    corr_matrix = df[corr_cols].corr()
    pairs = []
    for i, col_a in enumerate(corr_cols):
        for col_b in corr_cols[i + 1:]:
            val = corr_matrix.loc[col_a, col_b]
            if not np.isnan(val):
                pairs.append(
                    {
                        "algorithm": algo,
                        "var_a": col_a,
                        "var_b": col_b,
                        "correlation": val,
                    }
                )
    result = pd.DataFrame(pairs)
    return result


def check_dp_composition(
    df: pd.DataFrame,
) -> dict:
    if "include_count" not in df.columns:
        return {
            "check_performed": False,
            "reason": "include_count not in DP subset",
        }
    inc = pd.to_numeric(
        df["include_count"], errors="coerce"
    ).fillna(0).astype(int)
    exc = pd.to_numeric(
        df["exclude_count"], errors="coerce"
    ).fillna(0).astype(int)
    tie = pd.to_numeric(
        df["tie_count"], errors="coerce"
    ).fillna(0).astype(int)
    total = pd.to_numeric(
        df["total_evaluations"], errors="coerce"
    ).fillna(0).astype(int)

    computed_sum = inc + exc + tie
    matches = computed_sum.values == total.values
    n_exact = int(matches.sum())
    n_total = len(matches)
    result = {
        "check_performed": True,
        "n_rows_checked": n_total,
        "n_exact_match": n_exact,
        "all_exact": bool(n_exact == n_total),
        "exact_fraction": float(n_exact / n_total),
    }
    return result
