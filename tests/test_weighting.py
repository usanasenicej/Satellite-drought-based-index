import numpy as np
import pandas as pd
import pytest

from adewi.weighting import compute_entropy_weights, compute_pca_weights


def test_pca_and_entropy_weights():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "rf": np.random.normal(0, 1, n),
        "sm": np.random.normal(0, 1, n),
        "lst": np.random.normal(0, 1, n),
    })

    cols = ["rf", "sm", "lst"]
    pca_w = compute_pca_weights(df, cols)
    entropy_w = compute_entropy_weights(df, cols)

    assert set(pca_w.keys()) == set(cols)
    assert np.isclose(sum(pca_w.values()), 1.0)
    assert all(w >= 0 for w in pca_w.values())

    assert set(entropy_w.keys()) == set(cols)
    assert np.isclose(sum(entropy_w.values()), 1.0)
    assert all(w >= 0 for w in entropy_w.values())
