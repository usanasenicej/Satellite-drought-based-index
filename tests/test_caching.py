import pandas as pd
import pytest

from adewi.caching import CacheManager


def test_cache_manager(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    params = {"threshold": -1.0, "lead": 2}

    h1 = cache.compute_hash(df, params)
    assert len(h1) == 64
    assert not cache.is_cached("anomaly_stage", h1)

    cache.update_stage("anomaly_stage", h1)
    assert cache.is_cached("anomaly_stage", h1)

    # Change param -> hash changes
    h2 = cache.compute_hash(df, {"threshold": -1.5, "lead": 2})
    assert h1 != h2
    assert not cache.is_cached("anomaly_stage", h2)

    cache.clear()
    assert not cache.is_cached("anomaly_stage", h1)
