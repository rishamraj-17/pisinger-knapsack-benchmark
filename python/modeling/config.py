from typing import Dict, List, Optional, Tuple

RANDOM_SEED: int = 42
EPS: float = 1e-9
ARCTANH_CLIP: float = 0.9999
LOG_EPS_RESPONSE: float = 1e-9

ALGO_GREEDY: str = "Greedy"
ALGO_DP: str = "DynamicProgramming"
ALGO_BB: str = "BranchAndBound"

ALGORITHM_CANONICAL: list = [ALGO_GREEDY, ALGO_DP, ALGO_BB]

ALGO_SHORT_TO_CANONICAL: dict = {
    "Greedy": ALGO_GREEDY,
    "DP": ALGO_DP,
    "B&B": ALGO_BB,
}

ALGO_CANONICAL_TO_SHORT: dict = {v: k for k, v in ALGO_SHORT_TO_CANONICAL.items()}

IDENTIFIERS: List[str] = [
    "algorithm", "instance_id", "n", "family",
    "capacity_mode", "capacity", "seed",
]

GROUP_A_INSTANCE_CHARACTERISTICS: List[str] = [
    "total_weight", "total_value",
    "mean_weight", "mean_value", "median_weight", "median_value",
    "std_weight", "std_value", "min_weight", "max_weight",
    "min_value", "max_value",
    "weight_cv", "value_cv", "weight_skewness", "value_skewness",
    "weight_kurtosis", "value_kurtosis",
    "capacity_ratio", "slack", "average_fillable_items",
    "pearson_corr", "spearman_corr", "kendall_corr",
    "mean_ratio", "median_ratio", "std_ratio", "ratio_entropy",
    "unique_ratio_count", "duplicate_ratio_fraction",
    "unique_weights", "unique_values", "unique_pairs",
    "duplicate_items", "duplicate_pairs",
]

BENCHMARK_OUTCOMES: List[str] = [
    "time_nanos", "time_millis", "memory_bytes", "memory_mb",
    "solution_value", "optimal_value", "optimality_gap",
    "nodes_explored", "nodes_pruned", "max_queue_size", "optimal",
]

BB_METRICS: List[str] = [
    "nodes_generated", "leaf_nodes", "internal_nodes",
    "max_depth", "mean_depth", "median_depth", "min_depth",
    "depth_histogram",
    "mean_queue_size", "final_queue_size", "queue_histogram",
    "mean_bound", "bound_variance", "min_bound", "max_bound",
    "mean_bound_gap", "bound_gap_variance",
    "pruned_by_bound", "pruned_by_cap",
    "left_branches", "right_branches",
    "explored_children", "skipped_children",
    "skipped_infeasible", "skipped_by_bound", "skipped_by_cap",
    "improvement_count", "sum_improvement_amount",
    "mean_improvement_amount",
    "first_improvement_node", "last_improvement_node",
    "improvement_depths", "improvement_nodes",
    "explored_generated_ratio", "pruned_generated_ratio",
    "avg_branching_factor",
]

DP_METRICS: List[str] = [
    "capacity_density",
    "cells_allocated", "total_evaluations",
    "include_count", "exclude_count", "tie_count", "include_ratio",
    "nonzero_value_states", "zero_value_states", "fill_rate",
    "mean_cell_value", "cell_value_variance",
    "dp_sum_improvement_amount", "dp_mean_improvement_amount",
    "updates_per_cell",
]

GREEDY_METRICS: List[str] = [
    "selected_count", "solution_density", "residual_capacity",
    "capacity_utilization", "last_selected_position",
    "first_skipped_position",
]

STRING_HISTOGRAM_COLUMNS: List[str] = [
    "depth_histogram", "queue_histogram",
    "improvement_depths", "improvement_nodes",
]

CONSTANT_COLUMNS: List[str] = [
    "first_improvement_node",
    "leaf_nodes",
    "min_depth",
    "seed",
    "skipped_by_cap",
]

NEAR_CONSTANT_COLUMNS: List[str] = [
    "explored_generated_ratio",
]

REDUNDANT_COLUMNS: List[str] = [
    "time_nanos",
    "capacity",
]

STRUCTURALLY_MISSING_COLUMNS: List[str] = [
    "optimal_value",
]

COLUMNS_TO_RETAIN_FOR_CLUSTERING: List[str] = [
    "instance_id",
]

ALL_GLOBAL_EXCLUSIONS: List[str] = sorted(set(
    CONSTANT_COLUMNS
    + NEAR_CONSTANT_COLUMNS
    + REDUNDANT_COLUMNS
    + STRING_HISTOGRAM_COLUMNS
))

RESPONSE_COLUMNS_RAW: Dict[str, str] = {
    "log_time_millis": "time_millis",
    "log_memory_mb": "memory_mb",
    "log_nodes_explored": "nodes_explored",
    "optimality_gap": "optimality_gap",
    "fill_rate": "fill_rate",
    "optimal": "optimal",
    "solution_gap": "solution_gap",
}

RESPONSE_LOG_TRANSFORM: Dict[str, Optional[str]] = {
    "log_time_millis": "log",
    "log_memory_mb": "log",
    "log_nodes_explored": "log1p",
    "optimality_gap": None,
    "fill_rate": None,
    "optimal": None,
    "solution_gap": None,
}

PREDICTOR_LOG_TRANSFORM: List[str] = [
    "total_weight", "total_value", "average_fillable_items", "slack",
    "unique_ratio_count", "unique_weights", "unique_values",
    "unique_pairs", "duplicate_items", "duplicate_pairs",
    "total_evaluations",
    "include_count", "exclude_count", "tie_count",
    "updates_per_cell",
    "cells_allocated", "nonzero_value_states", "zero_value_states",
    "dp_sum_improvement_amount", "dp_mean_improvement_amount",
    "nodes_generated", "internal_nodes",
    "bound_variance", "sum_improvement_amount",
    "pruned_by_bound", "mean_bound_gap", "bound_gap_variance",
    "mean_queue_size", "final_queue_size",
    "left_branches", "right_branches",
    "explored_children", "skipped_children",
    "skipped_infeasible", "skipped_by_bound",
]

PREDICTOR_ARCTANH_TRANSFORM: List[str] = [
    "pearson_corr", "spearman_corr", "kendall_corr",
]

CORRELATION_BLOCK_DROPS: Dict[str, List[str]] = {
    "block_1": ["cells_allocated", "nonzero_value_states"],
    "block_2": ["capacity_density", "solution_density"],
    "block_3": ["cell_value_variance", "include_count"],
    "block_4": ["mean_bound", "max_bound", "min_bound"],
}

ALL_BLOCK_DROP_COLUMNS: List[str] = sorted(set(
    sum(CORRELATION_BLOCK_DROPS.values(), [])
))

MODEL_SPECIFIC_EXCLUSIONS: Dict[Tuple[str, str], List[str]] = {
    (ALGO_DP, "log_memory_mb"): [
        "cells_allocated", "nonzero_value_states", "zero_value_states",
    ],
    (ALGO_DP, "fill_rate"): [
        "fill_rate", "cells_allocated", "nonzero_value_states",
    ],
    (ALGO_BB, "log_time_millis"): [
        "mean_bound", "max_bound", "min_bound",
    ],
    (ALGO_BB, "optimal"): [
        "mean_bound", "max_bound", "min_bound",
    ],
    (ALGO_BB, "log_nodes_explored"): [
        "mean_bound", "max_bound", "min_bound",
        "nodes_generated", "internal_nodes",
    ],
    (ALGO_BB, "solution_gap"): [
        "mean_bound", "max_bound", "min_bound",
        "nodes_generated", "internal_nodes",
    ],
}

MODEL_SPECS = {
    (ALGO_GREEDY, "log_time_millis"): {
        "family": "ols",
        "status": "confirmatory",
        "response_transform": "log",
        "m2_predictor_label": "all_greedy",
        "model_exclusions": [],
    },
    (ALGO_GREEDY, "optimality_gap"): {
        "family": "fractional_logit",
        "status": "confirmatory",
        "response_transform": None,
        "m2_predictor_label": "all_greedy",
        "model_exclusions": [],
    },
    (ALGO_DP, "log_time_millis"): {
        "family": "ols",
        "status": "confirmatory",
        "response_transform": "log",
        "m2_predictor_label": "all_dp",
        "model_exclusions": [],
    },
    (ALGO_DP, "log_memory_mb"): {
        "family": "ols",
        "status": "exploratory",
        "response_transform": "log",
        "m2_predictor_label": "dp_minus_memory",
        "model_exclusions": MODEL_SPECIFIC_EXCLUSIONS[(ALGO_DP, "log_memory_mb")],
    },
    (ALGO_DP, "fill_rate"): {
        "family": "fractional_logit",
        "status": "supplementary",
        "response_transform": None,
        "m2_predictor_label": "dp_minus_fillrate",
        "model_exclusions": MODEL_SPECIFIC_EXCLUSIONS[(ALGO_DP, "fill_rate")],
    },
    (ALGO_BB, "log_time_millis"): {
        "family": "ols",
        "status": "confirmatory",
        "response_transform": "log",
        "m2_predictor_label": "bb_minus_bounds",
        "model_exclusions": MODEL_SPECIFIC_EXCLUSIONS[(ALGO_BB, "log_time_millis")],
    },
    (ALGO_BB, "optimal"): {
        "family": "elasticnet",
        "status": "exploratory",
        "response_transform": None,
        "m2_predictor_label": "bb_minus_bounds",
        "model_exclusions": MODEL_SPECIFIC_EXCLUSIONS[(ALGO_BB, "optimal")],
    },
    (ALGO_BB, "log_nodes_explored"): {
        "family": "ols",
        "status": "supplementary",
        "response_transform": "log",
        "m2_predictor_label": "bb_minus_nodes",
        "model_exclusions": MODEL_SPECIFIC_EXCLUSIONS[(ALGO_BB, "log_nodes_explored")],
    },
    (ALGO_BB, "solution_gap"): {
        "family": "hurdle",
        "status": "supplementary",
        "response_transform": None,
        "m2_predictor_label": "bb_minus_nodes",
        "model_exclusions": MODEL_SPECIFIC_EXCLUSIONS[(ALGO_BB, "solution_gap")],
    },
}

ALGORITHMS: List[str] = [ALGO_GREEDY, ALGO_DP, ALGO_BB]

FAMILIES: List[str] = [
    "Uncorrelated", "WeaklyCorrelated", "StronglyCorrelated",
    "InverseCorrelated", "AlmostEqualRatios",
]

FAMILY_REFERENCE: str = "Uncorrelated"

ALGORITHM_METRICS: Dict[str, List[str]] = {
    ALGO_GREEDY: GREEDY_METRICS,
    ALGO_DP: DP_METRICS,
    ALGO_BB: BB_METRICS,
}

ALGORITHM_LABEL_MAP: Dict[str, str] = {
    ALGO_GREEDY: "Greedy",
    ALGO_DP: "DP",
    ALGO_BB: "BandB",
}

M2_PREDICTOR_LABELS: Dict[str, List[str]] = {
    "all_greedy": GREEDY_METRICS,
    "all_dp": DP_METRICS,
    "dp_minus_memory": [
        c for c in DP_METRICS
        if c not in MODEL_SPECIFIC_EXCLUSIONS[(ALGO_DP, "log_memory_mb")]
    ],
    "dp_minus_fillrate": [
        c for c in DP_METRICS
        if c not in MODEL_SPECIFIC_EXCLUSIONS[(ALGO_DP, "fill_rate")]
    ],
    "bb_minus_bounds": [
        c for c in BB_METRICS
        if c not in CORRELATION_BLOCK_DROPS["block_4"]
    ],
    "bb_minus_nodes": [
        c for c in BB_METRICS
        if c not in (
            CORRELATION_BLOCK_DROPS["block_4"]
            + MODEL_SPECIFIC_EXCLUSIONS[(ALGO_BB, "log_nodes_explored")]
        )
    ],
}

LOFO_N_FOLDS: int = 5
CV5_N_SPLITS: int = 5
ELASTICNET_ALPHA: float = 0.5
ELASTICNET_CV_FOLDS: int = 5
ELASTICNET_N_CS: int = 50
ELASTICNET_MAX_ITER: int = 10000
N_BOOTSTRAP_RESAMPLES: int = 1999
N_PERMUTATION_REPEATS: int = 20

BH_ALPHA: float = 0.05

PIPELINE_VERSION: str = "1.0.0"
