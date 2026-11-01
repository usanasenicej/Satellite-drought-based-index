"""Write tables and processed series for the paper and the Streamlit app.

Outputs
-------
data/processed/
    adewi_index_timeseries.csv  – full index time series
    climatology.csv             – seasonal climatology reference

results/tables/
    table_lead_time_events.csv          – per-event lead-time table
    table_lead_time_summary.csv         – per-province and pooled summary
    table_data_quality.csv              – missing-value and QC summary
    table_known_drought_validation.csv  – hit rate vs documented periods
    table_seasonal_lead_time.csv        – lead times by Rwanda season (A/B/C)
    table_false_alarms.csv              – ADEWI events with no NDVI match
    table_evi_ndvi_correlation.csv      – EVI–NDVI correlation by province
    table_crop_correlation.csv          – crop-production correlation (optional)
    adewi_full_results.xlsx             – multi-sheet Excel workbook
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_tables(
    index_df: pd.DataFrame,
    clim: pd.DataFrame,
    events: pd.DataFrame,
    lead_summary: pd.DataFrame,
    qc: pd.DataFrame,
    periods: pd.DataFrame,
    tables_dir: Path,
    processed_dir: Path,
    crop_corr: pd.DataFrame | None = None,
    seasonal_lead: pd.DataFrame | None = None,
    false_alarms: pd.DataFrame | None = None,
    evi_corr: pd.DataFrame | None = None,
    sensitivity: pd.DataFrame | None = None,
) -> dict[str, Path]:
    """Write all result tables to CSV and a multi-sheet Excel workbook.

    Parameters
    ----------
    index_df:
        Full index time series.
    clim:
        Seasonal climatology table.
    events:
        Per-event lead-time results.
    lead_summary:
        Aggregated lead-time summary per province.
    qc:
        Data quality summary.
    periods:
        Known drought period validation.
    tables_dir:
        Output directory for tables.
    processed_dir:
        Output directory for processed data files.
    crop_corr:
        Optional crop-production correlation table.
    seasonal_lead:
        Optional seasonal lead-time breakdown (A/B/C).
    false_alarms:
        Optional false-alarm table.
    evi_corr:
        Optional EVI–NDVI correlation table.
    sensitivity:
        Optional sensitivity-analysis results (written if present).

    Returns
    -------
    Dict mapping short name → file path for all written files.
    """
    tables_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path] = {
        "index": processed_dir / "adewi_index_timeseries.csv",
        "climatology": processed_dir / "climatology.csv",
        "events": tables_dir / "table_lead_time_events.csv",
        "lead_summary": tables_dir / "table_lead_time_summary.csv",
        "qc": tables_dir / "table_data_quality.csv",
        "periods": tables_dir / "table_known_drought_validation.csv",
        "index_xlsx": tables_dir / "adewi_full_results.xlsx",
    }

    # Core CSV outputs
    index_df.to_csv(paths["index"], index=False)
    clim.to_csv(paths["climatology"], index=False)
    events.to_csv(paths["events"], index=False)
    lead_summary.to_csv(paths["lead_summary"], index=False)
    qc.to_csv(paths["qc"], index=False)
    periods.to_csv(paths["periods"], index=False)

    # Optional extras
    if crop_corr is not None:
        p = tables_dir / "table_crop_correlation.csv"
        crop_corr.to_csv(p, index=False)
        paths["crop"] = p

    if seasonal_lead is not None and not seasonal_lead.empty:
        p = tables_dir / "table_seasonal_lead_time.csv"
        seasonal_lead.to_csv(p, index=False)
        paths["seasonal_lead"] = p

    if false_alarms is not None and not false_alarms.empty:
        p = tables_dir / "table_false_alarms.csv"
        false_alarms.to_csv(p, index=False)
        paths["false_alarms"] = p

    if evi_corr is not None and not evi_corr.empty:
        p = tables_dir / "table_evi_ndvi_correlation.csv"
        evi_corr.to_csv(p, index=False)
        paths["evi_corr"] = p

    if sensitivity is not None and not sensitivity.empty:
        p = tables_dir / "table_sensitivity_analysis.csv"
        sensitivity.to_csv(p, index=False, float_format="%.3f")
        paths["sensitivity"] = p

    # Multi-sheet Excel workbook
    with pd.ExcelWriter(paths["index_xlsx"], engine="openpyxl") as xl:
        index_df.to_excel(xl, sheet_name="index", index=False)
        lead_summary.to_excel(xl, sheet_name="lead_summary", index=False)
        events.to_excel(xl, sheet_name="events", index=False)
        periods.to_excel(xl, sheet_name="validation_periods", index=False)
        qc.to_excel(xl, sheet_name="quality", index=False)
        if seasonal_lead is not None and not seasonal_lead.empty:
            seasonal_lead.to_excel(xl, sheet_name="seasonal_lead", index=False)
        if false_alarms is not None and not false_alarms.empty:
            false_alarms.to_excel(xl, sheet_name="false_alarms", index=False)
        if evi_corr is not None and not evi_corr.empty:
            evi_corr.to_excel(xl, sheet_name="evi_ndvi_corr", index=False)
        if sensitivity is not None and not sensitivity.empty:
            sensitivity.to_excel(xl, sheet_name="sensitivity", index=False)

    return paths
