"""Satellite-based Agricultural Drought Early-Warning Index (ADEWI) for Rwanda."""

from __future__ import annotations

from .anomalies import compute_anomalies
from .caching import CacheManager
from .combined_index import compute_cadi_paper, compute_indices
from .config import ensure_dirs, load_config
from .delay_metrics import analyze_detection_dynamics
from .events import extract_drought_events
from .forecasting import forecast_autoregressive, forecast_exponential_smoothing
from .geography import RWANDA_DISTRICTS, generate_rwanda_geojson, get_districts_by_province, get_province_names
from .lead_time import analyze_lead_time, detect_events, match_lead_times
from .logger import get_pipeline_logger, log_execution_time
from .ml_early_warning import prepare_ml_dataset, train_drought_classifier
from .preprocessing import preprocess
from .reports import generate_executive_summary_markdown, generate_latex_table
from .roc_evaluation import evaluate_detection_performance
from .run_pipeline import run
from .schema import validate_environmental_timeseries
from .spatial import compute_zonal_statistics
from .standardized_indices import classify_vhi, compute_tci, compute_vci, compute_vhi
from .water_balance import compute_climatic_water_balance, compute_spei, estimate_pet_hargreaves, estimate_pet_thornthwaite
from .weighting import compute_entropy_weights, compute_pca_weights

__version__ = "0.3.0"
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
    "compute_vci",
    "compute_tci",
    "compute_vhi",
    "classify_vhi",
    "estimate_pet_hargreaves",
    "estimate_pet_thornthwaite",
    "compute_climatic_water_balance",
    "compute_spei",
    "compute_pca_weights",
    "compute_entropy_weights",
    "extract_drought_events",
    "train_drought_classifier",
    "prepare_ml_dataset",
    "forecast_autoregressive",
    "forecast_exponential_smoothing",
    "evaluate_detection_performance",
    "analyze_detection_dynamics",
    "RWANDA_DISTRICTS",
    "get_districts_by_province",
    "get_province_names",
    "generate_rwanda_geojson",
    "compute_zonal_statistics",
    "CacheManager",
    "validate_environmental_timeseries",
    "get_pipeline_logger",
    "log_execution_time",
    "generate_latex_table",
    "generate_executive_summary_markdown",
]
