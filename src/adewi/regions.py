"""Study-area geometry (approximate bounding boxes for Eastern and Southern Rwanda).

When real GeoJSON from HDX / geoBoundaries is placed in data/raw, load_boundaries()
will use it. Until then, published bounding boxes are used for masking synthetic grids.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Approximate bounding boxes (WGS84) for provincial masking of coarse grids.
PROVINCE_BBOX = {
    "Eastern": {"lon_min": 30.05, "lon_max": 30.90, "lat_min": -2.35, "lat_max": -1.05},
    "Southern": {"lon_min": 29.35, "lon_max": 30.15, "lat_min": -2.85, "lat_max": -1.75},
}

RWANDA_BBOX = {"lon_min": 28.85, "lon_max": 30.90, "lat_min": -2.85, "lat_max": -1.05}

# Representative districts used for maps / Streamlit filters.
DISTRICTS = {
    "Eastern": ["Bugesera", "Gatsibo", "Kayonza", "Kirehe", "Ngoma", "Nyagatare", "Rwamagana"],
    "Southern": ["Gisagara", "Huye", "Kamonyi", "Muhanga", "Nyamagabe", "Nyanza", "Nyaruguru", "Ruhango"],
}

DISTRICT_CENTROIDS = {
    "Nyagatare": (-1.30, 30.33),
    "Gatsibo": (-1.58, 30.45),
    "Kayonza": (-1.93, 30.62),
    "Kirehe": (-2.25, 30.65),
    "Ngoma": (-2.17, 30.50),
    "Rwamagana": (-1.95, 30.43),
    "Bugesera": (-2.20, 30.15),
    "Kamonyi": (-2.00, 29.90),
    "Muhanga": (-2.08, 29.75),
    "Ruhango": (-2.20, 29.78),
    "Nyanza": (-2.35, 29.75),
    "Huye": (-2.60, 29.74),
    "Gisagara": (-2.62, 29.85),
    "Nyamagabe": (-2.48, 29.47),
    "Nyaruguru": (-2.70, 29.52),
}


def province_mask(lats: np.ndarray, lons: np.ndarray, province: str) -> np.ndarray:
    """Boolean mask of shape (n_lat, n_lon) for a province bbox."""
    box = PROVINCE_BBOX[province]
    lat2d, lon2d = np.meshgrid(lats, lons, indexing="ij")
    return (
        (lon2d >= box["lon_min"])
        & (lon2d <= box["lon_max"])
        & (lat2d >= box["lat_min"])
        & (lat2d <= box["lat_max"])
    )


def load_district_table(cfg: dict[str, Any] | None = None) -> pd.DataFrame:
    rows = []
    for prov, districts in DISTRICTS.items():
        for d in districts:
            lat, lon = DISTRICT_CENTROIDS[d]
            rows.append({"province": prov, "district": d, "lat": lat, "lon": lon})
    return pd.DataFrame(rows)


def try_load_geojson(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        import json

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return None
