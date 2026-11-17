import numpy as np
import pytest

from adewi.roc_evaluation import evaluate_detection_performance


def test_evaluate_detection_performance():
    np.random.seed(42)
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    # Well separated scores
    y_scores = np.array([0.1, 0.2, 0.15, 0.3, 0.7, 0.85, 0.9, 0.8])

    res = evaluate_detection_performance(y_true, y_scores)
    assert res["roc_auc"] == 1.0
    assert res["youden_j"] == 1.0
    assert 0.3 < res["optimal_threshold"] <= 0.7
    assert res["brier_score"] >= 0.0
