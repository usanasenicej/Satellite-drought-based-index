"""Rwanda administrative geography, district metadata, and GeoJSON utilities.

Comprehensive geospatial reference for Rwanda's 5 provinces and 30 districts,
including agro-ecological zones and bounding coordinates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DistrictInfo:
    name: str
    province: str
    capital: str
    lat: float
    lon: float
    agro_zone: str
    drought_vulnerability: str  # High, Moderate, Low


RWANDA_DISTRICTS: dict[str, DistrictInfo] = {
    # Eastern Province (7 districts) - High drought vulnerability
    "Bugesera": DistrictInfo("Bugesera", "Eastern", "Nyamata", -2.15, 30.08, "Bugesera Depression", "High"),
    "Gatsibo": DistrictInfo("Gatsibo", "Eastern", "Kabarore", -1.60, 30.45, "Eastern Savanna", "High"),
    "Kayonza": DistrictInfo("Kayonza", "Eastern", "Mukarange", -1.90, 30.55, "Eastern Savanna", "High"),
    "Kirehe": DistrictInfo("Kirehe", "Eastern", "Nyakarambi", -2.25, 30.65, "Eastern Savanna", "High"),
    "Ngoma": DistrictInfo("Ngoma", "Eastern", "Kibungo", -2.18, 30.48, "Eastern Plateau", "Moderate"),
    "Nyagatare": DistrictInfo("Nyagatare", "Eastern", "Nyagatare", -1.30, 30.32, "Eastern Savanna", "High"),
    "Rwamagana": DistrictInfo("Rwamagana", "Eastern", "Kigabiro", -1.95, 30.43, "Eastern Plateau", "Moderate"),
    # Southern Province (8 districts)
    "Gisagara": DistrictInfo("Gisagara", "Southern", "Ndora", -2.62, 29.85, "Mayaga & Peripheral Bugesera", "High"),
    "Huye": DistrictInfo("Huye", "Southern", "Butare", -2.60, 29.74, "Central Plateau", "Moderate"),
    "Kamonyi": DistrictInfo("Kamonyi", "Southern", "Gacurabwenge", -2.00, 29.90, "Central Plateau", "Moderate"),
    "Muhanga": DistrictInfo("Muhanga", "Southern", "Gitarama", -2.08, 29.75, "Central Plateau", "Moderate"),
    "Nyamagabe": DistrictInfo("Nyamagabe", "Southern", "Gasaka", -2.48, 29.50, "Congo-Nile Divide", "Low"),
    "Nyanza": DistrictInfo("Nyanza", "Southern", "Nyanza", -2.35, 29.75, "Mayaga & Central Plateau", "High"),
    "Nyaruguru": DistrictInfo("Nyaruguru", "Southern", "Kibeho", -2.72, 29.53, "Congo-Nile Divide", "Low"),
    "Ruhango": DistrictInfo("Ruhango", "Southern", "Ruhango", -2.22, 29.78, "Mayaga & Central Plateau", "Moderate"),
    # Kigali City (3 districts)
    "Gasabo": DistrictInfo("Gasabo", "Kigali", "Kacyiru", -1.90, 30.12, "Central Plateau", "Moderate"),
    "Kicukiro": DistrictInfo("Kicukiro", "Kigali", "Kicukiro", -1.98, 30.10, "Central Plateau", "Moderate"),
    "Nyarugenge": DistrictInfo("Nyarugenge", "Kigali", "Nyarugenge", -1.95, 30.05, "Central Plateau", "Moderate"),
    # Northern Province (5 districts)
    "Burera": DistrictInfo("Burera", "Northern", "Cyeru", -1.45, 29.85, "Buberuka Highlands", "Low"),
    "Gakenke": DistrictInfo("Gakenke", "Northern", "Gakenke", -1.70, 29.78, "Buberuka Highlands", "Low"),
    "Gicumbi": DistrictInfo("Gicumbi", "Northern", "Byumba", -1.58, 30.07, "Buberuka Highlands", "Low"),
    "Musanze": DistrictInfo("Musanze", "Northern", "Muhoza", -1.50, 29.63, "Volcanic Range", "Low"),
    "Rulindo": DistrictInfo("Rulindo", "Northern", "Tare", -1.73, 30.00, "Central Plateau", "Low"),
    # Western Province (7 districts)
    "Karongi": DistrictInfo("Karongi", "Western", "Rubengera", -2.15, 29.35, "Lake Kivu Shore", "Low"),
    "Ngororero": DistrictInfo("Ngororero", "Western", "Ngororero", -1.87, 29.62, "Congo-Nile Divide", "Low"),
    "Nyabihu": DistrictInfo("Nyabihu", "Western", "Mukamira", -1.65, 29.50, "Congo-Nile Divide", "Low"),
    "Nyamasheke": DistrictInfo("Nyamasheke", "Western", "Nyamasheke", -2.37, 29.15, "Lake Kivu Shore", "Low"),
    "Rubavu": DistrictInfo("Rubavu", "Western", "Gisenyi", -1.68, 29.27, "Lake Kivu Shore", "Low"),
    "Rusizi": DistrictInfo("Rusizi", "Western", "Kamembe", -2.48, 28.90, "Imbo Lowlands", "Low"),
    "Rutsiro": DistrictInfo("Rutsiro", "Western", "Gihango", -1.95, 29.32, "Congo-Nile Divide", "Low"),
}


def get_districts_by_province(province: str) -> list[DistrictInfo]:
    """Return all districts belonging to a given province."""
    return [d for d in RWANDA_DISTRICTS.values() if d.province.lower() == province.lower()]


def get_province_names() -> list[str]:
    """Return sorted unique province names."""
    return sorted(list({d.province for d in RWANDA_DISTRICTS.values()}))


def generate_rwanda_geojson() -> dict[str, Any]:
    """Generate a lightweight GeoJSON FeatureCollection containing all 30 districts."""
    features = []
    for d in RWANDA_DISTRICTS.values():
        # Generate bounding square around centroid for rendering
        delta = 0.08
        coords = [
            [
                [round(d.lon - delta, 4), round(d.lat - delta, 4)],
                [round(d.lon + delta, 4), round(d.lat - delta, 4)],
                [round(d.lon + delta, 4), round(d.lat + delta, 4)],
                [round(d.lon - delta, 4), round(d.lat + delta, 4)],
                [round(d.lon - delta, 4), round(d.lat - delta, 4)],
            ]
        ]
        feat = {
            "type": "Feature",
            "id": d.name,
            "properties": {
                "name": d.name,
                "province": d.province,
                "capital": d.capital,
                "agro_zone": d.agro_zone,
                "drought_vulnerability": d.drought_vulnerability,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": coords,
            },
        }
        features.append(feat)

    return {
        "type": "FeatureCollection",
        "features": features,
    }
