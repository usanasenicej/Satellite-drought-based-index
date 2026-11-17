import numpy as np
import pandas as pd
import pytest

from adewi.synthetic_data import _enso_iod_cycle, inject_cloud_gaps


def test_enso_iod_cycle():
    dates = pd.date_range("2018-01-01", "2024-12-31", freq="16D")
    cycle = _enso_iod_cycle(dates)
    assert len(cycle) == len(dates)
    assert cycle.min() < 0
    assert cycle.max() > 0


def test_inject_cloud_gaps():
    arr = np.ones((10, 10))
    corrupted = inject_cloud_gaps(arr, gap_rate=0.2, seed=42)
    assert np.isnan(corrupted).sum() > 0
    assert np.isnan(corrupted).sum() < 50
    # No gap test
    clean = inject_cloud_gaps(arr, gap_rate=0.0)
    assert not np.isnan(clean).any()
