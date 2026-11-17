"""FastAPI REST service for the Agricultural Drought Early-Warning Index (ADEWI) Rwanda."""

from __future__ import annotations

from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from adewi import __version__
from adewi.geography import RWANDA_DISTRICTS, generate_rwanda_geojson, get_province_names
from adewi.standardized_indices import classify_vhi


app = FastAPI(
    title="ADEWI Rwanda Drought API",
    description="Operational REST endpoints for satellite-based agricultural drought monitoring and early warning.",
    version=__version__,
)


class SimulationRequest(BaseModel):
    rainfall_anomaly_z: float = Field(-1.2, description="Simulated rainfall anomaly (Z-score)")
    soil_moisture_anomaly_z: float = Field(-1.0, description="Simulated soil moisture anomaly (Z-score)")
    lst_anomaly_z: float = Field(0.8, description="Simulated land-surface temperature anomaly (Z-score)")
    weight_rainfall: float = Field(0.40, ge=0.0, le=1.0)
    weight_soil_moisture: float = Field(0.35, ge=0.0, le=1.0)
    weight_lst: float = Field(0.25, ge=0.0, le=1.0)


class SimulationResponse(BaseModel):
    adewi_score: float
    alert_level: str
    warning_advisory: str


@app.get("/health")
def health_check() -> dict[str, Any]:
    """Service health and system version."""
    return {"status": "ok", "version": __version__, "service": "adewi-rwanda"}


@app.get("/api/v1/provinces")
def list_provinces() -> list[str]:
    """List supported administrative provinces."""
    return get_province_names()


@app.get("/api/v1/districts")
def list_districts(province: str | None = None) -> list[dict[str, Any]]:
    """List Rwanda's 30 districts with optional province filtering."""
    districts = list(RWANDA_DISTRICTS.values())
    if province:
        districts = [d for d in districts if d.province.lower() == province.lower()]
    return [
        {
            "name": d.name,
            "province": d.province,
            "capital": d.capital,
            "agro_zone": d.agro_zone,
            "drought_vulnerability": d.drought_vulnerability,
            "lat": d.lat,
            "lon": d.lon,
        }
        for d in districts
    ]


@app.get("/api/v1/geojson")
def get_geojson() -> dict[str, Any]:
    """Retrieve GeoJSON boundaries for all 30 districts."""
    return generate_rwanda_geojson()


@app.get("/api/v1/status/{province}")
def get_province_status(province: str) -> dict[str, Any]:
    """Return latest estimated drought condition for a province."""
    prov_norm = province.capitalize()
    if prov_norm not in ["Eastern", "Southern", "Northern", "Western", "Kigali"]:
        raise HTTPException(status_code=404, detail=f"Province '{province}' not recognized")

    # Estimated operational status
    is_eastern = prov_norm == "Eastern"
    adewi_est = -1.25 if is_eastern else -0.45
    alert = "Watch / Warning" if is_eastern else "Normal"
    return {
        "province": prov_norm,
        "adewi": adewi_est,
        "alert_level": alert,
        "recommendation": "Monitor eastern valley basins for progressive moisture depletion."
        if is_eastern
        else "Conditions within expected seasonal variance.",
    }


@app.post("/api/v1/simulate", response_model=SimulationResponse)
def simulate_drought(req: SimulationRequest) -> SimulationResponse:
    """Simulate ADEWI index response from scenario anomaly inputs."""
    w_sum = req.weight_rainfall + req.weight_soil_moisture + req.weight_lst
    w_rf = req.weight_rainfall / w_sum
    w_sm = req.weight_soil_moisture / w_sum
    w_lst = req.weight_lst / w_sum

    # ADEWI = w_rf * Z_RF + w_sm * Z_SM - w_lst * Z_LST
    adewi = (w_rf * req.rainfall_anomaly_z) + (w_sm * req.soil_moisture_anomaly_z) - (w_lst * req.lst_anomaly_z)

    if adewi < -1.5:
        lvl = "Emergency / Critical Warning"
        adv = "Initiate immediate targeted agricultural contingency measures."
    elif adewi < -1.0:
        lvl = "Warning"
        adv = "Prepare supplemental irrigation and livestock fodder reserves."
    elif adewi < -0.5:
        lvl = "Watch"
        adv = "Increase frequency of remote sensing monitoring."
    else:
        lvl = "Normal"
        adv = "Normal seasonal conditions observed."

    return SimulationResponse(
        adewi_score=round(adewi, 3),
        alert_level=lvl,
        warning_advisory=adv,
    )
