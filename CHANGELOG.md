# Changelog

All notable changes to the ADEWI-Rwanda project are documented here.  
Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Interactive Geospatial Map** in Streamlit App (Tab 3): interactive district-level coordinate visualization displaying study districts and drought severity.
- **Functional District Explorer** in Streamlit App: provides district location details, coordinates, and province context.
- **Export & Download buttons** in Streamlit: one-click CSV downloads for filtered time-series data, detected drought events, and custom sensitivity scenarios.
- **Side-by-side sensitivity comparison chart**: interactive Plotly visualization contrasting baseline vs custom weight scenarios.
- **Data caching (`@st.cache_data`)**: optimized Streamlit app performance by caching pipeline data loading.
- **Console script entry point**: `adewi` command defined in `pyproject.toml` pointing to `adewi.run_pipeline:main`.
- **Optional dependency groups**: added `geo` and `dev` dependencies in `pyproject.toml`.
- **Enhanced configuration loading & validation**: relative path resolution for validation files (`crop_stats_file`), configuration validation, and LRU caching in `config.py`.
- **Comprehensive NumPy-style docstrings**: complete documentation across `config.py`, `anomalies.py`, `preprocessing.py`, `regions.py`, `synthetic_data.py`, and `run_pipeline.py`.
- **Quick Start section in README.md** with simple setup, running, and exploration commands.

### Changed
- Bumped project version to `0.2.0` across `pyproject.toml` and `src/adewi/__init__.py`.
- Cleaned and consolidated CHANGELOG sections.

---

## [0.3.0] — 2026-11-17

### Added
- **Standardized Remote-Sensing Drought Indices**: Added `adewi.standardized_indices` implementing Kogan's Vegetation Condition Index (VCI), Temperature Condition Index (TCI), and Vegetation Health Index (VHI).
- **SPEI & Climatic Water Balance**: Added `adewi.water_balance` computing Hargreaves/Thornthwaite potential evapotranspiration (PET) and multi-scalar SPEI.
- **Dynamic Weight Optimization**: Added `adewi.weighting` supporting Principal Component Analysis (PCA) and Shannon Entropy Weight Method (EWM).
- **Run-Theory Event Analytics**: Added `adewi.events` characterizing drought spells, duration, cumulative deficit, and peak intensity.
- **ENSO/IOD & Cloud Dropout Simulation**: Enhanced `adewi.synthetic_data` with inter-annual teleconnections and sensor cloud gap corruption.
- **Machine Learning Early-Warning Classifier**: Added `adewi.ml_early_warning` predicting drought onset 16-to-48 days in advance using RandomForest and GradientBoosting.
- **Time-Series Forecaster**: Added `adewi.forecasting` with autoregressive AR(p) and Holt linear exponential smoothing models.
- **Diagnostic ROC & Precision-Recall Suite**: Added `adewi.roc_evaluation` with ROC-AUC, Precision-Recall curves, and Youden's J statistic.
- **Lead-Time Dynamics & False Alarms**: Added `adewi.delay_metrics` calculating Mean Detection Delay (MDD) and False Discovery Rate (FDR).
- **Rwanda 30-District Geospatial Metadata**: Added `adewi.geography` with full provincial classifications, agro-ecological zones, and GeoJSON boundary generators.
- **Spatial Zonal Statistics**: Added `adewi.spatial` with gridded raster masking and drought area fraction quantification.
- **CHIRPS Satellite Connector & CLI**: Added `adewi.connectors.chirps` and `scripts/fetch_chirps.py` for downloading precipitation pentads.
- **STAC Earth Observation Client**: Added `adewi.connectors.stac` supporting Sentinel-2 and MODIS search queries.
- **FastAPI Real-Time Drought Alert REST API**: Added `app/api.py` with asynchronous endpoints for live metrics and simulations.
- **Multi-Command CLI**: Added `run`, `eval`, `forecast`, `serve`, and `info` subcommands to the `adewi` CLI.
- **Pipeline DAG Caching**: Added `adewi.caching` with SHA-256 fingerprinting to skip unchanged pipeline stages.
- **Schema & Data Integrity Validator**: Added `adewi.schema` enforcing strict physical ranges and missing value limits.
- **Structured Telemetry & Profiler**: Added `adewi.logger` providing JSON logs and execution timers.
- **Streamlit Early Warning Alerts & Gauges**: Added real-time provincial alert badges and risk status cards in `app/streamlit_app.py`.
- **Streamlit Agro-Ecological District Directory**: Enriched map explorer with 30-district agro-zones and vulnerability ratings.
- **Streamlit Climate Scenario Simulator**: Added interactive 'What-If' simulator tab with dynamic gauge visualizations.
- **Streamlit Research Data Package**: Added one-click bundle download for datasets, GeoJSON boundaries, and run reports.
- **Comprehensive Integration Test Suite**: Added end-to-end multi-module pipeline tests in `tests/test_integration_pipeline.py`.
- **Multi-Stage Docker & Compose Orchestration**: Added `Dockerfile` and `docker-compose.yml` for unified dashboard and API deployment.
- **GitHub Actions Multi-OS CI Workflow**: Added `.github/workflows/ci.yml` with Linux/Windows matrix testing.
- **Code Quality & Pre-Commit Standards**: Added `ruff.toml` and `.pre-commit-config.yaml`.
- **Automated LaTeX & Markdown Reports**: Added `adewi.reports` generating booktabs tables and executive briefs.
- **BibTeX Bibliography Database**: Added `paper/references.bib` with citations for remote sensing literature.
- **Academic Manuscript Overhaul**: Updated `paper/manuscript_draft.md` with methodology, ML benchmarks, and citations.
- **System Architecture Guide**: Added `docs/architecture.md` with comprehensive mermaid architecture diagrams.

### Changed
- Bumped version to `0.3.0` across `pyproject.toml` and `src/adewi/__init__.py`.

---

## [0.2.0] — 2026-10-29

### Added
- `lead_time.false_alarm_rate()` — counts ADEWI events with no matching NDVI response
- `lead_time.lead_time_by_season()` — stratifies lead times by Rwanda Season A/B/C
- `validation.evi_correlation()` — quantifies EVI–NDVI agreement to justify EVI in CADI
- `combined_index.compute_cadi_paper()` — convenience function using exact brief weights
- `combined_index.evi_class` column in index output
- `visualization.fig_evi_ndvi_comparison()` — Figure 09
- `visualization.fig_province_comparison()` — Figure 10
- `visualization.fig_cadi_vs_adewi()` — Figure 11
- `visualization.FIGURE_METADATA` dict with figure numbers and captions for paper
- `export.write_tables()` — new optional parameters: seasonal_lead, false_alarms, evi_corr, sensitivity
- New Excel sheets: seasonal_lead, false_alarms, evi_ndvi_corr, sensitivity
- `table_seasonal_lead_time.csv`, `table_false_alarms.csv`, `table_evi_ndvi_correlation.csv`
- `paper/manuscript_template.md` — full RJAS-style manuscript template (Sections 1–6 + Supplementary)
- `run_pipeline.py` includes false_alarm_rate and seasonal_lead in JSON run report
- Streamlit app: 5-tab layout (Time Series, Lead-Time Analysis, Drought Map, Sensitivity, About)
- Streamlit app: district filter, CADI / EVI / rainfall series selector, live sensitivity scenario runner
- Streamlit app: annual drought fraction bar chart, drought class strip heatmap
- Streamlit app: custom CSS sidebar styling
- `config/config.yaml`: two additional validation periods (2020 short dry spell, 2018 mid-season dry)
- `config/config.yaml`: `crop_types` field (maize, beans) for documentation
- `validation.default_crop_placeholder()` now includes schematic bean production data
- `tests/test_anomalies.py` — unit tests for climatology and Z-score computation
- `tests/test_combined_index.py` — unit tests for ADEWI/CADI index construction and drought classification
- `tests/test_preprocessing.py` — unit tests for gap interpolation, physical clipping, and calendar attachment
- `tests/test_validation.py` — unit tests for known-period hit-rate and crop-correlation helpers
- `tests/conftest.py` — shared pytest fixtures (minimal synthetic DataFrame)
- `scripts/sensitivity_analysis.py` — equal-weight and leave-one-out sensitivity tests for ADEWI
- `LICENSE` — MIT licence for open reproducibility
- `CHANGELOG.md` — this file
- `CONTRIBUTING.md` — contributor guide

### Changed
- **Drought classification thresholds** corrected to match research brief exactly:
  `Normal ≥ −0.5`, `Mild −0.5→−1.0`, `Moderate −1.0→−1.5`, `Severe −1.5→−2.0`, `Extreme < −2.0`
  (previously `Watch/Mild/Moderate/Severe` at −0.5/−1.0/−1.5/−2.0 — labels were shifted one step)
- **CADI weights** updated to match research brief formula:
  `ndvi: 0.30, evi: 0.15, rainfall: 0.30, soil_moisture: 0.20, lst: 0.20`
  (previously `ndvi: 0.20, evi: 0.15, rainfall: 0.25, soil_moisture: 0.25, lst: 0.15`)
- `combined_index.classify_drought()` docstring and logic aligned with new thresholds
- `gee_export_code_editor.js` expanded with inline step comments, MOD13A2 alternative,
  ESA CCI soil moisture documented alternative, and post-download checklist
- Visualization figures use `constrained_layout`, `fill_between`, `bar_label`, and accessible palettes
- `README.md` notebook listing updated from partial list to complete table

---

## [0.1.0] — 2026-10-13

### Added
- Full end-to-end pipeline (`python -m adewi`) producing all figures and tables
- Synthetic data cube for demonstration without GEE credentials
- ADEWI formula: `0.40·Z_rain + 0.35·Z_SM − 0.25·Z_LST`
- CADI status index including NDVI and EVI
- Lead-time detection (backward search up to 12 composites ≈ 6 months)
- Publication figures 1–9 in `results/figures/`
- CSV/Excel result tables in `results/tables/`
- Streamlit prototype (`streamlit run app/streamlit_app.py`)
- GEE JavaScript and Python export scripts
- Digital Earth Africa sandbox extract script
- Five analysis notebooks (`01`–`05`)
- `config/config.yaml` for tunable weights and thresholds
- `paper/manuscript_draft.md` template for RJAS submission
- Single unit test (`tests/test_lead_time.py`)
