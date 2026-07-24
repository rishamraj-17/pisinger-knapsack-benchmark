from typing import Optional

import numpy as np
from sklearn.metrics import auc as sklearn_auc
from sklearn.metrics import roc_curve


def r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return 0.0
    return float(1.0 - ss_res / ss_tot)


def adj_r_squared(
    r2: float, n: int, p: int
) -> float:
    if n - p - 1 <= 0:
        return 0.0
    return float(
        1.0 - (1.0 - r2) * (n - 1) / (n - p - 1)
    )


def pseudo_r_squared_mcfadden(
    ll_model: float, ll_null: float
) -> float:
    if ll_null == 0:
        return 0.0
    return float(1.0 - ll_model / ll_null)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(
        np.sqrt(np.mean((y_true - y_pred) ** 2))
    )


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def brier_score(
    y_true: np.ndarray, y_prob: np.ndarray
) -> float:
    return float(np.mean((y_true - y_prob) ** 2))


def auc_roc(
    y_true: np.ndarray, y_prob: np.ndarray
) -> Optional[float]:
    unique_classes = np.unique(y_true)
    if len(unique_classes) < 2:
        return None
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    if len(fpr) < 2 or len(tpr) < 2:
        return None
    return float(sklearn_auc(fpr, tpr))


def cohens_f2(r2_1: float, r2_2: float) -> float:
    denom = 1.0 - r2_2
    if denom <= 0:
        return float("inf")
    return float((r2_2 - r2_1) / denom)


def duan_smearing(
    residuals: np.ndarray,
    family_labels: Optional[np.ndarray] = None,
) -> dict:
    if family_labels is None:
        phi_pooled = float(np.mean(np.exp(residuals)))
        return {"pooled": phi_pooled}
    unique_families = np.unique(family_labels)
    phi_dict: dict = {}
    for fam in unique_families:
        mask = family_labels == fam
        if mask.sum() > 0:
            phi_dict[str(fam)] = float(
                np.mean(np.exp(residuals[mask]))
            )
    phi_pooled = float(np.mean(np.exp(residuals)))
    return {"pooled": phi_pooled, **phi_dict}


def backtransformed_rmse(
    y_log_true: np.ndarray,
    y_log_pred: np.ndarray,
    smearing_factor: float,
) -> float:
    y_orig = np.exp(y_log_pred) * smearing_factor
    y_true_orig = np.exp(y_log_true)
    return float(
        np.sqrt(np.mean((y_true_orig - y_orig) ** 2))
    )


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(y_true == y_pred))


def precision_recall_f1(
    y_true: np.ndarray, y_pred: np.ndarray, positive_class=1
) -> dict:
    tp = int(np.sum((y_pred == positive_class) & (y_true == positive_class)))
    fp = int(np.sum((y_pred == positive_class) & (y_true != positive_class)))
    fn = int(np.sum((y_pred != positive_class) & (y_true == positive_class)))
    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = (
        float(2 * precision * recall / (precision + recall))
        if (precision + recall) > 0
        else 0.0
    )
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
