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
    return ((doy - 1) // step) * step + 1


def climatology(df: pd.DataFrame, variables: tuple[str, ...] = VARIABLES) -> pd.DataFrame:
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
    clim = climatology(df)
    zdf = zscores(df, clim)
    return zdf, clim
