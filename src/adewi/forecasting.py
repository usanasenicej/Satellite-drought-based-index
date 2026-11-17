"""Time-series anomaly forecasting for drought indices.

Implements:
1. Autoregressive AR(p) forecaster with ridge regularization.
2. Double exponential smoothing (Holt's linear trend).
3. Forecast confidence bounds (95% standard prediction interval).
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class ForecastResult:
    historical: pd.Series
    forecast: pd.Series
    lower_bound: pd.Series
    upper_bound: pd.Series


def forecast_autoregressive(
    series: pd.Series,
    steps: int = 3,
    lags: int = 4,
    alpha: float = 0.05,
) -> ForecastResult:
    """Forecast future composite values using an AR(p) model with Ridge regression."""
    y = series.dropna().values
    n = len(y)
    if n <= lags + 2:
        # Fallback to naive persistence
        last_val = y[-1] if n > 0 else 0.0
        fc = pd.Series([last_val] * steps)
        return ForecastResult(series, fc, fc - 0.5, fc + 0.5)

    # Build lag design matrix
    X_mat = np.zeros((n - lags, lags))
    y_vec = y[lags:]
    for i in range(lags):
        X_mat[:, i] = y[lags - 1 - i : n - 1 - i]

    # Add bias term
    X_design = np.hstack([np.ones((len(X_mat), 1)), X_mat])

    # Ridge solution: w = (X^T X + lambda I)^(-1) X^T y
    ridge_lambda = 0.01
    reg_matrix = ridge_lambda * np.eye(X_design.shape[1])
    reg_matrix[0, 0] = 0.0  # Do not regularize intercept
    weights = np.linalg.solve(X_design.T @ X_design + reg_matrix, X_design.T @ y_vec)

    # In-sample residuals std for confidence interval
    residuals = y_vec - X_design @ weights
    sigma = np.std(residuals, ddof=1) if len(residuals) > 1 else 0.2

    # Iterative forward forecasting
    history_window = list(y[-lags:])
    forecasts = []
    lowers = []
    uppers = []

    for step_i in range(1, steps + 1):
        x_in = np.array([1.0] + history_window[::-1][:lags])
        y_hat = float(x_in @ weights)
        forecasts.append(y_hat)
        # Margin grows with sqrt(step)
        margin = 1.96 * sigma * np.sqrt(step_i)
        lowers.append(y_hat - margin)
        uppers.append(y_hat + margin)
        history_window.append(y_hat)

    idx = pd.RangeIndex(start=len(series), stop=len(series) + steps)
    return ForecastResult(
        historical=series,
        forecast=pd.Series(forecasts, index=idx),
        lower_bound=pd.Series(lowers, index=idx),
        upper_bound=pd.Series(uppers, index=idx),
    )


def forecast_exponential_smoothing(
    series: pd.Series,
    steps: int = 3,
    alpha: float = 0.3,
    beta: float = 0.1,
) -> ForecastResult:
    """Holt's linear exponential smoothing forecast."""
    y = series.dropna().values
    if len(y) < 2:
        last_val = y[-1] if len(y) > 0 else 0.0
        fc = pd.Series([last_val] * steps)
        return ForecastResult(series, fc, fc - 0.5, fc + 0.5)

    level = y[0]
    trend = y[1] - y[0]

    for val in y[1:]:
        last_level = level
        level = alpha * val + (1.0 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1.0 - beta) * trend

    forecasts = [level + (m * trend) for m in range(1, steps + 1)]
    sigma = float(np.std(y)) if len(y) > 1 else 0.2

    idx = pd.RangeIndex(start=len(series), stop=len(series) + steps)
    fc_series = pd.Series(forecasts, index=idx)
    return ForecastResult(
        historical=series,
        forecast=fc_series,
        lower_bound=fc_series - 1.96 * sigma,
        upper_bound=fc_series + 1.96 * sigma,
    )
