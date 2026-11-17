"""Machine Learning Early-Warning Drought Prediction Models.

Predicts agricultural drought onset (e.g. vegetation stress) k composite steps
(16, 32, 48 days) in advance using lagged meteorological and soil moisture anomalies.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


def prepare_ml_dataset(
    df: pd.DataFrame,
    lead_steps: int = 2,
    target_threshold: float = -1.0,
    target_col: str = "z_ndvi",
    feature_cols: tuple[str, ...] = ("z_rainfall", "z_soil_moisture", "z_lst", "adewi"),
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Build feature matrix X and future drought onset target y.

    y[t] = 1 if target_col[t + lead_steps] <= target_threshold else 0.
    """
    data = df.sort_values(["region", "date"]).copy() if "region" in df.columns else df.copy()

    # Create target shifted backwards (looking into future)
    data["target"] = (data[target_col] <= target_threshold).astype(int)
    data["future_target"] = data.groupby("region")["target"].shift(-lead_steps) if "region" in data.columns else data["target"].shift(-lead_steps)

    valid_features = [col for col in feature_cols if col in data.columns]
    valid_data = data.dropna(subset=valid_features + ["future_target"]).reset_index(drop=True)

    X = valid_data[valid_features].values
    y = valid_data["future_target"].values.astype(int)

    return X, y, valid_features


def train_drought_classifier(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    model_type: str = "rf",
    test_size: float = 0.3,
    random_state: int = 42,
) -> dict[str, Any]:
    """Train and evaluate early warning classifier with temporal splitting."""
    n_samples = len(X)
    split_idx = int(n_samples * (1.0 - test_size))

    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    if model_type == "rf":
        model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=random_state)
    elif model_type == "gb":
        model = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=random_state)
    else:
        model = LogisticRegression(random_state=random_state)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    try:
        y_prob = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else 0.5
    except Exception:
        auc = 0.5

    importances = {}
    if hasattr(model, "feature_importances_"):
        for name, imp in zip(feature_names, model.feature_importances_):
            importances[name] = float(imp)
    elif hasattr(model, "coef_"):
        for name, coef in zip(feature_names, model.coef_[0]):
            importances[name] = float(coef)

    return {
        "model": model,
        "model_type": model_type,
        "metrics": {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(auc),
        },
        "feature_importances": importances,
    }
