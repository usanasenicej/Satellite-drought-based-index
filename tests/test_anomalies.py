"""Unit tests for adewi.anomalies module.

Tests cover:
- DOY binning helper (_doy_bin)
- Climatology table construction (climatology)
- Z-score normalization (zscores)
- Full compute_anomalies roundtrip
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adewi.anomalies import _doy_bin, climatology, compute_anomalies, zscores
from adewi.preprocessing import preprocess


# ---------------------------------------------------------------------------
# _doy_bin
# ---------------------------------------------------------------------------


def test_doy_bin_january_first():
    # DOY 1 → bin 1
    result = _doy_bin(pd.Series([1]))
    assert result.iloc[0] == 1


def test_doy_bin_day_17():
    # DOY 17 → (17-1)//16 * 16 + 1 = 1*16+1 = 17
    result = _doy_bin(pd.Series([17]))
    assert result.iloc[0] == 17


def test_doy_bin_same_for_composites():
    # Days 1–16 all map to bin 1
    series = pd.Series(range(1, 17))
    bins = _doy_bin(series)
    assert (bins == 1).all()


# ---------------------------------------------------------------------------
# climatology
# ---------------------------------------------------------------------------


def test_climatology_has_mean_and_std_columns(preprocessed_df):
    clim = climatology(preprocessed_df)
    assert "ndvi_mean" in clim.columns
    assert "ndvi_std" in clim.columns
    assert "province" in clim.columns
    assert "doy_bin" in clim.columns


def test_climatology_n_equals_years_sampled(preprocessed_df):
    clim = climatology(preprocessed_df)
    # Each (province, doy_bin) group should have at least 1 sample
    assert (clim["n"] >= 1).all()


def test_climatology_std_non_negative(preprocessed_df):
    clim = climatology(preprocessed_df)
    for v in ("ndvi", "evi", "rainfall", "soil_moisture", "lst"):
        assert (clim[f"{v}_std"] >= 0).all()


# ---------------------------------------------------------------------------
# zscores
# ---------------------------------------------------------------------------


def test_zscores_columns_present(preprocessed_df):
    clim = climatology(preprocessed_df)
    zdf = zscores(preprocessed_df, clim)
    for col in ("z_ndvi", "z_evi", "z_rainfall", "z_soil_moisture", "z_lst"):
        assert col in zdf.columns


def test_zscores_roughly_standardized(preprocessed_df):
    """Mean Z-score across all bins should be near 0 (within rounding)."""
    clim = climatology(preprocessed_df)
    zdf = zscores(preprocessed_df, clim)
    for col in ("z_ndvi", "z_rainfall"):
        mean_z = zdf[col].mean()
        assert abs(mean_z) < 1.0, f"{col} mean Z-score unexpectedly large: {mean_z}"


# ---------------------------------------------------------------------------
# compute_anomalies roundtrip
# ---------------------------------------------------------------------------


def test_compute_anomalies_returns_tuple(preprocessed_df):
    result = compute_anomalies(preprocessed_df)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_compute_anomalies_zdf_has_z_ndvi(preprocessed_df):
    zdf, clim = compute_anomalies(preprocessed_df)
    assert "z_ndvi" in zdf.columns


def test_compute_anomalies_clim_not_empty(preprocessed_df):
    zdf, clim = compute_anomalies(preprocessed_df)
    assert len(clim) > 0


def test_compute_anomalies_no_all_nan_z(preprocessed_df):
    """Z-score columns should not be entirely NaN (would indicate a merge failure)."""
    zdf, _ = compute_anomalies(preprocessed_df)
    for col in ("z_ndvi", "z_rainfall", "z_soil_moisture", "z_lst"):
        assert zdf[col].notna().any(), f"{col} is entirely NaN"
