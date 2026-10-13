"""Shared pytest fixtures for ADEWI unit tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def minimal_df() -> pd.DataFrame:
    """Minimal two-province synthetic DataFrame with all required columns.

    Covers two full Rwanda seasons (Season A and B) across 2022–2023 so that
    the 16-day climatology bins are populated enough for Z-score computation.
    Uses a fixed random seed for reproducibility.
    """
    rng = np.random.default_rng(0)
    times = pd.date_range("2022-01-01", periods=48, freq="16D")
    rows = []
    for prov in ("Eastern", "Southern"):
        for t in times:
            rows.append(
                {
                    "time": t,
                    "province": prov,
                    "ndvi": float(rng.uniform(0.2, 0.8)),
                    "evi": float(rng.uniform(0.1, 0.6)),
                    "rainfall": float(rng.uniform(0.0, 80.0)),
                    "soil_moisture": float(rng.uniform(0.05, 0.4)),
                    "lst": float(rng.uniform(290.0, 320.0)),
                    "data_source": "synthetic",
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture
def preprocessed_df(minimal_df: pd.DataFrame) -> pd.DataFrame:
    """Return a calendar-enriched, clipped DataFrame ready for anomaly computation."""
    from adewi.preprocessing import preprocess

    clean, _ = preprocess(minimal_df)
    return clean
