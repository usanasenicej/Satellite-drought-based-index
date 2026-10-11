"""Combined Agricultural Drought Index (CADI) and Agricultural Drought Early-Warning Index (ADEWI).

ADEWI (vegetation-independent, designed to lead NDVI):
    ADEWI = w_r * Z_rainfall + w_sm * Z_soil_moisture - w_lst * Z_LST

CADI (status index that includes vegetation):
    CADI = w_n * Z_NDVI + w_e * Z_EVI + w_r * Z_rainfall + w_sm * Z_SM - w_lst * Z_LST

Negative values indicate drought-favourable conditions.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def classify_drought(index: pd.Series, classes: dict[str, float] | None = None) -> pd.Series:
    """User specification: Mild < -0.5, Moderate < -1.0, Severe < -1.5, Extreme < -2.0."""
    labels = []
    for x in index:
        if pd.isna(x):
            labels.append("Missing")
        elif x < -2.0:
            labels.append("Extreme")
        elif x < -1.5:
            labels.append("Severe")
        elif x < -1.0:
            labels.append("Moderate")
        elif x < -0.5:
            labels.append("Mild")
        else:
            labels.append("Normal")
    return pd.Series(labels, index=index.index)


def compute_indices(zdf: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    w_a = cfg["weights"]["adewi"]
    w_c = cfg["weights"]["cadi"]
    out = zdf.copy()

    out["adewi"] = (
        w_a["rainfall"] * out["z_rainfall"]
        + w_a["soil_moisture"] * out["z_soil_moisture"]
        - w_a["lst"] * out["z_lst"]
    )
    out["cadi"] = (
        w_c["ndvi"] * out["z_ndvi"]
        + w_c["evi"] * out["z_evi"]
        + w_c["rainfall"] * out["z_rainfall"]
        + w_c["soil_moisture"] * out["z_soil_moisture"]
        - w_c["lst"] * out["z_lst"]
    )

    classes = cfg["drought"]["classes"]
    # Ensure Extreme is represented
    class_cfg = dict(classes)
    class_cfg.setdefault("Severe", -2.0)

    out["adewi_class"] = classify_drought(out["adewi"], class_cfg)
    out["cadi_class"] = classify_drought(out["cadi"], class_cfg)
    out["ndvi_class"] = classify_drought(out["z_ndvi"], class_cfg)
    return out


def spatial_adewi_cube(cube: dict[str, Any], cfg: dict[str, Any]) -> np.ndarray:
    """Compute ADEWI on the spatial cube using a simple climatology over time (per pixel, per doy-bin)."""
    from .anomalies import _doy_bin

    w = cfg["weights"]["adewi"]
    times = cube["time"]
    doy = pd.Series(times.dayofyear)
    bins = _doy_bin(doy).to_numpy()
    unique_bins = np.unique(bins)

    def zfield(arr: np.ndarray) -> np.ndarray:
        z = np.full_like(arr, np.nan, dtype=float)
        for b in unique_bins:
            idx = np.where(bins == b)[0]
            sl = arr[idx]
            mean = np.nanmean(sl, axis=0)
            std = np.nanstd(sl, axis=0, ddof=1)
            std = np.where(std == 0, np.nan, std)
            z[idx] = (sl - mean) / std
        return z

    z_r = zfield(cube["rainfall"])
    z_s = zfield(cube["soil_moisture"])
    z_t = zfield(cube["lst"])
    adewi = w["rainfall"] * z_r + w["soil_moisture"] * z_s - w["lst"] * z_t
    mask = cube["mask"]
    adewi[:, ~mask] = np.nan
    return adewi
