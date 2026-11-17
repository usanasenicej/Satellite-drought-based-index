"""Climatic water balance and SPEI (Standardized Precipitation Evapotranspiration Index).

Calculates:
- Potential Evapotranspiration (PET) via Hargreaves and Thornthwaite approximations.
- Climatic Water Balance (D = Precipitation - PET).
- Multi-scalar Standardized Precipitation Evapotranspiration Index (SPEI).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def estimate_pet_hargreaves(
    tmean_c: pd.Series | np.ndarray,
    tmin_c: pd.Series | np.ndarray,
    tmax_c: pd.Series | np.ndarray,
    ra_mj_m2_day: float = 35.0,
) -> pd.Series:
    """Estimate Potential Evapotranspiration (PET in mm/day) using Hargreaves method.

    PET = 0.0023 * (Tmean + 17.8) * sqrt(Tmax - Tmin) * Ra * 0.408
    where Ra * 0.408 converts extraterrestrial radiation in MJ/m2/day to mm/day equivalent.
    """
    trange = np.maximum(0.0, np.asarray(tmax_c) - np.asarray(tmin_c))
    tmean = np.asarray(tmean_c)
    pet = 0.0023 * (tmean + 17.8) * np.sqrt(trange) * (ra_mj_m2_day * 0.408)
    return pd.Series(np.maximum(0.0, pet))


def estimate_pet_thornthwaite(
    tmean_c: pd.Series | np.ndarray,
    lat_deg: float = -2.0,  # Rwanda is ~2 degrees South
) -> pd.Series:
    """Estimate daily/composite PET (mm/day) using Thornthwaite approximation.

    Calibrated for equatorial tropical Rwanda with daylight length ~ 12 hours.
    """
    t = np.maximum(0.0, np.asarray(tmean_c))
    # Standard monthly heat index I = sum((T/5)^1.514)
    # For tropical Rwanda, T ~ 20-22 deg C, giving I ~ 95
    i_heat = 95.0
    a = (6.75e-7 * i_heat**3) - (7.71e-5 * i_heat**2) + (1.792e-2 * i_heat) + 0.49239
    # Monthly PET in cm, converted to mm/day (divided by 30)
    pet_month_cm = 1.6 * (10.0 * t / i_heat) ** a
    pet_mm_day = (pet_month_cm * 10.0) / 30.0
    return pd.Series(np.maximum(0.0, pet_mm_day))


def compute_climatic_water_balance(
    precipitation_mm: pd.Series,
    pet_mm: pd.Series,
) -> pd.Series:
    """Compute climatic water deficit or surplus: D = P - PET."""
    return precipitation_mm - pet_mm


def compute_spei(
    water_balance: pd.Series,
    window: int = 1,
) -> pd.Series:
    """Compute empirical Standardized Precipitation-Evapotranspiration Index (SPEI).

    Computes standardized z-score of rolling accumulated water balance D.
    """
    rolling_d = water_balance.rolling(window=window, min_periods=1).mean()
    mean_val = rolling_d.mean()
    std_val = rolling_d.std(ddof=1)
    if std_val == 0 or np.isnan(std_val):
        return pd.Series(0.0, index=water_balance.index)
    z = (rolling_d - mean_val) / std_val
    return z.clip(lower=-3.5, upper=3.5)
