import pandas as pd
import pytest

from adewi.schema import validate_environmental_timeseries


def test_validate_environmental_timeseries():
    df = pd.DataFrame({
        "province": ["Eastern", "Eastern"],
        "time": ["2020-01-01", "2020-01-17"],
        "ndvi": [0.6, 0.7],
        "rainfall": [40.0, 50.0],
        "soil_moisture": [0.25, 0.30],
        "lst": [300.0, 305.0],
    })

    rep = validate_environmental_timeseries(df)
    assert rep.is_valid
    assert len(rep.errors) == 0

    # Bad column range
    bad_df = df.copy()
    bad_df["ndvi"] = [1.5, 2.0]
    rep_bad = validate_environmental_timeseries(bad_df)
    assert not rep_bad.is_valid
    assert rep_bad.range_violations["ndvi"] == 2
