import numpy as np
import pandas as pd
import pytest

from adewi.standardized_indices import classify_vhi, compute_tci, compute_vci, compute_vhi


def test_compute_vci_and_tci():
    df = pd.DataFrame({
        "region": ["Eastern"] * 5,
        "doy_bin": [1] * 5,
        "ndvi": [0.2, 0.4, 0.6, 0.8, 1.0],
        "lst": [300.0, 305.0, 310.0, 315.0, 320.0],
    })
    vci = compute_vci(df, ndvi_col="ndvi")
    tci = compute_tci(df, lst_col="lst")
    vhi = compute_vhi(vci, tci, alpha=0.5)

    assert len(vci) == 5
    assert np.isclose(vci.iloc[0], 0.0)
    assert np.isclose(vci.iloc[-1], 100.0)
    assert np.isclose(tci.iloc[0], 100.0)
    assert np.isclose(tci.iloc[-1], 0.0)
    assert np.isclose(vhi.iloc[2], 50.0)

    cats = classify_vhi(vhi)
    assert cats.iloc[0] == "No Drought"
    assert classify_vhi(5.0) == "Extreme Drought"
    assert classify_vhi(15.0) == "Severe Drought"
    assert classify_vhi(25.0) == "Moderate Drought"
    assert classify_vhi(35.0) == "Mild Drought"
