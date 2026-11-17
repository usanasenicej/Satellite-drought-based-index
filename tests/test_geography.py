import pytest

from adewi.geography import (
    RWANDA_DISTRICTS,
    generate_rwanda_geojson,
    get_districts_by_province,
    get_province_names,
)


def test_rwanda_geography():
    assert len(RWANDA_DISTRICTS) == 30

    provinces = get_province_names()
    assert set(provinces) == {"Eastern", "Southern", "Northern", "Western", "Kigali"}

    eastern = get_districts_by_province("Eastern")
    assert len(eastern) == 7
    eastern_names = {d.name for d in eastern}
    assert "Bugesera" in eastern_names
    assert "Nyagatare" in eastern_names

    southern = get_districts_by_province("Southern")
    assert len(southern) == 8
    southern_names = {d.name for d in southern}
    assert "Huye" in southern_names
    assert "Gisagara" in southern_names


def test_rwanda_geojson():
    geojson = generate_rwanda_geojson()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 30
    first_feat = geojson["features"][0]
    assert "geometry" in first_feat
    assert "properties" in first_feat
    assert "agro_zone" in first_feat["properties"]
