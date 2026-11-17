import numpy as np
import pytest

from adewi.spatial import compute_zonal_statistics


def test_compute_zonal_statistics():
    lat = np.array([-2.5, -2.0, -1.5])
    lon = np.array([29.5, 30.0, 30.5])
    raster = np.array([
        [-1.5, -0.5, 0.2],
        [-2.0, -1.2, 0.8],
        [0.1, 0.5, 1.2],
    ])

    zones = {
        "SouthWest": (-2.6, -1.9, 29.4, 30.1),
        "NorthEast": (-1.6, -1.4, 30.4, 30.6),
    }

    df = compute_zonal_statistics(raster, lat, lon, zones, drought_threshold=-1.0)
    assert len(df) == 2
    sw = df[df["zone_name"] == "SouthWest"].iloc[0]
    assert sw["valid_pixels"] == 4
    assert sw["drought_area_fraction"] > 0
    ne = df[df["zone_name"] == "NorthEast"].iloc[0]
    assert ne["valid_pixels"] == 1
    assert ne["drought_area_fraction"] == 0.0
