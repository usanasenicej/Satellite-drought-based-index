# Changelog

All notable changes to the ADEWI-Rwanda project are documented here.  
Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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
- README: full confirmed study title with "…Assessing the Lead Time…in the Eastern and Southern Provinces"
- README: Quick Start section (5 commands from clone to running app)
- README: complete notebook table with stage descriptions
- README: 9-phase research workflow matching the research brief

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
