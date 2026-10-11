from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adewi.lead_time import _runs_below, detect_events, match_lead_times


def test_runs_below_min_length():
    s = pd.Series([0, -1.2, -1.3, 0.1, -2.0, 0.2, -1.1, -1.2, -1.4])
    runs = _runs_below(s, -1.0, min_len=2)
    assert runs == [(1, 2), (6, 8)]


def test_lead_time_positive_when_adewi_leads():
    n = 20
    times = pd.date_range("2022-01-01", periods=n, freq="16D")
    z_ndvi = pd.Series([0.0] * n)
    adewi = pd.Series([0.0] * n)
    # ADEWI drops from step 4, NDVI from step 7
    adewi.iloc[4:12] = -1.2
    z_ndvi.iloc[7:14] = -1.3
    df = pd.DataFrame({"time": times, "z_ndvi": z_ndvi, "adewi": adewi})
    events = detect_events(df, "z_ndvi", -1.0, 2)
    matches = match_lead_times(df, events, -1.0)
    assert matches.iloc[0]["detected"]
    assert matches.iloc[0]["lead_weeks"] > 0
