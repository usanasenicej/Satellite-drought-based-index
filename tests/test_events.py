import pandas as pd
import pytest

from adewi.events import extract_drought_events


def test_extract_drought_events():
    df = pd.DataFrame({
        "region": ["Eastern"] * 7,
        "date": ["2020-01-01", "2020-01-17", "2020-02-02", "2020-02-18", "2020-03-05", "2020-03-21", "2020-04-06"],
        "adewi": [0.5, -1.2, -2.0, -1.5, -0.2, -1.8, 0.2],
    })

    events = extract_drought_events(df, index_col="adewi", threshold=-1.0)
    assert len(events) == 2

    # First event: indices 1, 2, 3 (values -1.2, -2.0, -1.5)
    ev1 = events.iloc[0]
    assert ev1["duration_periods"] == 3
    assert ev1["duration_days"] == 48
    assert ev1["start_date"] == "2020-01-17"
    assert ev1["end_date"] == "2020-02-18"
    assert ev1["peak_date"] == "2020-02-02"
    assert ev1["peak_intensity"] == 1.0  # abs(-2.0 - (-1.0))

    # Second event: index 5 (value -1.8)
    ev2 = events.iloc[1]
    assert ev2["duration_periods"] == 1
    assert ev2["duration_days"] == 16
