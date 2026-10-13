#!/usr/bin/env python
"""Sensitivity analysis for ADEWI index weights.

The manuscript (Section 3.4 / Discussion) notes that equal-weight and
leave-one-variable-out tests can be reported as a robustness check.  This
script runs three sensitivity scenarios for each province and prints a
comparison table.

Usage (from the repo root):
    python scripts/sensitivity_analysis.py

Outputs:
    results/tables/table_sensitivity_analysis.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adewi.anomalies import compute_anomalies
from adewi.combined_index import classify_drought, compute_indices
from adewi.config import ensure_dirs, load_config
from adewi.data_loading import load_provincial_timeseries
from adewi.lead_time import analyze_lead_time
from adewi.preprocessing import preprocess

# ---------------------------------------------------------------------------
# Weight scenarios
# ---------------------------------------------------------------------------

SCENARIOS: dict[str, dict] = {
    "default (0.40/0.35/0.25)": {
        "rainfall": 0.40,
        "soil_moisture": 0.35,
        "lst": 0.25,
    },
    "equal weight (1/3 each)": {
        "rainfall": 1 / 3,
        "soil_moisture": 1 / 3,
        "lst": 1 / 3,
    },
    "leave-out rainfall (0/0.58/0.42)": {
        "rainfall": 0.00,
        "soil_moisture": 0.58,
        "lst": 0.42,
    },
    "leave-out soil moisture (0.62/0/0.38)": {
        "rainfall": 0.62,
        "soil_moisture": 0.00,
        "lst": 0.38,
    },
    "leave-out LST (0.53/0.47/0)": {
        "rainfall": 0.53,
        "soil_moisture": 0.47,
        "lst": 0.00,
    },
    "rainfall-dominant (0.60/0.30/0.10)": {
        "rainfall": 0.60,
        "soil_moisture": 0.30,
        "lst": 0.10,
    },
    "soil-moisture-dominant (0.25/0.60/0.15)": {
        "rainfall": 0.25,
        "soil_moisture": 0.60,
        "lst": 0.15,
    },
}


def run_scenario(
    zdf: pd.DataFrame,
    cfg: dict,
    scenario_name: str,
    adewi_weights: dict,
) -> pd.DataFrame:
    """Compute ADEWI with custom weights, run lead-time analysis, return summary."""
    import copy

    local_cfg = copy.deepcopy(cfg)
    local_cfg["weights"]["adewi"] = adewi_weights

    index_df = compute_indices(zdf, local_cfg)
    _, summary = analyze_lead_time(index_df, local_cfg)

    overall = summary[summary["province"] == "Eastern+Southern"]
    if overall.empty:
        return pd.DataFrame()

    row = overall.iloc[0].to_dict()
    row["scenario"] = scenario_name
    row["w_rainfall"] = adewi_weights["rainfall"]
    row["w_soil_moisture"] = adewi_weights["soil_moisture"]
    row["w_lst"] = adewi_weights["lst"]
    return pd.DataFrame([row])


def main() -> None:
    cfg = load_config()
    ensure_dirs(cfg)

    raw_df, _ = load_provincial_timeseries(cfg)
    clean, _ = preprocess(raw_df)
    zdf, _ = compute_anomalies(clean)

    results = []
    for name, weights in SCENARIOS.items():
        print(f"  Running scenario: {name} …")
        row_df = run_scenario(zdf, cfg, name, weights)
        if not row_df.empty:
            results.append(row_df)

    if not results:
        print("No events detected in any scenario — check data source.")
        return

    table = pd.concat(results, ignore_index=True)

    # Reorder columns for readability
    front = ["scenario", "w_rainfall", "w_soil_moisture", "w_lst",
             "n_ndvi_events", "n_detected", "success_rate",
             "mean_lead_weeks", "median_lead_weeks", "max_lead_weeks"]
    cols = front + [c for c in table.columns if c not in front]
    table = table[cols]

    out = Path(cfg["paths"]["tables"]) / "table_sensitivity_analysis.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False, float_format="%.3f")

    print("\n=== ADEWI Sensitivity Analysis (pooled Eastern+Southern) ===\n")
    print(table.to_string(index=False))
    print(f"\nSaved → {out}")


if __name__ == "__main__":
    main()
