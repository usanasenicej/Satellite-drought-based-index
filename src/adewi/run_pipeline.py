"""End-to-end ADEWI analysis for Eastern and Southern Rwanda."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .anomalies import compute_anomalies
from .combined_index import compute_indices, spatial_adewi_cube
from .config import ensure_dirs, load_config
from .data_loading import load_provincial_timeseries
from .export import write_tables
from .lead_time import analyze_lead_time
from .preprocessing import preprocess
from .validation import crop_correlation, default_crop_placeholder, periods_hit_rate
from .visualization import make_all_figures


def run(config_path: str | None = None) -> dict:
    cfg = load_config(config_path)
    ensure_dirs(cfg)

    crop_path = Path(cfg["validation"]["crop_stats_file"])
    if not crop_path.exists():
        default_crop_placeholder(crop_path)

    raw_df, cube = load_provincial_timeseries(cfg)
    clean, qc = preprocess(raw_df)
    zdf, clim = compute_anomalies(clean)
    index_df = compute_indices(zdf, cfg)
    events, lead_summary = analyze_lead_time(index_df, cfg)
    periods = periods_hit_rate(index_df, cfg)
    crop = crop_correlation(index_df, cfg)

    adewi_cube = spatial_adewi_cube(cube, cfg) if cube is not None else None

    figures = make_all_figures(
        index_df,
        events,
        periods,
        Path(cfg["paths"]["figures"]),
        cube=cube,
        adewi_cube=adewi_cube,
    )
    tables = write_tables(
        index_df,
        clim,
        events,
        lead_summary,
        qc,
        periods,
        Path(cfg["paths"]["tables"]),
        Path(cfg["paths"]["data_processed"]),
        crop_corr=crop,
    )

    overall = lead_summary[lead_summary["province"] == "Eastern+Southern"]
    mean_lead = float(overall["mean_lead_weeks"].iloc[0]) if len(overall) else np.nan
    success = float(overall["success_rate"].iloc[0]) if len(overall) else np.nan

    report = {
        "data_source": str(clean["data_source"].iloc[0]) if "data_source" in clean.columns else "unknown",
        "n_timesteps": int(clean.groupby("province").size().iloc[0]),
        "period": [str(clean["time"].min().date()), str(clean["time"].max().date())],
        "mean_lead_weeks": mean_lead,
        "success_rate": success,
        "n_figures": len(figures),
        "figures": [str(p) for p in figures],
        "tables": {k: str(v) for k, v in tables.items()},
        "lead_summary": lead_summary.to_dict(orient="records"),
        "note": (
            "If data_source is 'synthetic', replace data/processed/provincial_timeseries.csv "
            "with a GEE/DE Africa export before interpreting results scientifically."
        ),
    }
    out = Path(cfg["paths"]["results"]) / "run_report.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Rwanda ADEWI analysis pipeline")
    parser.add_argument("--config", default=None, help="Path to config YAML")
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
