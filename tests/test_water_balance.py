import numpy as np
import pandas as pd
import pytest

from adewi.water_balance import (
    compute_climatic_water_balance,
    compute_spei,
    estimate_pet_hargreaves,
    estimate_pet_thornthwaite,
)


def test_pet_estimations():
    tmean = pd.Series([20.0, 22.0, 24.0])
    tmin = pd.Series([15.0, 16.0, 17.0])
    tmax = pd.Series([25.0, 28.0, 31.0])

    pet_hg = estimate_pet_hargreaves(tmean, tmin, tmax)
    assert len(pet_hg) == 3
    assert (pet_hg > 0).all()

    pet_th = estimate_pet_thornthwaite(tmean)
    assert len(pet_th) == 3
    assert (pet_th > 0).all()


def test_water_balance_and_spei():
    p = pd.Series([100.0, 50.0, 10.0, 5.0, 0.0, 120.0, 80.0])
    pet = pd.Series([50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0])
    d = compute_climatic_water_balance(p, pet)
    assert d.iloc[0] == 50.0
    assert d.iloc[4] == -50.0

    spei = compute_spei(d, window=2)
    assert len(spei) == len(d)
    assert spei.min() < 0
    assert spei.max() > 0
