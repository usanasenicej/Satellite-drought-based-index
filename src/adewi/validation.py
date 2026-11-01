"""Validate ADEWI against known drought periods and (optional) crop statistics.

Two validation layers
---------------------
1. **Known-period hit rate** – Does ADEWI cross the drought threshold during
   documented dry spells in Rwanda?
2. **Crop-production correlation** – Do seasonal mean ADEWI values correlate
   with official maize/bean production statistics from NISR / MINAGRI?

Additional analysis
-------------------
* ``evi_correlation()`` – quantifies agreement between EVI and NDVI anomalies
  to justify EVI inclusion in CADI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Known drought period hit rate
# ---------------------------------------------------------------------------

def periods_hit_rate(index_df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    """Check whether ADEWI crosses the drought threshold in each documented period.

    Parameters
    ----------
    index_df:
        Index DataFrame with columns adewi, z_ndvi, time.
    cfg:
        Configuration dict.

    Returns
    -------
    DataFrame with one row per validation period, columns:
    period, start, end, in_study_window, mean_adewi, min_adewi,
    fraction_below_threshold, mean_z_ndvi, detected.
    """
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
                    "mean_z_evi": np.nan,
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
                "mean_z_evi": float(sl["z_evi"].mean()) if "z_evi" in sl.columns else np.nan,
                "detected": bool((sl["adewi"] <= thr).any()),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# EVI–NDVI correlation
# ---------------------------------------------------------------------------

def evi_correlation(index_df: pd.DataFrame) -> pd.DataFrame:
    """Compute correlation between EVI and NDVI standardized anomalies.

    Justifies EVI inclusion in CADI: if the correlation is high, both indices
    measure similar vegetation stress, and a small EVI weight adds robustness
    without introducing an independent signal.

    Parameters
    ----------
    index_df:
        Index DataFrame with columns z_ndvi, z_evi, province.

    Returns
    -------
    DataFrame with columns: province, pearson_r, n, note.
    """
    rows = []
    for prov, g in index_df.groupby("province"):
        valid = g[["z_ndvi", "z_evi"]].dropna()
        r = float(valid["z_ndvi"].corr(valid["z_evi"])) if len(valid) >= 3 else np.nan
        rows.append(
            {
                "province": prov,
                "pearson_r": r,
                "n": len(valid),
                "note": (
                    "High r (>0.80) justifies EVI as a complementary vegetation indicator. "
                    "Lower r suggests EVI captures additional variance."
                ),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Crop-production correlation
# ---------------------------------------------------------------------------

def crop_correlation(index_df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame | None:
    """Correlate annual mean ADEWI with crop production statistics.

    Requires ``data/raw/nisr_crop_production_placeholder.csv`` (or a real
    NISR / MINAGRI seasonal agricultural survey file) with at minimum the
    columns: province, year, production_tonnes.

    Parameters
    ----------
    index_df:
        Index DataFrame.
    cfg:
        Configuration dict.

    Returns
    -------
    DataFrame of correlation results, or None if the crop file is absent or
    incompatible.
    """
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
                "crop": g["crop"].iloc[0] if "crop" in g.columns else "mixed",
                "corr_adewi_production": float(g["adewi"].corr(g["production_tonnes"])),
                "corr_ndvi_production": float(g["z_ndvi"].corr(g["production_tonnes"])),
                "corr_rainfall_production": float(g["z_rainfall"].corr(g["production_tonnes"])),
                "note": (
                    "REPLACE placeholder with NISR Seasonal Agricultural Survey data "
                    "before reporting in the manuscript."
                ),
            }
        )
    return pd.DataFrame(recs) if recs else merged


# ---------------------------------------------------------------------------
# Default placeholder crop file
# ---------------------------------------------------------------------------

def default_crop_placeholder(path: Path) -> pd.DataFrame:
    """Write a schematic NISR-style crop-production table for pipeline testing.

    ⚠️  REPLACE with official NISR / MINAGRI Seasonal Agricultural Survey
    figures for maize and beans (the primary food crops in Eastern and Southern
    Rwanda) before submitting the paper. Values here are schematic, not
    official statistics.

    Parameters
    ----------
    path:
        Target CSV path (parent directories are created if absent).

    Returns
    -------
    DataFrame written to *path*.
    """
    rows = []
    # Schematic maize production (tonnes, provincial aggregate) — REPLACE.
    maize = {
        "Eastern": {
            2018: 148000, 2019: 155000, 2020: 151000,
            2021: 142000, 2022: 128000, 2023: 133000, 2024: 150000,
        },
        "Southern": {
            2018: 121000, 2019: 126000, 2020: 124000,
            2021: 119000, 2022: 112000, 2023: 116000, 2024: 123000,
        },
    }
    # Schematic bean production (tonnes, provincial aggregate) — REPLACE.
    beans = {
        "Eastern": {
            2018: 52000, 2019: 54000, 2020: 53000,
            2021: 49000, 2022: 44000, 2023: 47000, 2024: 51000,
        },
        "Southern": {
            2018: 45000, 2019: 47000, 2020: 46000,
            2021: 43000, 2022: 40000, 2023: 41000, 2024: 44000,
        },
    }
    for crop_name, prov_data in [("maize", maize), ("beans", beans)]:
        for prov, years in prov_data.items():
            for y, prod in years.items():
                rows.append(
                    {
                        "province": prov,
                        "year": y,
                        "crop": crop_name,
                        "production_tonnes": prod,
                        "source": "PLACEHOLDER — replace with NISR SAS / MINAGRI",
                    }
                )
    df = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
