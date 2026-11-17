"""SpatioTemporal Asset Catalog (STAC) client for Earth Observation data.

Interfaces Planetary Computer and Earth Search STAC APIs to query:
- MODIS NDVI / EVI (MOD13Q1 / MYD13Q1)
- MODIS Land Surface Temperature (MOD11A2)
- Sentinel-2 L2A surface reflectance
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any
import urllib.request


PLANETARY_COMPUTER_STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
EARTH_SEARCH_STAC_URL = "https://earth-search.aws.element84.com/v1/search"

# Rwanda bounding box: [min_lon, min_lat, max_lon, max_lat]
RWANDA_BBOX = [28.86, -2.84, 30.90, -1.05]


@dataclass
class StacQuery:
    collections: list[str]
    bbox: list[float]
    datetime_range: str  # e.g. "2023-01-01T00:00:00Z/2023-03-31T23:59:59Z"
    limit: int = 20
    max_cloud_cover: float = 30.0

    def to_payload(self) -> dict[str, Any]:
        return {
            "collections": self.collections,
            "bbox": self.bbox,
            "datetime": self.datetime_range,
            "limit": self.limit,
            "query": {
                "eo:cloud_cover": {"lt": self.max_cloud_cover}
            } if self.max_cloud_cover < 100.0 else {},
        }


def build_modis_stac_query(
    start_date: str,
    end_date: str,
    product: str = "vegetation",  # "vegetation" or "temperature"
    bbox: list[float] | None = None,
) -> StacQuery:
    """Build STAC query for MODIS 16-day vegetation or 8-day temperature collections."""
    collection = "modis-13Q1-061" if product == "vegetation" else "modis-11A2-061"
    dt_str = f"{start_date}T00:00:00Z/{end_date}T23:59:59Z"
    return StacQuery(
        collections=[collection],
        bbox=bbox or RWANDA_BBOX,
        datetime_range=dt_str,
        max_cloud_cover=100.0,  # MODIS composite products already cloud-screened
    )


def build_sentinel2_stac_query(
    start_date: str,
    end_date: str,
    max_cloud_cover: float = 20.0,
    bbox: list[float] | None = None,
) -> StacQuery:
    """Build STAC query for Sentinel-2 L2A over Rwanda."""
    dt_str = f"{start_date}T00:00:00Z/{end_date}T23:59:59Z"
    return StacQuery(
        collections=["sentinel-2-l2a"],
        bbox=bbox or RWANDA_BBOX,
        datetime_range=dt_str,
        max_cloud_cover=max_cloud_cover,
    )
