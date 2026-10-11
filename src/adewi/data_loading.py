"""Load satellite/climate data for Eastern and Southern Rwanda.

Priority:
1. Processed NetCDF / CSV already in data/processed (from GEE or DE Africa export)
2. Raw CSV exports in data/raw matching the expected columns
3. Synthetic cube (development / demonstration only)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .config import ensure_dirs
from .synthetic_data import cube_to_provincial_means, generate_cube

EXPECTED_COLUMNS = ["time", "province", "ndvi", "evi", "rainfall", "soil_moisture", "lst"]


def _read_csv_if_valid(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    df = pd.read_csv(path, parse_dates=["time"])
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing columns: {missing}")
    df["data_source"] = df.get("data_source", pd.Series(["observed"] * len(df)))
    return df.sort_values(["province", "time"]).reset_index(drop=True)


def load_provincial_timeseries(cfg: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any] | None]:
    """Return (dataframe, optional spatial cube). Cube is only present for synthetic/raster runs."""
    ensure_dirs(cfg)
    processed = Path(cfg["paths"]["data_processed"]) / "provincial_timeseries.csv"
    raw = Path(cfg["paths"]["data_raw"]) / "provincial_timeseries.csv"

    for candidate in (processed, raw):
        df = _read_csv_if_valid(candidate)
        if df is not None:
            return df, None

    if not cfg.get("synthetic", {}).get("enabled", True):
        raise FileNotFoundError(
            "No observed provincial_timeseries.csv found in data/raw or data/processed. "
            "Run scripts/gee_export_timeseries.py (or the DE Africa notebook) and save the CSV, "
            "or keep synthetic.enabled: true in config/config.yaml."
        )

    cube = generate_cube(cfg)
    df = cube_to_provincial_means(cube)
    out = Path(cfg["paths"]["data_processed"]) / "provincial_timeseries.csv"
    df.to_csv(out, index=False)
    return df, cube
