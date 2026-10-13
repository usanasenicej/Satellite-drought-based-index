"""Unit tests for adewi.preprocessing module.

Tests cover:
- Physical range clipping (clip_physical_ranges)
- Gap interpolation (interpolate_gaps)
- Calendar column attachment (add_calendar)
- Quality summary generation (quality_summary)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adewi.preprocessing import (
    add_calendar,
    clip_physical_ranges,
    interpolate_gaps,
    preprocess,
    quality_summary,
)


# ---------------------------------------------------------------------------
# clip_physical_ranges
# ---------------------------------------------------------------------------


def test_clip_ndvi_above_one():
    df = pd.DataFrame(
        {
            "time": pd.date_range("2022-01-01", periods=3, freq="16D"),
            "province": ["Eastern"] * 3,
            "ndvi": [1.5, -0.1, 0.6],
            "evi": [0.4, 0.4, 0.4],
            "rainfall": [20.0, 20.0, 20.0],
            "soil_moisture": [0.2, 0.2, 0.2],
            "lst": [300.0, 300.0, 300.0],
        }
    )
    out = clip_physical_ranges(df)
    assert out["ndvi"].max() <= 1.0
    assert out["ndvi"].min() >= 0.0


def test_clip_rainfall_non_negative():
    df = pd.DataFrame(
        {
            "time": pd.date_range("2022-01-01", periods=2, freq="16D"),
            "province": ["Southern"] * 2,
            "ndvi": [0.5, 0.5],
            "evi": [0.3, 0.3],
            "rainfall": [-5.0, 30.0],
            "soil_moisture": [0.1, 0.1],
            "lst": [305.0, 305.0],
        }
    )
    out = clip_physical_ranges(df)
    assert out["rainfall"].min() >= 0.0


def test_clip_lst_physical_range():
    df = pd.DataFrame(
        {
            "time": pd.date_range("2022-01-01", periods=2, freq="16D"),
            "province": ["Eastern"] * 2,
            "ndvi": [0.5, 0.5],
            "evi": [0.3, 0.3],
            "rainfall": [10.0, 10.0],
            "soil_moisture": [0.2, 0.2],
            "lst": [100.0, 400.0],  # both out of range
        }
    )
    out = clip_physical_ranges(df)
    assert out["lst"].min() >= 250.0
    assert out["lst"].max() <= 340.0


# ---------------------------------------------------------------------------
# interpolate_gaps
# ---------------------------------------------------------------------------


def test_interpolate_short_gap_filled():
    times = pd.date_range("2022-01-01", periods=5, freq="16D")
    df = pd.DataFrame(
        {
            "time": times,
            "province": ["Eastern"] * 5,
            "ndvi": [0.5, np.nan, np.nan, 0.5, 0.5],
            "evi": [0.3] * 5,
            "rainfall": [20.0] * 5,
            "soil_moisture": [0.2] * 5,
            "lst": [300.0] * 5,
        }
    )
    out = interpolate_gaps(df, limit=2)
    assert out["ndvi"].isna().sum() == 0


def test_interpolate_long_gap_not_filled():
    """Gaps longer than `limit` should remain NaN at the edges."""
    times = pd.date_range("2022-01-01", periods=7, freq="16D")
    ndvi = [0.5, np.nan, np.nan, np.nan, np.nan, np.nan, 0.5]
    df = pd.DataFrame(
        {
            "time": times,
            "province": ["Eastern"] * 7,
            "ndvi": ndvi,
            "evi": [0.3] * 7,
            "rainfall": [20.0] * 7,
            "soil_moisture": [0.2] * 7,
            "lst": [300.0] * 7,
        }
    )
    # limit=2 means at most 2 consecutive NaNs are filled
    out = interpolate_gaps(df, limit=2)
    assert out["ndvi"].isna().sum() > 0


# ---------------------------------------------------------------------------
# add_calendar
# ---------------------------------------------------------------------------


def test_calendar_columns_present():
    df = pd.DataFrame(
        {
            "time": pd.date_range("2022-01-01", periods=3, freq="16D"),
            "province": ["Eastern"] * 3,
        }
    )
    out = add_calendar(df)
    for col in ("year", "month", "week", "doy", "season"):
        assert col in out.columns


def test_season_a_in_september():
    df = pd.DataFrame(
        {
            "time": [pd.Timestamp("2022-09-15")],
            "province": ["Eastern"],
        }
    )
    out = add_calendar(df)
    assert out.loc[0, "season"] == "A"


def test_season_b_in_march():
    df = pd.DataFrame(
        {
            "time": [pd.Timestamp("2022-03-01")],
            "province": ["Southern"],
        }
    )
    out = add_calendar(df)
    assert out.loc[0, "season"] == "B"


# ---------------------------------------------------------------------------
# quality_summary
# ---------------------------------------------------------------------------


def test_quality_summary_columns(minimal_df):
    clean, summary = preprocess(minimal_df)
    assert "province" in summary.columns
    assert "n_timesteps" in summary.columns
    assert "ndvi_missing_pct" in summary.columns


def test_quality_summary_no_missing_in_clean(minimal_df):
    clean, summary = preprocess(minimal_df)
    assert summary["ndvi_missing_pct"].max() == pytest.approx(0.0, abs=1e-6)
