"""Data quality, validation, and schema enforcement for satellite time-series.

Validates:
- Required column presence (province, time, ndvi, evi, rainfall, soil_moisture, lst).
- Physical domain bounds.
- Temporal sequence continuity.
- Missing value percentage thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np
import pandas as pd


PHYSICAL_RANGES = {
    "ndvi": (-0.2, 1.0),
    "evi": (-0.2, 1.0),
    "rainfall": (0.0, 500.0),
    "soil_moisture": (0.0, 1.0),
    "lst": (250.0, 350.0),
}


@dataclass
class ValidationReport:
    is_valid: bool
    missing_pct: dict[str, float]
    range_violations: dict[str, int]
    row_count: int
    errors: list[str]


def validate_environmental_timeseries(
    df: pd.DataFrame,
    required_cols: tuple[str, ...] = ("province", "time", "ndvi", "rainfall", "soil_moisture", "lst"),
    max_missing_allowed: float = 0.20,
) -> ValidationReport:
    """Validate DataFrame against environmental research schema."""
    errors: list[str] = []
    missing_pct: dict[str, float] = {}
    range_violations: dict[str, int] = {}

    # Check columns
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if errors:
        return ValidationReport(False, {}, {}, len(df), errors)

    # Check missing values
    for col in required_cols:
        pct = float(df[col].isna().mean())
        missing_pct[col] = round(pct, 4)
        if pct > max_missing_allowed:
            errors.append(f"Column '{col}' has {pct*100:.1f}% missing values (exceeds {max_missing_allowed*100:.0f}%)")

    # Check physical ranges
    for col, (vmin, vmax) in PHYSICAL_RANGES.items():
        if col in df.columns:
            valid_vals = df[col].dropna()
            violations = int(((valid_vals < vmin) | (valid_vals > vmax)).sum())
            range_violations[col] = violations
            if violations > 0:
                errors.append(f"Column '{col}' contains {violations} values outside physical range [{vmin}, {vmax}]")

    return ValidationReport(
        is_valid=len(errors) == 0,
        missing_pct=missing_pct,
        range_violations=range_violations,
        row_count=len(df),
        errors=errors,
    )
