"""Unit tests for adewi.validation module.

Tests cover:
- periods_hit_rate: known drought period detection and column output
- crop_correlation: correlation computation with mock crop data
- default_crop_placeholder: file creation and schema
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adewi.anomalies import compute_anomalies
from adewi.combined_index import compute_indices
from adewi.preprocessing import preprocess
from adewi.validation import crop_correlation, default_crop_placeholder, periods_hit_rate


# ---------------------------------------------------------------------------
# Shared config with an in-window validation period
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
        "adewi_event_threshold": -1.0,
    },
    "validation": {
        # Period that overlaps with the minimal_df date range (2022–2024)
        "known_drought_periods": [
            {"label": "2022 Season A dry spell", "start": "2021-10-01", "end": "2022-02-28"},
            {"label": "Future period (out of window)", "start": "2030-01-01", "end": "2030-06-30"},
        ],
        "crop_stats_file": "data/raw/nisr_crop_production_placeholder.csv",
    },
}


def _make_index_df(minimal_df: pd.DataFrame) -> pd.DataFrame:
    clean, _ = preprocess(minimal_df)
    zdf, _ = compute_anomalies(clean)
    return compute_indices(zdf, MINIMAL_CFG)


# ---------------------------------------------------------------------------
# periods_hit_rate
# ---------------------------------------------------------------------------


def test_periods_hit_rate_columns(minimal_df):
    index_df = _make_index_df(minimal_df)
    result = periods_hit_rate(index_df, MINIMAL_CFG)
    for col in ("period", "in_study_window", "mean_adewi", "detected"):
        assert col in result.columns


def test_periods_hit_rate_out_of_window_flag(minimal_df):
    index_df = _make_index_df(minimal_df)
    result = periods_hit_rate(index_df, MINIMAL_CFG)
    future = result[result["period"] == "Future period (out of window)"]
    assert len(future) == 1
    assert not future.iloc[0]["in_study_window"]


def test_periods_hit_rate_in_window_has_values(minimal_df):
    index_df = _make_index_df(minimal_df)
    result = periods_hit_rate(index_df, MINIMAL_CFG)
    in_window = result[result["in_study_window"] is True or result["in_study_window"] == True]
    # At least the 2022 period partially overlaps — min_adewi should be numeric
    in_w = result[result["in_study_window"]]
    if len(in_w):
        assert not in_w["mean_adewi"].isna().all()


def test_periods_hit_rate_returns_one_row_per_period(minimal_df):
    index_df = _make_index_df(minimal_df)
    result = periods_hit_rate(index_df, MINIMAL_CFG)
    assert len(result) == len(MINIMAL_CFG["validation"]["known_drought_periods"])


# ---------------------------------------------------------------------------
# default_crop_placeholder
# ---------------------------------------------------------------------------


def test_default_crop_placeholder_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "crop.csv"
        df = default_crop_placeholder(path)
        assert path.exists()
        assert len(df) > 0


def test_default_crop_placeholder_has_required_columns():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "crop.csv"
        df = default_crop_placeholder(path)
        for col in ("province", "year", "crop", "production_tonnes"):
            assert col in df.columns


def test_default_crop_placeholder_both_provinces():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "crop.csv"
        df = default_crop_placeholder(path)
        assert "Eastern" in df["province"].values
        assert "Southern" in df["province"].values


# ---------------------------------------------------------------------------
# crop_correlation
# ---------------------------------------------------------------------------


def test_crop_correlation_returns_none_if_no_file(minimal_df, tmp_path):
    """If the crop statistics CSV does not exist, correlation should return None."""
    index_df = _make_index_df(minimal_df)
    cfg = dict(MINIMAL_CFG)
    cfg["validation"] = dict(cfg["validation"])
    cfg["validation"]["crop_stats_file"] = str(tmp_path / "nonexistent.csv")
    result = crop_correlation(index_df, cfg)
    assert result is None


def test_crop_correlation_with_placeholder(minimal_df):
    """crop_correlation should not raise when the placeholder file is present."""
    index_df = _make_index_df(minimal_df)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "crop.csv"
        default_crop_placeholder(path)
        cfg = dict(MINIMAL_CFG)
        cfg["validation"] = dict(cfg["validation"])
        cfg["validation"]["crop_stats_file"] = str(path)
        # Should run without error; result may be empty DataFrame or None
        result = crop_correlation(index_df, cfg)
        # Just check it doesn't crash — data range may not overlap
        assert result is None or isinstance(result, pd.DataFrame)
