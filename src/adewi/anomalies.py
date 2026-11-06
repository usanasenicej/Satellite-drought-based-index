"""Standardized anomalies (Z-scores) relative to the 2018–2024 climatology.

Z = (x - mean_doy) / std_doy

Climatology is computed per province and day-of-year (binned to the 16-day
composite calendar) so that Season A/B cycles are removed before drought detection.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .synthetic_data import VARIABLES


def _doy_bin(doy: pd.Series, step: int = 16) -> pd.Series:
    """Bin day-of-year into step-sized intervals aligned with MODIS composites.

    Parameters
    ----------
    doy : pd.Series
        Day of year values (1 to 366).
    step : int, default 16
        Interval width in days.

    Returns
    -------
    pd.Series
        Binned day of year identifiers.
    """
    return ((doy - 1) // step) * step + 1


def climatology(df: pd.DataFrame, variables: tuple[str, ...] = VARIABLES) -> pd.DataFrame:
    """Compute seasonal climatological means and standard deviations.

    Calculates mean and sample standard deviation for each environmental variable
    grouped by province and 16-day day-of-year composite bin.

    Parameters
    ----------
    df : pd.DataFrame
        Preprocessed environmental time-series containing columns 'province',
        'doy', and each variable in ``variables``.
    variables : tuple of str, default VARIABLES
        List of variable names to compute climatology for.

    Returns
    -------
    pd.DataFrame
        Climatology table with columns ['province', 'doy_bin', 'n',
        '{var}_mean', '{var}_std', ...].
    """
    work = df.copy()
    work["doy_bin"] = _doy_bin(work["doy"])
    rows = []
    for (prov, doy), g in work.groupby(["province", "doy_bin"]):
        rec: dict[str, Any] = {"province": prov, "doy_bin": int(doy), "n": len(g)}
        for v in variables:
            rec[f"{v}_mean"] = g[v].mean()
            rec[f"{v}_std"] = g[v].std(ddof=1)
        rows.append(rec)
    return pd.DataFrame(rows)


def zscores(df: pd.DataFrame, clim: pd.DataFrame, variables: tuple[str, ...] = VARIABLES) -> pd.DataFrame:
    """Compute standardized anomalies (Z-scores) against seasonal climatology.

    Subtracts the province/doy-bin mean and divides by standard deviation for each
    variable. Positive LST anomalies indicate unusually hot conditions.

    Parameters
    ----------
    df : pd.DataFrame
        Input observations with 'province', 'doy', and environmental variables.
    clim : pd.DataFrame
        Climatological reference statistics produced by :func:`climatology`.
    variables : tuple of str, default VARIABLES
        List of variable names to standardize.

    Returns
    -------
    pd.DataFrame
        Merged DataFrame containing original variables and added 'z_{var}' columns.
    """
    work = df.copy()
    work["doy_bin"] = _doy_bin(work["doy"])
    merged = work.merge(clim, on=["province", "doy_bin"], how="left")
    for v in variables:
        mean = merged[f"{v}_mean"]
        std = merged[f"{v}_std"].replace(0, np.nan)
        merged[f"z_{v}"] = (merged[v] - mean) / std
        # High LST is drought-like; keep raw z_lst (positive = hotter than normal)
    return merged


def compute_anomalies(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute full standardized anomaly dataset and reference climatology.

    Parameters
    ----------
    df : pd.DataFrame
        Preprocessed time-series dataset.

    Returns
    -------
    tuple of (pd.DataFrame, pd.DataFrame)
        A tuple containing:
        - zdf: DataFrame with standardized anomaly columns (z_ndvi, z_rainfall, etc.).
        - clim: Reference climatology table used for standardization.
    """
    clim = climatology(df)
    zdf = zscores(df, clim)
    return zdf, clim
