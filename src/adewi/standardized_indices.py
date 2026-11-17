"""Standardized remote sensing drought indices: VCI, TCI, and VHI.

Implements Kogan's (1990, 1995) drought indices:
- Vegetation Condition Index (VCI)
- Temperature Condition Index (TCI)
- Vegetation Health Index (VHI)
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_vci(
    df: pd.DataFrame,
    ndvi_col: str = "ndvi",
    group_col: str = "doy_bin",
    region_col: str = "region",
) -> pd.Series:
    """Compute the Vegetation Condition Index (VCI).

    VCI = 100 * (NDVI - NDVI_min) / (NDVI_max - NDVI_min)
    computed per seasonal DOY composite bin and region.
    """
    if df.empty or ndvi_col not in df.columns:
        return pd.Series(index=df.index, dtype=float)

    cols = [c for c in [region_col, group_col] if c in df.columns]
    if cols:
        grouped = df.groupby(cols)[ndvi_col]
        min_val = grouped.transform("min")
        max_val = grouped.transform("max")
    else:
        min_val = df[ndvi_col].min()
        max_val = df[ndvi_col].max()

    rng = max_val - min_val
    # Avoid zero division
    rng = rng.replace(0, np.nan)
    vci = 100.0 * (df[ndvi_col] - min_val) / rng
    return vci.clip(lower=0.0, upper=100.0)


def compute_tci(
    df: pd.DataFrame,
    lst_col: str = "lst",
    group_col: str = "doy_bin",
    region_col: str = "region",
) -> pd.Series:
    """Compute the Temperature Condition Index (TCI).

    TCI = 100 * (LST_max - LST) / (LST_max - LST_min)
    Higher temperatures indicate greater thermal stress, resulting in lower TCI.
    """
    if df.empty or lst_col not in df.columns:
        return pd.Series(index=df.index, dtype=float)

    cols = [c for c in [region_col, group_col] if c in df.columns]
    if cols:
        grouped = df.groupby(cols)[lst_col]
        min_val = grouped.transform("min")
        max_val = grouped.transform("max")
    else:
        min_val = df[lst_col].min()
        max_val = df[lst_col].max()

    rng = max_val - min_val
    rng = rng.replace(0, np.nan)
    tci = 100.0 * (max_val - df[lst_col]) / rng
    return tci.clip(lower=0.0, upper=100.0)


def compute_vhi(
    vci: pd.Series,
    tci: pd.Series,
    alpha: float = 0.5,
) -> pd.Series:
    """Compute the Vegetation Health Index (VHI).

    VHI = alpha * VCI + (1 - alpha) * TCI
    where alpha typically equals 0.5.
    """
    return (alpha * vci + (1.0 - alpha) * tci).clip(lower=0.0, upper=100.0)


def classify_vhi(vhi: pd.Series | float) -> pd.Series | str:
    """Classify VHI into standard drought severity categories:
    - Extreme Drought: < 10
    - Severe Drought: 10 - 20
    - Moderate Drought: 20 - 30
    - Mild Drought: 30 - 40
    - No Drought: >= 40
    """
    def _cat(val: float) -> str:
        if pd.isna(val):
            return "Unknown"
        if val < 10.0:
            return "Extreme Drought"
        if val < 20.0:
            return "Severe Drought"
        if val < 30.0:
            return "Moderate Drought"
        if val < 40.0:
            return "Mild Drought"
        return "No Drought"

    if isinstance(vhi, (int, float, np.floating)):
        return _cat(float(vhi))
    return vhi.apply(_cat)
