"""Combined Agricultural Drought Index (CADI) and Agricultural Drought Early-Warning Index (ADEWI).

Research brief formulas
-----------------------
ADEWI (vegetation-independent, designed to lead NDVI):
    ADEWI = 0.40·Z_rainfall + 0.35·Z_soil_moisture − 0.25·Z_LST

CADI (comprehensive status index that includes vegetation):
    CADI = 0.30·Z_NDVI + 0.15·Z_EVI + 0.30·Z_rainfall + 0.20·Z_SM − 0.20·Z_LST
    (weights from research brief §2; total ≈ 1.15 unnormalised)

Drought classification (research brief §2):
    Normal   ≥ −0.5
    Mild     −0.5 to −1.0
    Moderate −1.0 to −1.5
    Severe   −1.5 to −2.0
    Extreme  < −2.0

Negative values indicate drought-favourable conditions.
ADEWI excludes vegetation so its signals can be compared against NDVI
without incorporating vegetation into both sides of the comparison.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Drought classification
# ---------------------------------------------------------------------------

def classify_drought(index: pd.Series, classes: dict[str, float] | None = None) -> pd.Series:
    """Classify standardized index values into drought severity categories.

    Thresholds match the research brief:
        Normal   ≥ −0.5
        Mild     −0.5 to −1.0
        Moderate −1.0 to −1.5
        Severe   −1.5 to −2.0
        Extreme  < −2.0

    Parameters
    ----------
    index:
        Series of standardized anomaly values.
    classes:
        Optional override dict mapping label → threshold (lower bound).
        Keys must include at least Mild, Moderate, Severe, Extreme.

    Returns
    -------
    pd.Series of string labels, same index as *index*.
    """
    if classes is None:
        classes = {
            "Mild": -0.5,
            "Moderate": -1.0,
            "Severe": -1.5,
            "Extreme": -2.0,
        }
    mild_thr = float(classes.get("Mild", -0.5))
    moderate_thr = float(classes.get("Moderate", -1.0))
    severe_thr = float(classes.get("Severe", -1.5))
    extreme_thr = float(classes.get("Extreme", -2.0))

    labels = []
    for x in index:
        if pd.isna(x):
            labels.append("Missing")
        elif x < extreme_thr:
            labels.append("Extreme")
        elif x < severe_thr:
            labels.append("Severe")
        elif x < moderate_thr:
            labels.append("Moderate")
        elif x < mild_thr:
            labels.append("Mild")
        else:
            labels.append("Normal")
    return pd.Series(labels, index=index.index)


# ---------------------------------------------------------------------------
# Index computation
# ---------------------------------------------------------------------------

def compute_indices(zdf: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    """Compute ADEWI and CADI from Z-score anomalies using config weights.

    Parameters
    ----------
    zdf:
        DataFrame with columns z_ndvi, z_evi, z_rainfall, z_soil_moisture, z_lst,
        province, and time.
    cfg:
        Configuration dict (from config/config.yaml).

    Returns
    -------
    DataFrame with additional columns: adewi, cadi, adewi_class, cadi_class, ndvi_class.
    """
    w_a = cfg["weights"]["adewi"]
    w_c = cfg["weights"]["cadi"]
    out = zdf.copy()

    # ADEWI: vegetation-independent early warning signal
    out["adewi"] = (
        w_a["rainfall"] * out["z_rainfall"]
        + w_a["soil_moisture"] * out["z_soil_moisture"]
        - w_a["lst"] * out["z_lst"]
    )
    # CADI: comprehensive drought status (includes vegetation)
    out["cadi"] = (
        w_c["ndvi"] * out["z_ndvi"]
        + w_c["evi"] * out["z_evi"]
        + w_c["rainfall"] * out["z_rainfall"]
        + w_c["soil_moisture"] * out["z_soil_moisture"]
        - w_c["lst"] * out["z_lst"]
    )

    classes = cfg["drought"]["classes"]

    out["adewi_class"] = classify_drought(out["adewi"], classes)
    out["cadi_class"] = classify_drought(out["cadi"], classes)
    out["ndvi_class"] = classify_drought(out["z_ndvi"], classes)
    out["evi_class"] = classify_drought(out["z_evi"], classes)
    return out


def compute_cadi_paper(zdf: pd.DataFrame) -> pd.Series:
    """Compute CADI using the exact weights specified in the research brief.

    Formula (research brief §2):
        CADI = 0.30·Z_NDVI + 0.15·Z_EVI + 0.30·Z_rain + 0.20·Z_SM − 0.20·Z_LST

    This convenience function bypasses the YAML config and applies the brief
    weights directly, which is useful for sensitivity comparisons.

    Parameters
    ----------
    zdf:
        DataFrame with columns z_ndvi, z_evi, z_rainfall, z_soil_moisture, z_lst.

    Returns
    -------
    pd.Series of CADI values (same index as *zdf*).
    """
    return (
        0.30 * zdf["z_ndvi"]
        + 0.15 * zdf["z_evi"]
        + 0.30 * zdf["z_rainfall"]
        + 0.20 * zdf["z_soil_moisture"]
        - 0.20 * zdf["z_lst"]
    )


# ---------------------------------------------------------------------------
# Spatial ADEWI cube
# ---------------------------------------------------------------------------

def spatial_adewi_cube(cube: dict[str, Any], cfg: dict[str, Any]) -> np.ndarray:
    """Compute ADEWI on a spatial raster cube using pixel-level climatology.

    Climatology is computed per pixel and day-of-year bin (16-day) to remove
    seasonal cycles before drought detection.

    Parameters
    ----------
    cube:
        Spatial data cube as returned by ``synthetic_data.generate_cube()``.
    cfg:
        Configuration dict.

    Returns
    -------
    np.ndarray of shape (n_time, n_lat, n_lon) with ADEWI values.
    NaN outside the study-area mask.
    """
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
