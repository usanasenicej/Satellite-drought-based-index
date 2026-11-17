"""Gridded spatial raster and zonal statistics engine for Rwanda.

Computes:
- Spatial masks for administrative polygons / bounding boxes.
- Zonal statistics across districts or provinces (mean, std, min, max, median).
- Drought area percentage (fraction of pixels exceeding threshold).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np
import pandas as pd


@dataclass
class ZonalStat:
    zone_name: str
    valid_pixels: int
    mean: float
    std: float
    median: float
    min: float
    max: float
    drought_area_fraction: float


def compute_zonal_statistics(
    raster: np.ndarray,
    lat_coords: np.ndarray,
    lon_coords: np.ndarray,
    zones: dict[str, tuple[float, float, float, float]],  # name -> (lat_min, lat_max, lon_min, lon_max)
    drought_threshold: float = -1.0,
) -> pd.DataFrame:
    """Compute zonal statistics across a 2D gridded raster for defined bounding zones."""
    results: list[dict] = []
    lon_grid, lat_grid = np.meshgrid(lon_coords, lat_coords)

    for zone_name, (lat_min, lat_max, lon_min, lon_max) in zones.items():
        mask = (
            (lat_grid >= lat_min)
            & (lat_grid <= lat_max)
            & (lon_grid >= lon_min)
            & (lon_grid <= lon_max)
        )
        sub_vals = raster[mask]
        valid_vals = sub_vals[np.isfinite(sub_vals)]

        if len(valid_vals) == 0:
            results.append(
                asdict(
                    ZonalStat(
                        zone_name=zone_name,
                        valid_pixels=0,
                        mean=np.nan,
                        std=np.nan,
                        median=np.nan,
                        min=np.nan,
                        max=np.nan,
                        drought_area_fraction=np.nan,
                    )
                )
            )
            continue

        drought_frac = float(np.mean(valid_vals <= drought_threshold))
        results.append(
            asdict(
                ZonalStat(
                    zone_name=zone_name,
                    valid_pixels=len(valid_vals),
                    mean=round(float(np.mean(valid_vals)), 4),
                    std=round(float(np.std(valid_vals, ddof=1)) if len(valid_vals) > 1 else 0.0, 4),
                    median=round(float(np.median(valid_vals)), 4),
                    min=round(float(np.min(valid_vals)), 4),
                    max=round(float(np.max(valid_vals)), 4),
                    drought_area_fraction=round(drought_frac, 4),
                )
            )
        )

    return pd.DataFrame(results)
