"""Physically motivated synthetic satellite/climate series for Rwanda.

This module exists so the full ADEWI pipeline can be developed, tested and
demonstrated BEFORE Google Earth Engine / Digital Earth Africa exports are
available. Results from this generator MUST NOT be submitted as observational
findings. Every output file is tagged with data_source = 'synthetic'.

Design:
- Bimodal rainfall (Season A: Sep–Dec; Season B: Feb–May), typical of Rwanda.
- Known dry episodes around 2022 Season A and early 2023 in the Eastern Province.
- Rainfall and soil-moisture deficits lead vegetation decline by ~3 sixteen-day
  composites (~6 weeks), which is the phenomenon ADEWI is meant to capture.
- LST rises as soil moisture falls.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .regions import PROVINCE_BBOX, province_mask


VARIABLES = ("ndvi", "evi", "rainfall", "soil_moisture", "lst")


def _seasonal_cycle(doy: np.ndarray) -> np.ndarray:
    """Unitless seasonal wetness: peaks in Season B (Mar–May) and Season A (Oct–Dec)."""
    rad = 2 * np.pi * doy / 365.25
    # Two peaks: ~day 105 (mid-April) and ~day 305 (early November).
    return 0.55 + 0.28 * np.cos(rad - 2.0) + 0.22 * np.cos(2 * rad - 0.4)


def _drought_forcing(dates: pd.DatetimeIndex) -> np.ndarray:
    """Negative pulses during documented/plausible dry spells (2018–2024 window)."""
    f = np.zeros(len(dates))
    episodes = [
        ("2021-10-01", "2022-02-15", -1.35),
        ("2023-01-10", "2023-04-20", -1.05),
        ("2018-06-15", "2018-08-31", -0.55),  # mild mid-season dry
        ("2020-01-15", "2020-03-10", -0.70),
    ]
    for start, end, amp in episodes:
        m = (dates >= start) & (dates <= end)
        n = m.sum()
        if n == 0:
            continue
        # Smooth onset/decay
        window = np.hanning(max(n * 2 - 1, 3))[:n]
        window = window / window.max()
        f[m] += amp * window
    return f


def generate_cube(cfg: dict[str, Any]) -> dict[str, Any]:
    syn = cfg["synthetic"]
    rng = np.random.default_rng(syn["seed"])
    start = cfg["study"]["start_date"]
    end = cfg["study"]["end_date"]
    freq = cfg["study"]["temporal_resolution"]

    dates = pd.date_range(start, end, freq=freq)
    n_t = len(dates)
    n_lat = int(syn["n_lat"])
    n_lon = int(syn["n_lon"])
    lead = int(syn["typical_lead_composites"])

    lat = np.linspace(PROVINCE_BBOX["Southern"]["lat_min"], PROVINCE_BBOX["Eastern"]["lat_max"], n_lat)
    lon = np.linspace(PROVINCE_BBOX["Southern"]["lon_min"], PROVINCE_BBOX["Eastern"]["lon_max"], n_lon)

    doy = dates.dayofyear.to_numpy()
    seasonal = _seasonal_cycle(doy)
    drought = _drought_forcing(dates)

    east = province_mask(lat, lon, "Eastern")
    south = province_mask(lat, lon, "Southern")
    study = east | south
    # Eastern province is drier / more drought-prone
    aridity = np.where(east, 1.15, np.where(south, 0.85, 0.0))

    rain_base = 28.0  # mm per 16-day composite, scaled by season
    sm_base = 0.22
    ndvi_base = 0.48
    evi_base = 0.32
    lst_base = 301.0  # K

    rainfall = np.zeros((n_t, n_lat, n_lon))
    soil_moisture = np.zeros_like(rainfall)
    lst = np.zeros_like(rainfall)
    ndvi = np.zeros_like(rainfall)
    evi = np.zeros_like(rainfall)

    rain_anom = drought.copy()
    sm_anom = np.roll(drought, lead // 2) * 0.9  # SM lags rain slightly
    veg_anom = np.roll(drought, lead) * 0.85  # vegetation lags both

    for t in range(n_t):
        spatial_noise = rng.normal(0, 0.08, size=(n_lat, n_lon))
        wet = seasonal[t]
        r = rain_base * wet * (1 + 0.55 * rain_anom[t]) * (1.15 - 0.25 * aridity)
        r = r * (1 + spatial_noise)
        rainfall[t] = np.where(study, np.clip(r, 0, None), np.nan)

        sm = sm_base * (0.7 + 0.6 * wet) * (1 + 0.45 * sm_anom[t]) * (1.1 - 0.2 * aridity)
        sm = sm * (1 + 0.5 * spatial_noise)
        soil_moisture[t] = np.where(study, np.clip(sm, 0.05, 0.45), np.nan)

        # LST inverse to moisture
        lst_t = lst_base + 6.0 * (1 - wet) - 4.0 * sm_anom[t] + 1.5 * aridity
        lst[t] = np.where(study, lst_t + rng.normal(0, 0.4, size=(n_lat, n_lon)), np.nan)

        n = ndvi_base * (0.65 + 0.55 * wet) * (1 + 0.40 * veg_anom[t]) * (1.05 - 0.12 * aridity)
        n = n * (1 + 0.35 * spatial_noise)
        ndvi[t] = np.where(study, np.clip(n, 0.05, 0.92), np.nan)

        e = evi_base * (0.65 + 0.55 * wet) * (1 + 0.38 * veg_anom[t]) * (1.05 - 0.12 * aridity)
        e = e * (1 + 0.35 * spatial_noise)
        evi[t] = np.where(study, np.clip(e, 0.02, 0.80), np.nan)

    cube = {
        "time": dates,
        "lat": lat,
        "lon": lon,
        "mask": study.astype(bool),
        "province_masks": {"Eastern": east, "Southern": south},
        "ndvi": ndvi,
        "evi": evi,
        "rainfall": rainfall,
        "soil_moisture": soil_moisture,
        "lst": lst,
        "data_source": "synthetic",
        "variables": VARIABLES,
    }
    return cube


def cube_to_provincial_means(cube: dict[str, Any]) -> pd.DataFrame:
    """Spatial mean of each variable by province and time."""
    rows = []
    for prov, mask in cube["province_masks"].items():
        for t, ts in enumerate(cube["time"]):
            rec: dict[str, Any] = {"time": ts, "province": prov}
            for v in cube["variables"]:
                field = cube[v][t]
                rec[v] = float(np.nanmean(np.where(mask, field, np.nan)))
            rows.append(rec)
    df = pd.DataFrame(rows).sort_values(["province", "time"]).reset_index(drop=True)
    df["data_source"] = cube["data_source"]
    return df
