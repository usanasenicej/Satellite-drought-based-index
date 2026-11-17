import numpy as np
import pandas as pd
import pytest

from adewi.forecasting import forecast_autoregressive, forecast_exponential_smoothing


def test_forecast_autoregressive():
    np.random.seed(42)
    s = pd.Series(np.sin(np.linspace(0, 10, 50)) + np.random.normal(0, 0.1, 50))
    res = forecast_autoregressive(s, steps=3, lags=4)

    assert len(res.forecast) == 3
    assert len(res.lower_bound) == 3
    assert len(res.upper_bound) == 3
    assert (res.lower_bound <= res.forecast).all()
    assert (res.upper_bound >= res.forecast).all()


def test_forecast_exponential_smoothing():
    s = pd.Series([1.0, 1.2, 1.4, 1.6, 1.8, 2.0])
    res = forecast_exponential_smoothing(s, steps=2)
    assert len(res.forecast) == 2
    assert res.forecast.iloc[0] > 2.0
    assert (res.lower_bound <= res.forecast).all()
