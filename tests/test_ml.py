import numpy as np
import pandas as pd
import pytest

from adewi.ml_early_warning import prepare_ml_dataset, train_drought_classifier


def test_prepare_and_train_drought_classifier():
    np.random.seed(42)
    n = 120
    df = pd.DataFrame({
        "region": ["Eastern"] * (n // 2) + ["Southern"] * (n // 2),
        "date": pd.date_range("2020-01-01", periods=n // 2, freq="16D").tolist() * 2,
        "z_rainfall": np.random.normal(0, 1, n),
        "z_soil_moisture": np.random.normal(0, 1, n),
        "z_lst": np.random.normal(0, 1, n),
        "adewi": np.random.normal(0, 1, n),
        "z_ndvi": np.random.normal(0, 1, n),
    })

    X, y, feats = prepare_ml_dataset(df, lead_steps=2, target_threshold=-0.5)
    assert len(X) > 0
    assert len(y) == len(X)
    assert len(feats) == 4

    # Test random forest
    res_rf = train_drought_classifier(X, y, feats, model_type="rf")
    assert "metrics" in res_rf
    assert "accuracy" in res_rf["metrics"]
    assert 0.0 <= res_rf["metrics"]["accuracy"] <= 1.0
    assert len(res_rf["feature_importances"]) == len(feats)

    # Test logistic regression
    res_lr = train_drought_classifier(X, y, feats, model_type="lr")
    assert "accuracy" in res_lr["metrics"]
