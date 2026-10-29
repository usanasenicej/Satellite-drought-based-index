"""Lead-time analysis: weeks by which ADEWI crosses a drought threshold before NDVI.

For each NDVI drought event (z_ndvi below threshold for min_event_steps consecutive
composites), search backward for the first ADEWI crossing of the same threshold.
Lead time = (NDVI onset − ADEWI onset) converted to weeks.

16-day composites → weeks = days / 7.

Additional analyses
-------------------
- False-alarm rate: ADEWI events with no matching NDVI event within a forward window.
- Seasonal breakdown: lead times stratified by Rwanda growing season (A / B / C).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Event detection helpers
# ---------------------------------------------------------------------------

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


def detect_events(
    prov_df: pd.DataFrame,
    column: str,
    threshold: float,
    min_len: int,
) -> pd.DataFrame:
    """Detect sustained threshold crossings in *column* and return event table.

    Parameters
    ----------
    prov_df:
        Time-sorted DataFrame for a single province.
    column:
        Column name to scan (e.g. ``'z_ndvi'`` or ``'adewi'``).
    threshold:
        Inclusive threshold; values ≤ threshold trigger an event.
    min_len:
        Minimum number of consecutive steps to constitute an event.

    Returns
    -------
    DataFrame with one row per event and columns:
    event_id, onset, end, duration_steps, peak_value, onset_pos, end_pos.
    """
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
                "season": prov_df.loc[i, "season"] if "season" in prov_df.columns else None,
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Lead-time matching
# ---------------------------------------------------------------------------

def match_lead_times(
    prov_df: pd.DataFrame,
    ndvi_events: pd.DataFrame,
    threshold: float,
    search_window_steps: int = 12,
) -> pd.DataFrame:
    """For each NDVI event, find the earliest ADEWI crossing in the preceding window.

    Parameters
    ----------
    prov_df:
        Province time series with columns adewi and time.
    ndvi_events:
        Event table from ``detect_events()`` for NDVI.
    threshold:
        ADEWI threshold (usually same as NDVI threshold).
    search_window_steps:
        How many 16-day composites to look back (default 12 ≈ 6 months).

    Returns
    -------
    DataFrame with lead-time results and a *detected* boolean column.
    """
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
                "ndvi_season": ev.get("season"),
                "adewi_onset": adewi_onset,
                "lead_days": lead_days,
                "lead_weeks": lead_days / 7.0 if pd.notna(lead_days) else np.nan,
                "detected": detected,
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# False-alarm rate
# ---------------------------------------------------------------------------

def false_alarm_rate(
    prov_df: pd.DataFrame,
    ndvi_events: pd.DataFrame,
    threshold: float,
    min_len: int,
    forward_window_steps: int = 8,
) -> pd.DataFrame:
    """Identify ADEWI events not followed by a matching NDVI event (false alarms).

    An ADEWI event is a 'false alarm' if no NDVI event starts within
    *forward_window_steps* 16-day composites after the ADEWI onset.

    Parameters
    ----------
    prov_df:
        Province time series.
    ndvi_events:
        Table of detected NDVI drought events.
    threshold:
        Detection threshold applied to ADEWI.
    min_len:
        Minimum event duration (composites).
    forward_window_steps:
        Search window forward from ADEWI onset to look for an NDVI response.

    Returns
    -------
    DataFrame with columns: adewi_event_id, adewi_onset, false_alarm,
    nearest_ndvi_event_days, province.
    """
    df = prov_df.sort_values("time").reset_index(drop=True)
    adewi_events = detect_events(df, "adewi", threshold, min_len)

    ndvi_onsets = (
        pd.to_datetime(ndvi_events["onset"]).values
        if not ndvi_events.empty
        else np.array([], dtype="datetime64[ns]")
    )

    rows = []
    for _, aev in adewi_events.iterrows():
        a_onset = pd.Timestamp(aev["onset"])
        # look forward up to forward_window_steps × 16 days
        horizon = a_onset + pd.Timedelta(days=forward_window_steps * 16)
        in_window = ndvi_onsets[
            (ndvi_onsets >= np.datetime64(a_onset)) & (ndvi_onsets <= np.datetime64(horizon))
        ]
        if len(in_window) == 0:
            nearest_days = np.nan
            false_alarm = True
        else:
            nearest_days = float(
                (pd.Timestamp(in_window.min()) - a_onset).days
            )
            false_alarm = False
        rows.append(
            {
                "adewi_event_id": aev["event_id"],
                "adewi_onset": a_onset,
                "adewi_season": aev.get("season"),
                "adewi_peak": aev["peak_value"],
                "false_alarm": false_alarm,
                "nearest_ndvi_onset_days": nearest_days,
            }
        )

    result = pd.DataFrame(rows)
    if not result.empty:
        fa_rate = float(result["false_alarm"].mean())
        result.attrs["false_alarm_rate"] = fa_rate
    return result


# ---------------------------------------------------------------------------
# Seasonal lead-time breakdown
# ---------------------------------------------------------------------------

def lead_time_by_season(events: pd.DataFrame) -> pd.DataFrame:
    """Summarise lead times stratified by Rwanda growing season (A / B / C).

    Season A: September – January (long rains)
    Season B: February – June (short rains)
    Season C: July – August (dry season, minor cropping)

    Parameters
    ----------
    events:
        Lead-time event table as returned by ``analyze_lead_time()``.

    Returns
    -------
    DataFrame with columns: season, n_events, n_detected, success_rate,
    mean_lead_weeks, median_lead_weeks, max_lead_weeks.
    """
    if events.empty or "ndvi_season" not in events.columns:
        return pd.DataFrame(
            columns=["season", "n_events", "n_detected", "success_rate",
                     "mean_lead_weeks", "median_lead_weeks", "max_lead_weeks"]
        )

    rows = []
    for season, g in events.groupby("ndvi_season"):
        det = g[g["detected"]]
        rows.append(
            {
                "season": season,
                "n_events": len(g),
                "n_detected": int(g["detected"].sum()),
                "success_rate": float(g["detected"].mean()),
                "mean_lead_weeks": float(det["lead_weeks"].mean()) if len(det) else np.nan,
                "median_lead_weeks": float(det["lead_weeks"].median()) if len(det) else np.nan,
                "max_lead_weeks": float(det["lead_weeks"].max()) if len(det) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("season")


# ---------------------------------------------------------------------------
# Main analysis entry point
# ---------------------------------------------------------------------------

def analyze_lead_time(
    index_df: pd.DataFrame,
    cfg: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run full lead-time analysis for all provinces.

    Detects NDVI drought events, matches them to preceding ADEWI signals,
    and computes per-province and pooled summary statistics.

    Parameters
    ----------
    index_df:
        Output from ``combined_index.compute_indices()``.
    cfg:
        Configuration dict.

    Returns
    -------
    events:
        Row-per-event table with lead-time values.
    summary:
        Per-province + pooled summary statistics.
    """
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
