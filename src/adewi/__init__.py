"""Satellite-based Agricultural Drought Early-Warning Index (ADEWI) for Rwanda."""

from __future__ import annotations

from .anomalies import compute_anomalies
from .combined_index import compute_cadi_paper, compute_indices
from .config import ensure_dirs, load_config
from .lead_time import analyze_lead_time, detect_events, match_lead_times
from .preprocessing import preprocess
from .run_pipeline import run

__version__ = "0.2.0"
__study__ = "Eastern and Southern Provinces of Rwanda, 2018–2024"

__all__ = [
    "load_config",
    "ensure_dirs",
    "preprocess",
    "compute_anomalies",
    "compute_indices",
    "compute_cadi_paper",
    "detect_events",
    "match_lead_times",
    "analyze_lead_time",
    "run",
]
