import pytest

from adewi.connectors.stac import RWANDA_BBOX, build_modis_stac_query, build_sentinel2_stac_query


def test_stac_query_builders():
    q_modis = build_modis_stac_query("2022-01-01", "2022-03-31", product="vegetation")
    assert q_modis.collections == ["modis-13Q1-061"]
    assert q_modis.bbox == RWANDA_BBOX
    assert "2022-01-01" in q_modis.datetime_range
    payload = q_modis.to_payload()
    assert payload["collections"] == ["modis-13Q1-061"]

    q_lst = build_modis_stac_query("2022-01-01", "2022-03-31", product="temperature")
    assert q_lst.collections == ["modis-11A2-061"]

    q_s2 = build_sentinel2_stac_query("2023-05-01", "2023-05-31", max_cloud_cover=15.0)
    assert q_s2.collections == ["sentinel-2-l2a"]
    p_s2 = q_s2.to_payload()
    assert p_s2["query"]["eo:cloud_cover"]["lt"] == 15.0
