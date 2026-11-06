# Agricultural Drought Early-Warning Index (ADEWI) for Rwanda

**A satellite-based research project combining climate and remote-sensing data to investigate early detection of agricultural drought.**

**Research areas:** Remote Sensing · Climate Analytics · Agricultural Drought Monitoring

## Research Overview

Agricultural drought can threaten crop productivity, food security, and rural livelihoods. However, vegetation-based indicators may respond only after crops have already experienced water stress.

This project investigates whether combining rainfall, soil moisture, and land-surface temperature anomalies can provide earlier indications of agricultural drought than vegetation-based indicators alone.

The project develops the **Agricultural Drought Early-Warning Index (ADEWI)** and a complementary Combined Agricultural Drought Index (CADI), supported by a reproducible Python analysis pipeline and an interactive Streamlit application.

The study focuses on Rwanda's Eastern and Southern Provinces, using environmental time-series data spanning January 2018 through December 2024.

### Research Question

Can a multi-variable index based on rainfall, soil moisture, and land-surface temperature anomalies detect agricultural drought earlier than vegetation-based indicators in Eastern and Southern Rwanda?

### Research Objectives

1. Develop a reproducible workflow for processing environmental time-series data.
2. Calculate standardized anomalies for vegetation, rainfall, soil moisture, and land-surface temperature.
3. Construct ADEWI and CADI using environmental anomaly measurements.
4. Compare drought signal timing and estimate potential detection lead time.
5. Evaluate the sensitivity and reliability of the proposed indices using appropriate validation data.
6. Produce reproducible figures, tables, and an interactive research application.

## Study Scope

| Attribute | Description |
|---|---|
| Study area | Eastern and Southern Provinces, Rwanda |
| Study period | January 2018 – December 2024 |
| Research domain | Remote sensing, climate analytics, agricultural drought monitoring |
| Research level | Independent student research |
| Current version | v0.2.0 |
| Intended publication | Rwanda Journal of Agricultural Sciences or a relevant University of Rwanda agriculture journal |

## ⚡ Quick Start

Get from clone to full pipeline and interactive dashboard in four simple steps:

```powershell
# 1. Clone repository and navigate to directory
git clone https://github.com/usanasenicej/Satellite-drought-based-index.git
cd Satellite-drought-based-index

# 2. Create virtual environment and install in editable mode
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# 3. Execute the full ADEWI pipeline
adewi
# or: python -m adewi

# 4. Launch the interactive Streamlit dashboard
streamlit run app/streamlit_app.py
```

> [!TIP]
> On Windows PowerShell, you can also execute `./run.ps1` to automatically bootstrap the environment and run the complete pipeline.

## Methodology

### 1. Environmental Data

The analysis is designed to use satellite-derived and climate-related environmental measurements.

| Variable | Purpose | Potential Data Source |
|---|---|---|
| NDVI | Measures vegetation greenness and condition | MODIS |
| EVI | Provides a complementary vegetation indicator | MODIS |
| Rainfall | Captures precipitation deficits | CHIRPS |
| Soil moisture | Represents water availability in the soil | FLDAS or another documented product |
| Land-surface temperature (LST) | Captures thermal conditions associated with water stress | MODIS |

The workflow uses provincial time-series data for the Eastern and Southern Provinces.

Dataset selection, spatial and temporal resolution, quality screening, and aggregation methods must be documented before the results are interpreted.

### 2. Standardized Anomalies

Environmental variables are converted into standardized anomalies to make deviations from expected conditions comparable.

The conventional Z-score is:

$$
Z_t = \frac{X_t-\mu}{\sigma}
$$

Where:

- $X_t$ is the observed value at time $t$.
- $\mu$ is the reference-period mean.
- $\sigma$ is the reference-period standard deviation.

For seasonal environmental data, the reference distribution accounts for seasonal variation using 16-day day-of-year composite climatological bins.

Negative rainfall and soil-moisture anomalies indicate drier-than-reference conditions. Negative NDVI and EVI anomalies indicate below-reference vegetation greenness, while positive LST anomalies can indicate unusually warm surface conditions.

### 3. Agricultural Drought Early-Warning Index (ADEWI)

ADEWI combines rainfall, soil moisture, and land-surface temperature anomalies:

$$
\mathrm{ADEWI} = 0.40Z_{\mathrm{rain}} + 0.35Z_{\mathrm{SM}} - 0.25Z_{\mathrm{LST}}
$$

The initial formulation assigns the highest weight to rainfall, followed by soil moisture and land-surface temperature.

The negative temperature coefficient reflects the expectation that unusually high surface temperatures can accompany agricultural water stress.

**These coefficients are proposed starting values, not established optimal weights.** Their suitability must be evaluated through sensitivity analysis and, where possible, independent validation.

ADEWI excludes vegetation variables so that its drought signals can be compared with vegetation-based indicators without directly incorporating the same vegetation measurements into both sides of the comparison.

### 4. Combined Agricultural Drought Index (CADI)

CADI incorporates vegetation indicators alongside rainfall, soil moisture, and land-surface temperature:

$$
\mathrm{CADI} = 0.30Z_{\mathrm{NDVI}} + 0.15Z_{\mathrm{EVI}} + 0.30Z_{\mathrm{rain}} + 0.20Z_{\mathrm{SM}} - 0.20Z_{\mathrm{LST}}
$$

Because CADI includes vegetation variables, it is intended as a broader assessment of agricultural drought conditions rather than an independent predictor for evaluating lead time against NDVI.

### 5. Drought Classification

The drought classification thresholds are:

| Index Value | Classification |
|---|---|
| $x \geq -0.5$ | Normal |
| $-1.0 \leq x < -0.5$ | Mild |
| $-1.5 \leq x < -1.0$ | Moderate |
| $-2.0 \leq x < -1.5$ | Severe |
| $x < -2.0$ | Extreme |

### 6. Lead-Time Analysis

The pipeline compares the timing of ADEWI threshold crossings with vegetation-based drought signals.

Lead time is calculated as:

$$
L = t_{\mathrm{vegetation}} - t_{\mathrm{ADEWI}}
$$

Where:

- $t_{\mathrm{ADEWI}}$ is the date of the qualifying ADEWI signal.
- $t_{\mathrm{vegetation}}$ is the date of the corresponding vegetation-based signal.
- $L > 0$ indicates that ADEWI signaled earlier.
- $L = 0$ indicates simultaneous signals.
- $L < 0$ indicates that ADEWI signaled later.

## Repository Features

The repository provides an end-to-end research workflow for:

- Environmental time-series loading and preprocessing.
- Standardized anomaly calculation.
- ADEWI and CADI construction.
- Drought classification and signal detection.
- Lead-time analysis and event matching.
- Data-quality checks and summary statistics.
- Publication-oriented figures and tables.
- Excel workbooks and machine-readable CSV outputs.
- JSON run reports.
- Interactive Streamlit exploration with geospatial mapping and sensitivity testing.
- Jupyter notebooks for inspecting individual analysis stages.

## Research Status

**This repository is a research prototype, not a validated operational drought-warning service.**

The pipeline is designed to run with synthetic environmental data until observational datasets are obtained and configured. Synthetic data allow the software workflow to be tested, but they are not observations of actual drought events in Rwanda.

## Installation

### Requirements

- Python >= 3.10
- Git
- Required Python dependencies (`pip install -e .` or `pip install -r requirements.txt`)

### Windows Setup

```powershell
cd D:\Codes\Backend\Research
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Running the Analysis

Run the main pipeline via the CLI entrypoint:

```powershell
adewi
# or: python -m adewi
```

### Expected Outputs

| Path | Purpose |
|---|---|
| `results/figures/` | Generated time-series, lead-time, mapping, and validation figures (300 DPI PNG) |
| `results/tables/` | Summary statistics, lead-time events, quality checks, and Excel outputs |
| `data/processed/adewi_index_timeseries.csv` | Processed time series containing calculated indices |
| `results/run_report.json` | Machine-readable summary of the run and generated outputs |

## Interactive Exploration

Launch the Streamlit application:

```powershell
streamlit run app/streamlit_app.py
```

Features included in the web interface:
- **Time Series:** Multi-variable anomaly trajectories and yearly summaries.
- **Lead-Time Analysis:** Individual detected events, seasonal lead-time distributions, and false-alarm statistics.
- **Drought Map & Explorer:** District centroid interactive geographic map, temporal severity strip, and provincial comparisons.
- **Sensitivity:** Custom weight sliders, normalization feedback, and side-by-side scenario comparisons.
- **Exporting:** One-click CSV download buttons for filtered data and events.

## Configuration Reference

Settings in `config/config.yaml` control the behavior of the analysis pipeline:

| Section | Parameter | Default | Description |
|---|---|---|---|
| `study` | `temporal_resolution` | `16D` | Temporal step aligned with MODIS composites |
| `weights.adewi` | `rainfall` / `soil_moisture` / `lst` | 0.40 / 0.35 / 0.25 | Relative component weights for ADEWI |
| `weights.cadi` | `ndvi` / `evi` / `rainfall` / ... | 0.30 / 0.15 / 0.30 / ... | Component weights for status CADI |
| `drought.classes` | `Mild` / `Moderate` / `Severe` / `Extreme` | -0.5 / -1.0 / -1.5 / -2.0 | Severity classification thresholds |
| `drought` | `adewi_event_threshold` | -1.0 | Threshold defining an ADEWI event |
| `synthetic` | `enabled` / `seed` | `true` / `42` | Controls synthetic data generation when raw CSV is absent |

## Obtaining Observational Data

1. Set up a [Google Earth Engine](https://earthengine.google.com/) account.
2. Run `scripts/gee_export_code_editor.js` in the Earth Engine Code Editor, or use `scripts/gee_export_timeseries.py`.
3. Save the exported CSV to `data/raw/provincial_timeseries.csv`.
4. Re-run `adewi` to recompute all results against real observations.

## Jupyter Notebooks

| Notebook | Stage | Description |
|---|---|---|
| `01_data_loading.ipynb` | Phase 1 | Load environmental data and clip to the study area |
| `02_preprocessing.ipynb` | Phase 1–2 | Clean data, handle missing values, and compute anomalies |
| `03_combined_index.ipynb` | Phase 2–3 | Construct ADEWI and CADI and classify drought severity |
| `04_lead_time_analysis.ipynb` | Phase 3 | Detect events, match lead times, and conduct seasonal analysis |
| `05_final_figures.ipynb` | Phase 4 | Generate maps, graphs, and tables |

## Reproducibility & Integrity

For every reported result, preserve the underlying dataset metadata, standardization reference periods, and configuration parameters. See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and testing practices.
