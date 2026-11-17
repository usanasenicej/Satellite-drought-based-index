import pytest

from adewi.connectors.chirps import build_chirps_pentad_url, get_pentad_index, list_pentads_for_range


def test_chirps_connector():
    assert get_pentad_index(3) == 1
    assert get_pentad_index(8) == 2
    assert get_pentad_index(14) == 3
    assert get_pentad_index(19) == 4
    assert get_pentad_index(24) == 5
    assert get_pentad_index(29) == 6

    p = build_chirps_pentad_url(2022, 5, 2)
    assert p.year == 2022
    assert p.month == 5
    assert p.pentad == 2
    assert "chirps-v2.0.2022.05.2.tif.gz" in p.url

    p_list = list_pentads_for_range("2023-01-01", "2023-02-28")
    assert len(p_list) == 12  # 6 pentads/month * 2 months
