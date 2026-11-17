import pandas as pd
import pytest

from adewi.delay_metrics import analyze_detection_dynamics


def test_analyze_detection_dynamics():
    # Construct a dataset where an early alert at t=1 is followed by vegetation drop at t=3
    df = pd.DataFrame({
        "date": pd.date_range("2021-01-01", periods=6, freq="16D"),
        "adewi": [0.0, -1.5, -1.2, 0.0, 0.5, 0.0],
        "z_ndvi": [0.0, 0.0, -0.5, -1.2, -1.5, 0.0],
    })

    points = analyze_detection_dynamics(
        df,
        index_col="adewi",
        target_col="z_ndvi",
        thresholds=[-1.0],
        target_threshold=-1.0,
        window_periods=3,
    )

    assert len(points) == 1
    pt = points[0]
    assert pt.true_alarms > 0
    assert pt.mean_lead_days > 0
    assert pt.false_discovery_rate <= 1.0
