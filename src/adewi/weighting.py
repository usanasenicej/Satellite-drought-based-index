"""Data-driven dynamic weight calculation methods for combined drought indices.

Implements:
1. Principal Component Analysis (PCA) weighting based on PC1 component loading.
2. Shannon Entropy Weight Method (EWM) for objective weight assignment.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_pca_weights(df: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    """Compute objective weights using Principal Component Analysis (PCA).

    Uses the first principal component (eigenvector corresponding to maximum eigenvalue)
    of the correlation matrix.
    """
    valid_df = df[columns].dropna()
    if len(valid_df) < len(columns):
        # Fallback to equal weights
        return {col: 1.0 / len(columns) for col in columns}

    # Standardize data
    x = valid_df.values
    x_std = (x - np.mean(x, axis=0)) / (np.std(x, axis=0, ddof=1) + 1e-8)

    # Covariance/correlation matrix
    cov_matrix = np.cov(x_std, rowvar=False)

    # Eigen decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    # Largest eigenvalue index
    idx = np.argmax(eigenvalues)
    pc1 = np.abs(eigenvectors[:, idx])

    weights = pc1 / np.sum(pc1)
    return {col: float(w) for col, w in zip(columns, weights)}


def compute_entropy_weights(df: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    """Compute objective weights using the Shannon Entropy Weight Method (EWM).

    Measures information content and dispersion of each indicator.
    """
    valid_df = df[columns].dropna()
    n = len(valid_df)
    if n < len(columns):
        return {col: 1.0 / len(columns) for col in columns}

    # Normalize to [0, 1] range
    x = valid_df.values
    min_vals = np.min(x, axis=0)
    max_vals = np.max(x, axis=0)
    rng = max_vals - min_vals
    rng[rng == 0] = 1e-8

    p_ij = (x - min_vals) / rng
    # Add tiny epsilon to avoid log(0)
    p_norm = p_ij / (np.sum(p_ij, axis=0, keepdims=True) + 1e-12)
    p_norm = np.clip(p_norm, 1e-12, 1.0)

    # Shannon Entropy: e_j = -1/ln(n) * sum(p_ij * ln(p_ij))
    k = 1.0 / np.log(n)
    entropy = -k * np.sum(p_norm * np.log(p_norm), axis=0)

    # Diversity/information utility: d_j = 1 - e_j
    d = 1.0 - entropy
    d = np.maximum(0.0, d)
    if np.sum(d) == 0:
        return {col: 1.0 / len(columns) for col in columns}

    weights = d / np.sum(d)
    return {col: float(w) for col, w in zip(columns, weights)}
