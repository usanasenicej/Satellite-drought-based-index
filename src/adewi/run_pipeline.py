"""End-to-end ADEWI analysis pipeline for Eastern and Southern Rwanda.

Running this module (``python -m adewi``) executes the full analysis:
    1. Load data (observed CSV or synthetic cube)
    2. Preprocess and quality-control
    3. Compute standardized anomalies (Z-scores)
    4. Construct ADEWI and CADI indices
    5. Detect drought events and measure lead times
    6. Seasonal lead-time breakdown (Season A / B / C)
    7. False-alarm analysis
    8. Known-period validation
    9. EVI–NDVI correlation
    10. Crop-production correlation (if data available)
    11. Generate all publication figures
    12. Write tables and JSON run report

Results are written to results/figures/, results/tables/, and
data/processed/adewi_index_timeseries.csv.
"""

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
from .lead_time import analyze_lead_time, false_alarm_rate, lead_time_by_season
from .preprocessing import preprocess
from .validation import crop_correlation, default_crop_placeholder, evi_correlation, periods_hit_rate
from .visualization import make_all_figures


def run(config_path: str | None = None) -> dict:
    """Execute the full ADEWI analysis pipeline.

    Parameters
    ----------
    config_path:
        Optional path to a custom config YAML. Uses ``config/config.yaml``
        relative to the repository root when not specified.

    Returns
    -------
    dict
        JSON-serialisable run report with key metrics, file paths, and provenance.
    """
    cfg = load_config(config_path)
    ensure_dirs(cfg)

    # ------------------------------------------------------------------ #
    # 0. Ensure crop placeholder exists                                   #
    # ------------------------------------------------------------------ #
    crop_path = Path(cfg["validation"]["crop_stats_file"])
    if not crop_path.exists():
        default_crop_placeholder(crop_path)

    # ------------------------------------------------------------------ #
    # 1–3. Load → preprocess → anomalies                                  #
    # ------------------------------------------------------------------ #
    raw_df, cube = load_provincial_timeseries(cfg)
    clean, qc = preprocess(raw_df)
    zdf, clim = compute_anomalies(clean)

    # ------------------------------------------------------------------ #
    # 4. Build indices                                                     #
    # ------------------------------------------------------------------ #
    index_df = compute_indices(zdf, cfg)

    # ------------------------------------------------------------------ #
    # 5. Lead-time analysis                                               #
    # ------------------------------------------------------------------ #
    events, lead_summary = analyze_lead_time(index_df, cfg)

    # ------------------------------------------------------------------ #
    # 6. Seasonal lead-time breakdown                                     #
    # ------------------------------------------------------------------ #
    seasonal_lead = lead_time_by_season(events) if not events.empty else pd.DataFrame()

    # ------------------------------------------------------------------ #
    # 7. False-alarm analysis (per province, pooled)                      #
    # ------------------------------------------------------------------ #
    thr_a = float(cfg["drought"]["adewi_event_threshold"])
    min_len = int(cfg["drought"]["min_event_steps"])
    fa_tables = []
    for prov, g in index_df.groupby("province"):
        g = g.sort_values("time").reset_index(drop=True)
        from .lead_time import detect_events as _det
        ndvi_ev = _det(g, "z_ndvi", float(cfg["drought"]["ndvi_event_threshold"]), min_len)
        fa = false_alarm_rate(g, ndvi_ev, thr_a, min_len)
        if not fa.empty:
            fa["province"] = prov
            fa_tables.append(fa)
    false_alarms_df = pd.concat(fa_tables, ignore_index=True) if fa_tables else pd.DataFrame()
    fa_rate_overall = float(false_alarms_df["false_alarm"].mean()) if not false_alarms_df.empty else np.nan

    # ------------------------------------------------------------------ #
    # 8. Known-period validation                                          #
    # ------------------------------------------------------------------ #
    periods = periods_hit_rate(index_df, cfg)

    # ------------------------------------------------------------------ #
    # 9. EVI–NDVI correlation                                             #
    # ------------------------------------------------------------------ #
    evi_corr = evi_correlation(index_df)

    # ------------------------------------------------------------------ #
    # 10. Crop-production correlation                                     #
    # ------------------------------------------------------------------ #
    crop = crop_correlation(index_df, cfg)

    # ------------------------------------------------------------------ #
    # 11. Spatial ADEWI cube (map figures)                               #
    # ------------------------------------------------------------------ #
    adewi_cube = spatial_adewi_cube(cube, cfg) if cube is not None else None

    # ------------------------------------------------------------------ #
    # 12. Figures + tables                                               #
    # ------------------------------------------------------------------ #
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
        seasonal_lead=seasonal_lead,
        false_alarms=false_alarms_df,
        evi_corr=evi_corr,
    )

    # ------------------------------------------------------------------ #
    # Run report                                                          #
    # ------------------------------------------------------------------ #
    overall = lead_summary[lead_summary["province"] == "Eastern+Southern"]
    mean_lead = float(overall["mean_lead_weeks"].iloc[0]) if len(overall) else np.nan
    success = float(overall["success_rate"].iloc[0]) if len(overall) else np.nan

    report = {
        "data_source": str(clean["data_source"].iloc[0]) if "data_source" in clean.columns else "unknown",
        "n_timesteps": int(clean.groupby("province").size().iloc[0]),
        "period": [str(clean["time"].min().date()), str(clean["time"].max().date())],
        "mean_lead_weeks": mean_lead,
        "success_rate": success,
        "false_alarm_rate": fa_rate_overall,
        "n_figures": len(figures),
        "figures": [str(p) for p in figures],
        "tables": {k: str(v) for k, v in tables.items()},
        "lead_summary": lead_summary.to_dict(orient="records"),
        "seasonal_lead": seasonal_lead.to_dict(orient="records") if not seasonal_lead.empty else [],
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
