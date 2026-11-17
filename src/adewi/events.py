"""Drought event characterization based on Yevjevich's run theory.

Quantifies:
- Consecutive drought spell onset, termination, and duration.
- Cumulative deficit (drought severity).
- Peak intensity and timing.
- Inter-arrival and recovery periods.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import pandas as pd


@dataclass
class DroughtEvent:
    event_id: int
    region: str
    start_date: str
    end_date: str
    duration_periods: int
    duration_days: int
    cumulative_severity: float
    peak_intensity: float
    peak_date: str


def extract_drought_events(
    df: pd.DataFrame,
    index_col: str = "adewi",
    threshold: float = -1.0,
    date_col: str = "date",
    region_col: str = "region",
    period_days: int = 16,
) -> pd.DataFrame:
    """Extract drought events using threshold run-theory on an anomaly index.

    A drought event starts when the index falls below threshold, and ends
    when it recovers to or above the threshold.
    """
    if df.empty or index_col not in df.columns:
        return pd.DataFrame()

    results: list[dict] = []
    regions = df[region_col].unique() if region_col in df.columns else ["All"]

    event_counter = 1
    for reg in regions:
        reg_df = df[df[region_col] == reg] if region_col in df.columns else df
        reg_df = reg_df.sort_values(date_col).reset_index(drop=True)

        in_event = False
        cur_start_idx = 0
        cur_peak_intensity = 0.0
        cur_peak_date = ""
        cur_severity = 0.0

        for i, row in reg_df.iterrows():
            val = row[index_col]
            dt = str(row[date_col])

            if pd.notna(val) and val <= threshold:
                deficit = abs(val - threshold)
                if not in_event:
                    in_event = True
                    cur_start_idx = i
                    cur_severity = deficit
                    cur_peak_intensity = deficit
                    cur_peak_date = dt
                else:
                    cur_severity += deficit
                    if deficit > cur_peak_intensity:
                        cur_peak_intensity = deficit
                        cur_peak_date = dt
            else:
                if in_event:
                    end_idx = i - 1
                    dur = end_idx - cur_start_idx + 1
                    results.append(
                        asdict(
                            DroughtEvent(
                                event_id=event_counter,
                                region=str(reg),
                                start_date=str(reg_df.loc[cur_start_idx, date_col]),
                                end_date=str(reg_df.loc[end_idx, date_col]),
                                duration_periods=dur,
                                duration_days=dur * period_days,
                                cumulative_severity=round(cur_severity, 3),
                                peak_intensity=round(cur_peak_intensity, 3),
                                peak_date=cur_peak_date,
                            )
                        )
                    )
                    event_counter += 1
                    in_event = False

        if in_event:
            end_idx = len(reg_df) - 1
            dur = end_idx - cur_start_idx + 1
            results.append(
                asdict(
                    DroughtEvent(
                        event_id=event_counter,
                        region=str(reg),
                        start_date=str(reg_df.loc[cur_start_idx, date_col]),
                        end_date=str(reg_df.loc[end_idx, date_col]),
                        duration_periods=dur,
                        duration_days=dur * period_days,
                        cumulative_severity=round(cur_severity, 3),
                        peak_intensity=round(cur_peak_intensity, 3),
                        peak_date=cur_peak_date,
                    )
                )
            )
            event_counter += 1

    return pd.DataFrame(results)
