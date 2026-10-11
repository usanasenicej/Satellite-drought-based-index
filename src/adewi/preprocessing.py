"""Cleaning, alignment and quality control of provincial time series."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .synthetic_data import VARIABLES


def interpolate_gaps(df: pd.DataFrame, limit: int = 2) -> pd.DataFrame:
    out = df.copy()
    for prov, g in out.groupby("province"):
        idx = g.index
        for v in VARIABLES:
            out.loc[idx, v] = g[v].interpolate(limit=limit, limit_direction="both")
    return out


def clip_physical_ranges(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ndvi"] = out["ndvi"].clip(0.0, 1.0)
    out["evi"] = out["evi"].clip(0.0, 1.0)
    out["rainfall"] = out["rainfall"].clip(lower=0.0)
    out["soil_moisture"] = out["soil_moisture"].clip(0.0, 0.6)
    out["lst"] = out["lst"].clip(250.0, 340.0)
    return out


def add_calendar(df: pd.DataFrame) -> pd.DataFrame:
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
    clean = clip_physical_ranges(interpolate_gaps(df))
    clean = add_calendar(clean)
    summary = quality_summary(clean)
    return clean, summary
