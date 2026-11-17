"""CHIRPS satellite precipitation data connector.

Interfaces UC Santa Barbara's Climate Hazards Center CHIRPS-2.0 repository.
Supports:
- Constructing pentad / monthly download URLs for Africa/Rwanda.
- Parsing pentad indices (1 to 6 per month).
- Downloading and caching raster tiles or provincial summaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import urllib.request


CHIRPS_BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_pentad/peta"


@dataclass
class ChirpsPentad:
    year: int
    month: int
    pentad: int
    url: str
    filename: str


def get_pentad_index(day_of_month: int) -> int:
    """Return pentad index (1 to 6) for a given calendar day."""
    if day_of_month <= 5:
        return 1
    if day_of_month <= 10:
        return 2
    if day_of_month <= 15:
        return 3
    if day_of_month <= 20:
        return 4
    if day_of_month <= 25:
        return 5
    return 6


def build_chirps_pentad_url(year: int, month: int, pentad: int) -> ChirpsPentad:
    """Construct standard download URL for CHIRPS Africa pentad dataset."""
    filename = f"chirps-v2.0.{year}.{month:02d}.{pentad}.tif.gz"
    url = f"{CHIRPS_BASE_URL}/{year}/{filename}"
    return ChirpsPentad(
        year=year,
        month=month,
        pentad=pentad,
        url=url,
        filename=filename,
    )


def list_pentads_for_range(start_date: str, end_date: str) -> list[ChirpsPentad]:
    """Generate list of expected CHIRPS pentads between start and end dates."""
    dt_start = datetime.strptime(start_date, "%Y-%m-%d")
    dt_end = datetime.strptime(end_date, "%Y-%m-%d")

    pentads: list[ChirpsPentad] = []
    seen: set[tuple[int, int, int]] = set()

    for cur_year in range(dt_start.year, dt_end.year + 1):
        m_start = dt_start.month if cur_year == dt_start.year else 1
        m_end = dt_end.month if cur_year == dt_end.year else 12
        for m in range(m_start, m_end + 1):
            for p in range(1, 7):
                key = (cur_year, m, p)
                if key not in seen:
                    seen.add(key)
                    pentads.append(build_chirps_pentad_url(cur_year, m, p))

    return pentads
