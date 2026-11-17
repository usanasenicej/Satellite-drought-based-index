"""Probabilistic ROC and Precision-Recall diagnostic evaluation suite.

Evaluates drought detection capabilities against binary historical events or ground truth:
- ROC curve and AUC-ROC
- Precision-Recall curve and Average Precision
- Youden's J statistic for optimal operational threshold selection
- Brier skill score
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, precision_recall_curve, roc_auc_score, roc_curve


def evaluate_detection_performance(
    y_true: np.ndarray | pd.Series,
    y_scores: np.ndarray | pd.Series,
) -> dict[str, Any]:
    """Compute comprehensive diagnostic metrics for drought event detection."""
    y_true_arr = np.asarray(y_true).astype(int)
    # Higher score should mean higher probability of drought
    scores = np.asarray(y_scores)

    if len(np.unique(y_true_arr)) < 2:
        return {
            "roc_auc": 0.5,
            "optimal_threshold": 0.0,
            "youden_j": 0.0,
            "brier_score": 0.0,
        }

    fpr, tpr, thresholds = roc_curve(y_true_arr, scores)
    auc_val = float(roc_auc_score(y_true_arr, scores))

    # Youden's J statistic: max(TPR - FPR)
    j_scores = tpr - fpr
    best_idx = int(np.argmax(j_scores))
    best_threshold = float(thresholds[best_idx])
    best_j = float(j_scores[best_idx])

    prec, rec, pr_thresh = precision_recall_curve(y_true_arr, scores)

    # Normalize scores to [0, 1] for Brier score if needed
    norm_scores = (scores - np.min(scores)) / (np.ptp(scores) + 1e-8)
    brier = float(brier_score_loss(y_true_arr, norm_scores))

    return {
        "roc_auc": round(auc_val, 4),
        "optimal_threshold": round(best_threshold, 4),
        "youden_j": round(best_j, 4),
        "brier_score": round(brier, 4),
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "precision": prec.tolist(),
        "recall": rec.tolist(),
    }
