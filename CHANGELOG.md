# Changelog

All notable changes to the ADEWI-Rwanda project are documented here.  
Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `tests/test_anomalies.py` — unit tests for climatology and Z-score computation
- `tests/test_combined_index.py` — unit tests for ADEWI/CADI index construction and drought classification
- `tests/test_preprocessing.py` — unit tests for gap interpolation, physical clipping, and calendar attachment
- `tests/test_validation.py` — unit tests for known-period hit-rate and crop-correlation helpers
- `tests/conftest.py` — shared pytest fixtures (minimal synthetic DataFrame)
- `scripts/sensitivity_analysis.py` — equal-weight and leave-one-out sensitivity tests for ADEWI
- `LICENSE` — MIT licence for open reproducibility
- `CHANGELOG.md` — this file
- `CONTRIBUTING.md` — contributor guide

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
