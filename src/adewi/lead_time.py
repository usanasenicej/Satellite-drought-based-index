"""Lead-time analysis: weeks by which ADEWI crosses a drought threshold before NDVI.

For each NDVI drought event (z_ndvi below threshold for min_event_steps consecutive
composites), search backward for the first ADEWI crossing of the same threshold.
Lead time = (NDVI onset − ADEWI onset) converted to weeks.

16-day composites → weeks = days / 7.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _runs_below(series: pd.Series, threshold: float, min_len: int) -> list[tuple[int, int]]:
    """Return (start_pos, end_pos) inclusive runs in positional index."""
    below = (series.to_numpy() <= threshold)
    runs = []
    i, n = 0, len(below)
    while i < n:
        if not below[i]:
            i += 1
            continue
        j = i
        while j < n and below[j]:
            j += 1
        if (j - i) >= min_len:
            runs.append((i, j - 1))
        i = j
    return runs


def detect_events(prov_df: pd.DataFrame, column: str, threshold: float, min_len: int) -> pd.DataFrame:
    prov_df = prov_df.sort_values("time").reset_index(drop=True)
    runs = _runs_below(prov_df[column], threshold, min_len)
    rows = []
    for k, (i, j) in enumerate(runs, start=1):
        rows.append(
            {
                "event_id": k,
                "onset": prov_df.loc[i, "time"],
                "end": prov_df.loc[j, "time"],
                "duration_steps": j - i + 1,
                "peak_value": float(prov_df.loc[i:j, column].min()),
                "onset_pos": i,
                "end_pos": j,
            }
        )
    return pd.DataFrame(rows)


def match_lead_times(
    prov_df: pd.DataFrame,
    ndvi_events: pd.DataFrame,
    threshold: float,
    search_window_steps: int = 12,
) -> pd.DataFrame:
    """For each NDVI event, find the earliest ADEWI crossing in the preceding window."""
    df = prov_df.sort_values("time").reset_index(drop=True)
    rows = []
    for _, ev in ndvi_events.iterrows():
        i0 = int(ev["onset_pos"])
        i_start = max(0, i0 - search_window_steps)
        window = df.loc[i_start:i0]
        below = window["adewi"] <= threshold
        if below.any():
            first_pos = below[below].index[0]
            adewi_onset = df.loc[first_pos, "time"]
            ndvi_onset = ev["onset"]
            lead_days = (ndvi_onset - adewi_onset).days
            detected = True
        else:
            adewi_onset = pd.NaT
            lead_days = np.nan
            detected = False
        rows.append(
            {
                "ndvi_event_id": ev["event_id"],
                "ndvi_onset": ev["onset"],
                "ndvi_end": ev["end"],
                "ndvi_peak": ev["peak_value"],
                "adewi_onset": adewi_onset,
                "lead_days": lead_days,
                "lead_weeks": lead_days / 7.0 if pd.notna(lead_days) else np.nan,
                "detected": detected,
            }
        )
    return pd.DataFrame(rows)


def analyze_lead_time(index_df: pd.DataFrame, cfg: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    thr_n = float(cfg["drought"]["ndvi_event_threshold"])
    thr_a = float(cfg["drought"]["adewi_event_threshold"])
    min_len = int(cfg["drought"]["min_event_steps"])

    event_tables = []
    summary_rows = []
    for prov, g in index_df.groupby("province"):
        g = g.sort_values("time").reset_index(drop=True)
        ndvi_events = detect_events(g, "z_ndvi", thr_n, min_len)
        if ndvi_events.empty:
            summary_rows.append(
                {
                    "province": prov,
                    "n_ndvi_events": 0,
                    "n_detected": 0,
                    "success_rate": np.nan,
                    "mean_lead_weeks": np.nan,
                    "median_lead_weeks": np.nan,
                    "max_lead_weeks": np.nan,
                    "min_lead_weeks": np.nan,
                }
            )
            continue
        matches = match_lead_times(g, ndvi_events, thr_a)
        matches["province"] = prov
        event_tables.append(matches)
        det = matches[matches["detected"]]
        summary_rows.append(
            {
                "province": prov,
                "n_ndvi_events": len(matches),
                "n_detected": int(matches["detected"].sum()),
                "success_rate": float(matches["detected"].mean()),
                "mean_lead_weeks": float(det["lead_weeks"].mean()) if len(det) else np.nan,
                "median_lead_weeks": float(det["lead_weeks"].median()) if len(det) else np.nan,
                "max_lead_weeks": float(det["lead_weeks"].max()) if len(det) else np.nan,
                "min_lead_weeks": float(det["lead_weeks"].min()) if len(det) else np.nan,
            }
        )

    events = pd.concat(event_tables, ignore_index=True) if event_tables else pd.DataFrame()
    summary = pd.DataFrame(summary_rows)

    if not events.empty:
        det = events[events["detected"]]
        overall = {
            "province": "Eastern+Southern",
            "n_ndvi_events": len(events),
            "n_detected": int(events["detected"].sum()),
            "success_rate": float(events["detected"].mean()),
            "mean_lead_weeks": float(det["lead_weeks"].mean()) if len(det) else np.nan,
            "median_lead_weeks": float(det["lead_weeks"].median()) if len(det) else np.nan,
            "max_lead_weeks": float(det["lead_weeks"].max()) if len(det) else np.nan,
            "min_lead_weeks": float(det["lead_weeks"].min()) if len(det) else np.nan,
        }
        summary = pd.concat([summary, pd.DataFrame([overall])], ignore_index=True)

    return events, summary
