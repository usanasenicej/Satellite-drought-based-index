import pytest

from app.api import (
    SimulationRequest,
    get_geojson,
    get_province_status,
    health_check,
    list_districts,
    list_provinces,
    simulate_drought,
)


def test_api_functions():
    # Health check
    h = health_check()
    assert h["status"] == "ok"
    assert "version" in h

    # Provinces
    provinces = list_provinces()
    assert "Eastern" in provinces
    assert "Southern" in provinces

    # Districts
    districts = list_districts(province="Eastern")
    assert len(districts) == 7
    assert districts[0]["province"] == "Eastern"

    # GeoJSON
    geo = get_geojson()
    assert geo["type"] == "FeatureCollection"
    assert len(geo["features"]) == 30

    # Status
    status = get_province_status("Eastern")
    assert status["province"] == "Eastern"
    assert "adewi" in status

    # Simulation
    req = SimulationRequest(
        rainfall_anomaly_z=-1.8,
        soil_moisture_anomaly_z=-1.5,
        lst_anomaly_z=1.2,
        weight_rainfall=0.4,
        weight_soil_moisture=0.35,
        weight_lst=0.25,
    )
    res = simulate_drought(req)
    assert res.adewi_score < -1.5
    assert "Critical" in res.alert_level or "Emergency" in res.alert_level
