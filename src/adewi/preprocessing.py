"""Cleaning, alignment and quality control of provincial time series."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .synthetic_data import VARIABLES


def interpolate_gaps(df: pd.DataFrame, limit: int = 2) -> pd.DataFrame:
    """Linearly interpolate missing values within short data gaps per province.

    Parameters
    ----------
    df : pd.DataFrame
        Input observations with 'province' and variable columns.
    limit : int, default 2
        Maximum number of consecutive NaN values to fill in both directions.

    Returns
    -------
    pd.DataFrame
        DataFrame with short gaps interpolated.
    """
    out = df.copy()
    for prov, g in out.groupby("province"):
        idx = g.index
        for v in VARIABLES:
            out.loc[idx, v] = g[v].interpolate(limit=limit, limit_direction="both")
    return out


def clip_physical_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Clamp environmental variables to physically plausible terrestrial bounds.

    Bounds applied:
    - ndvi, evi: [0.0, 1.0] (vegetation index range)
    - rainfall: >= 0.0 mm
    - soil_moisture: [0.0, 0.6] m3/m3 (volumetric water content)
    - lst: [250.0, 340.0] Kelvin (~ -23°C to 67°C)

    Parameters
    ----------
    df : pd.DataFrame
        Input observations.

    Returns
    -------
    pd.DataFrame
        DataFrame with values clipped to physical limits.
    """
    out = df.copy()
    out["ndvi"] = out["ndvi"].clip(0.0, 1.0)
    out["evi"] = out["evi"].clip(0.0, 1.0)
    out["rainfall"] = out["rainfall"].clip(lower=0.0)
    out["soil_moisture"] = out["soil_moisture"].clip(0.0, 0.6)
    out["lst"] = out["lst"].clip(250.0, 340.0)
    return out


def add_calendar(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich time-series with agricultural calendar metadata for Rwanda.

    Adds:
    - year, month, week, doy (day of year)
    - season:
        - "A": Season A (September through January)
        - "B": Season B (February through June)
        - "C": Season C (July and August marshland/dry season)

    Parameters
    ----------
    df : pd.DataFrame
        Input observations with a 'time' datetime column.

    Returns
    -------
    pd.DataFrame
        DataFrame enriched with calendar columns.
    """
    out = df.copy()
    out["year"] = out["time"].dt.year
    out["month"] = out["time"].dt.month
    out["week"] = out["time"].dt.isocalendar().week.astype(int)
    out["doy"] = out["time"].dt.dayofyear
    # Agricultural seasons commonly used in Rwanda
    out["season"] = np.where(
        out["month"].isin([9, 10, 11, 12, 1]),
        "A",
        np.where(out["month"].isin([2, 3, 4, 5, 6]), "B", "C"),
    )
    return out


def quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate quality-control summary metrics per province.

    Parameters
    ----------
    df : pd.DataFrame
        Input preprocessed observations.

    Returns
    -------
    pd.DataFrame
        Table summarizing timestep counts, date ranges, and missingness
        percentage for each variable.
    """
    rows = []
    for prov, g in df.groupby("province"):
        rec: dict[str, Any] = {"province": prov, "n_timesteps": len(g)}
        for v in VARIABLES:
            rec[f"{v}_missing_pct"] = 100.0 * g[v].isna().mean()
        rec["date_start"] = g["time"].min()
        rec["date_end"] = g["time"].max()
        rows.append(rec)
    return pd.DataFrame(rows)


def preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute complete data preprocessing and quality control workflow.

    Clips physical ranges, interpolates short missingness gaps, attaches
    calendar/seasonal identifiers, and compiles quality assurance metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Raw time-series observations.

    Returns
    -------
    tuple of (pd.DataFrame, pd.DataFrame)
        A tuple containing:
        - clean: Cleaned and calendar-annotated DataFrame.
        - summary: Quality assurance summary table.
    """
    clean = clip_physical_ranges(interpolate_gaps(df))
    clean = add_calendar(clean)
    summary = quality_summary(clean)
    return clean, summary
