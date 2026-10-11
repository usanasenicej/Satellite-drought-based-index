"""Write tables and processed series for the paper and the Streamlit app."""

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
) -> dict[str, Path]:
    tables_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "index": processed_dir / "adewi_index_timeseries.csv",
        "climatology": processed_dir / "climatology.csv",
        "events": tables_dir / "table_lead_time_events.csv",
        "lead_summary": tables_dir / "table_lead_time_summary.csv",
        "qc": tables_dir / "table_data_quality.csv",
        "periods": tables_dir / "table_known_drought_validation.csv",
        "index_xlsx": tables_dir / "adewi_full_results.xlsx",
    }
    index_df.to_csv(paths["index"], index=False)
    clim.to_csv(paths["climatology"], index=False)
    events.to_csv(paths["events"], index=False)
    lead_summary.to_csv(paths["lead_summary"], index=False)
    qc.to_csv(paths["qc"], index=False)
    periods.to_csv(paths["periods"], index=False)
    if crop_corr is not None:
        p = tables_dir / "table_crop_correlation.csv"
        crop_corr.to_csv(p, index=False)
        paths["crop"] = p

    with pd.ExcelWriter(paths["index_xlsx"]) as xl:
        index_df.to_excel(xl, sheet_name="index", index=False)
        lead_summary.to_excel(xl, sheet_name="lead_summary", index=False)
        events.to_excel(xl, sheet_name="events", index=False)
        periods.to_excel(xl, sheet_name="validation_periods", index=False)
        qc.to_excel(xl, sheet_name="quality", index=False)
    return paths
