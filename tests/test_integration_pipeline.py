"""End-to-end integration tests for the full ADEWI analytical stack."""

import numpy as np
import pandas as pd
import pytest

from adewi.anomalies import compute_anomalies
from adewi.caching import CacheManager
from adewi.combined_index import compute_cadi_paper, compute_indices
from adewi.config import load_config
from adewi.delay_metrics import analyze_detection_dynamics
from adewi.events import extract_drought_events
from adewi.forecasting import forecast_autoregressive
from adewi.geography import RWANDA_DISTRICTS, get_districts_by_province
from adewi.ml_early_warning import prepare_ml_dataset, train_drought_classifier
from adewi.preprocessing import preprocess
from adewi.roc_evaluation import evaluate_detection_performance
from adewi.schema import validate_environmental_timeseries
from adewi.spatial import compute_zonal_statistics
from adewi.standardized_indices import compute_vci, compute_vhi
from adewi.water_balance import compute_climatic_water_balance, compute_spei


def test_full_pipeline_synthetic_integration():
    # 1. Synthesize 2-year sample
    n = 46  # 46 composite steps (2 years)
    dates = pd.date_range("2020-01-01", periods=n, freq="16D")
    df = pd.DataFrame({
        "province": ["Eastern"] * n,
        "region": ["Eastern"] * n,
        "date": dates,
        "time": dates,
        "doy": dates.dayofyear,
        "doy_bin": dates.dayofyear // 16,
        "ndvi": np.clip(np.random.normal(0.5, 0.1, n), 0.1, 0.9),
        "evi": np.clip(np.random.normal(0.35, 0.08, n), 0.05, 0.8),
        "rainfall": np.clip(np.random.normal(30.0, 10.0, n), 0.0, 120.0),
        "soil_moisture": np.clip(np.random.normal(0.22, 0.04, n), 0.05, 0.45),
        "lst": np.clip(np.random.normal(301.0, 3.0, n), 280.0, 325.0),
    })

    # 2. Schema validation
    val_rep = validate_environmental_timeseries(df)
    assert val_rep.is_valid

    # 3. Standardized indices & Water balance
    vci = compute_vci(df, ndvi_col="ndvi")
    assert len(vci) == n
    wb = compute_climatic_water_balance(df["rainfall"], pd.Series([25.0] * n))
    spei = compute_spei(wb, window=2)
    assert len(spei) == n

    # 4. Anomalies & Combined index
    cfg = load_config()
    df_clean, _ = preprocess(df)
    df_anom, _ = compute_anomalies(df_clean)
    assert "z_ndvi" in df_anom.columns
    assert "z_rainfall" in df_anom.columns

    df_idx = compute_indices(df_anom, cfg)
    assert "adewi" in df_idx.columns
    assert "cadi" in df_idx.columns

    # 5. Events extraction
    events = extract_drought_events(df_idx, index_col="adewi", threshold=-0.5)
    assert isinstance(events, pd.DataFrame)

    # 6. ML Early warning
    X, y, feats = prepare_ml_dataset(df_idx, lead_steps=1, target_threshold=-0.5)
    if len(X) > 10 and len(np.unique(y)) > 1:
        ml_res = train_drought_classifier(X, y, feats, model_type="rf")
        assert "metrics" in ml_res

    # 7. Forecaster
    fc = forecast_autoregressive(df_idx["adewi"], steps=2)
    assert len(fc.forecast) == 2
