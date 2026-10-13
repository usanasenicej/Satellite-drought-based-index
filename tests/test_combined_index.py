"""Unit tests for adewi.combined_index module.

Tests cover:
- drought classification (classify_drought)
- ADEWI and CADI index computation (compute_indices)
- Weight sum integrity
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adewi.anomalies import compute_anomalies
from adewi.combined_index import classify_drought, compute_indices
from adewi.preprocessing import preprocess


# ---------------------------------------------------------------------------
# Minimal config fixture (no file I/O needed)
# ---------------------------------------------------------------------------

MINIMAL_CFG = {
    "weights": {
        "adewi": {"rainfall": 0.40, "soil_moisture": 0.35, "lst": 0.25},
        "cadi": {
            "ndvi": 0.20,
            "evi": 0.15,
            "rainfall": 0.25,
            "soil_moisture": 0.25,
            "lst": 0.15,
        },
    },
    "drought": {
        "classes": {"Watch": -0.5, "Mild": -1.0, "Moderate": -1.5, "Severe": -2.0},
    },
}


# ---------------------------------------------------------------------------
# classify_drought
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        (0.0, "Normal"),
        (-0.4, "Normal"),
        (-0.6, "Mild"),
        (-1.2, "Moderate"),
        (-1.6, "Severe"),
        (-2.1, "Extreme"),
    ],
)
def test_classify_drought_thresholds(value, expected):
    result = classify_drought(pd.Series([value]))
    assert result.iloc[0] == expected


def test_classify_drought_nan():
    result = classify_drought(pd.Series([float("nan")]))
    assert result.iloc[0] == "Missing"


def test_classify_drought_length_preserved():
    s = pd.Series([0.0, -1.0, -2.0, -3.0])
    assert len(classify_drought(s)) == len(s)


# ---------------------------------------------------------------------------
# compute_indices
# ---------------------------------------------------------------------------


def test_compute_indices_adewi_column_exists(preprocessed_df):
    zdf, _ = compute_anomalies(preprocessed_df)
    result = compute_indices(zdf, MINIMAL_CFG)
    assert "adewi" in result.columns


def test_compute_indices_cadi_column_exists(preprocessed_df):
    zdf, _ = compute_anomalies(preprocessed_df)
    result = compute_indices(zdf, MINIMAL_CFG)
    assert "cadi" in result.columns


def test_compute_indices_adewi_class_column_exists(preprocessed_df):
    zdf, _ = compute_anomalies(preprocessed_df)
    result = compute_indices(zdf, MINIMAL_CFG)
    assert "adewi_class" in result.columns


def test_compute_indices_no_all_nan_adewi(preprocessed_df):
    zdf, _ = compute_anomalies(preprocessed_df)
    result = compute_indices(zdf, MINIMAL_CFG)
    assert result["adewi"].notna().any()


def test_compute_indices_adewi_formula():
    """ADEWI = 0.40·Z_r + 0.35·Z_sm − 0.25·Z_lst — verify numerically."""
    zdf = pd.DataFrame(
        {
            "province": ["Eastern"],
            "time": [pd.Timestamp("2022-01-01")],
            "z_ndvi": [0.0],
            "z_evi": [0.0],
            "z_rainfall": [1.0],
            "z_soil_moisture": [1.0],
            "z_lst": [1.0],
        }
    )
    result = compute_indices(zdf, MINIMAL_CFG)
    expected = 0.40 * 1.0 + 0.35 * 1.0 - 0.25 * 1.0  # = 0.50
    assert result["adewi"].iloc[0] == pytest.approx(expected, rel=1e-6)


def test_adewi_weights_sum_to_one():
    w = MINIMAL_CFG["weights"]["adewi"]
    total = w["rainfall"] + w["soil_moisture"] + w["lst"]
    assert total == pytest.approx(1.0, rel=1e-6)


def test_cadi_weights_sum_to_one():
    w = MINIMAL_CFG["weights"]["cadi"]
    total = w["ndvi"] + w["evi"] + w["rainfall"] + w["soil_moisture"] + w["lst"]
    assert total == pytest.approx(1.0, rel=1e-6)


def test_compute_indices_ndvi_class_column_exists(preprocessed_df):
    zdf, _ = compute_anomalies(preprocessed_df)
    result = compute_indices(zdf, MINIMAL_CFG)
    assert "ndvi_class" in result.columns
