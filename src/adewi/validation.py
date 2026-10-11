"""Validate ADEWI against known drought periods and (optional) crop statistics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def periods_hit_rate(index_df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    thr = float(cfg["drought"]["adewi_event_threshold"])
    rows = []
    for period in cfg["validation"]["known_drought_periods"]:
        start, end = pd.Timestamp(period["start"]), pd.Timestamp(period["end"])
        if end < index_df["time"].min() or start > index_df["time"].max():
            rows.append(
                {
                    "period": period["label"],
                    "start": start,
                    "end": end,
                    "in_study_window": False,
                    "mean_adewi": np.nan,
                    "min_adewi": np.nan,
                    "fraction_below_threshold": np.nan,
                    "mean_z_ndvi": np.nan,
                    "detected": False,
                }
            )
            continue
        sl = index_df[(index_df["time"] >= start) & (index_df["time"] <= end)]
        rows.append(
            {
                "period": period["label"],
                "start": start,
                "end": end,
                "in_study_window": True,
                "mean_adewi": float(sl["adewi"].mean()),
                "min_adewi": float(sl["adewi"].min()),
                "fraction_below_threshold": float((sl["adewi"] <= thr).mean()),
                "mean_z_ndvi": float(sl["z_ndvi"].mean()),
                "detected": bool((sl["adewi"] <= thr).any()),
            }
        )
    return pd.DataFrame(rows)


def crop_correlation(index_df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame | None:
    path = Path(cfg["validation"]["crop_stats_file"])
    if not path.exists():
        return None
    crops = pd.read_csv(path)
    if "year" not in crops.columns:
        return None
    seasonal = (
        index_df.groupby(["province", "year"])[["adewi", "cadi", "z_ndvi", "z_rainfall"]]
        .mean()
        .reset_index()
    )
    merged = seasonal.merge(crops, on=["province", "year"], how="inner")
    if merged.empty or "production_tonnes" not in merged.columns:
        return merged
    recs = []
    for prov, g in merged.groupby("province"):
        if g["production_tonnes"].nunique() < 3:
            continue
        recs.append(
            {
                "province": prov,
                "n_years": len(g),
                "corr_adewi_production": float(g["adewi"].corr(g["production_tonnes"])),
                "corr_ndvi_production": float(g["z_ndvi"].corr(g["production_tonnes"])),
                "corr_rainfall_production": float(g["z_rainfall"].corr(g["production_tonnes"])),
            }
        )
    return pd.DataFrame(recs) if recs else merged


def default_crop_placeholder(path: Path) -> pd.DataFrame:
    """Illustrative NISR-style table so the validation module has a file to merge.

    REPLACE with official NISR / MINAGRI seasonal agricultural survey figures
    before submitting the paper. Values here are schematic, not official statistics.
    """
    rows = []
    # Schematic maize production (tonnes, provincial aggregate) — REPLACE.
    schematic = {
        "Eastern": {2018: 148000, 2019: 155000, 2020: 151000, 2021: 142000, 2022: 128000, 2023: 133000, 2024: 150000},
        "Southern": {2018: 121000, 2019: 126000, 2020: 124000, 2021: 119000, 2022: 112000, 2023: 116000, 2024: 123000},
    }
    for prov, years in schematic.items():
        for y, prod in years.items():
            rows.append(
                {
                    "province": prov,
                    "year": y,
                    "crop": "maize",
                    "production_tonnes": prod,
                    "source": "PLACEHOLDER — replace with NISR SAS / MINAGRI",
                }
            )
    df = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
