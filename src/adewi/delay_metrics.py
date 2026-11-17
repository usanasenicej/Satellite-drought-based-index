"""Detection delay and false alarm dynamics for early warning systems.

Calculates:
- Mean Detection Lead / Delay (MDD in days and composite periods)
- False Alarm Rate (FAR) and False Discovery Rate (FDR)
- Missed Event Rate (MER)
- Threshold trade-off curve across alert sensitivity levels
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class TradeoffPoint:
    threshold: float
    true_alarms: int
    false_alarms: int
    missed_events: int
    false_discovery_rate: float
    mean_lead_days: float


def analyze_detection_dynamics(
    df: pd.DataFrame,
    index_col: str = "adewi",
    target_col: str = "z_ndvi",
    thresholds: list[float] | None = None,
    target_threshold: float = -1.0,
    window_periods: int = 4,
    period_days: int = 16,
) -> list[TradeoffPoint]:
    """Sweep warning thresholds to calculate lead time, false alarms, and missed events."""
    if thresholds is None:
        thresholds = [-0.5, -0.75, -1.0, -1.25, -1.5, -2.0]

    if df.empty or index_col not in df.columns or target_col not in df.columns:
        return []

    results: list[TradeoffPoint] = []
    data = df.sort_values("date").reset_index(drop=True)

    target_drought = (data[target_col] <= target_threshold).values
    n = len(data)

    for thresh in thresholds:
        index_alert = (data[index_col] <= thresh).values
        true_alarms = 0
        false_alarms = 0
        leads: list[int] = []

        for i in range(n):
            if index_alert[i]:
                # Check whether target drought occurs within future window [i, i + window_periods]
                future_window = target_drought[i : min(n, i + window_periods + 1)]
                if np.any(future_window):
                    true_alarms += 1
                    # Find first target drought step
                    first_hit = np.argmax(future_window)
                    leads.append(first_hit * period_days)
                else:
                    false_alarms += 1

        # Target drought events with no preceding alert within window
        missed = 0
        for j in range(n):
            if target_drought[j]:
                past_window = index_alert[max(0, j - window_periods) : j + 1]
                if not np.any(past_window):
                    missed += 1

        total_alarms = true_alarms + false_alarms
        fdr = false_alarms / total_alarms if total_alarms > 0 else 0.0
        avg_lead = float(np.mean(leads)) if leads else 0.0

        results.append(
            TradeoffPoint(
                threshold=thresh,
                true_alarms=true_alarms,
                false_alarms=false_alarms,
                missed_events=missed,
                false_discovery_rate=round(fdr, 3),
                mean_lead_days=round(avg_lead, 1),
            )
        )

    return results
