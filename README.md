
# Agricultural Drought Early-Warning Index (ADEWI) for Rwanda

**A satellite-based research project combining climate analytics, remote sensing, and environmental time-series analysis to investigate the early detection of agricultural drought.**

**Research Areas:** Remote Sensing · Climate Analytics · Environmental Data Science · Agricultural Drought Monitoring

---

## Table of Contents

- [Research Overview](#research-overview)
- [Research Question](#research-question)
- [Research Objectives](#research-objectives)
- [Study Area and Scope](#study-area-and-scope)
- [Methodology](#methodology)
- [Repository Features](#repository-features)
- [Quick Start](#quick-start)
- [Running the Analysis](#running-the-analysis)
- [Interactive Dashboard](#interactive-dashboard)
- [Expected Outputs](#expected-outputs)
- [Configuration Reference](#configuration-reference)
- [Obtaining Observational Data](#obtaining-observational-data)
- [Jupyter Notebooks](#jupyter-notebooks)
- [Research Status and Limitations](#research-status-and-limitations)
- [Reproducibility and Integrity](#reproducibility-and-integrity)

---

## Research Overview

Agricultural drought can threaten crop productivity, food security, and rural livelihoods. However, conventional vegetation-based indicators may respond only after crops have already begun experiencing water stress.

This project investigates whether combining rainfall, soil moisture, and land-surface temperature anomalies can provide earlier indications of agricultural drought than vegetation-based indicators alone.

To investigate this, the project develops two indices:

- **Agricultural Drought Early-Warning Index (ADEWI):** Combines rainfall, soil moisture, and land-surface temperature anomalies to investigate the potential for earlier drought detection.
- **Combined Agricultural Drought Index (CADI):** Incorporates vegetation indicators alongside climate and soil-related variables to provide a broader assessment of agricultural drought conditions.

The research is supported by a reproducible Python analysis pipeline and an interactive Streamlit application for exploring environmental anomalies, drought signals, and potential detection lead times.

The study focuses on Rwanda's Eastern and Southern Provinces, using environmental time-series data spanning January 2018 through December 2024.

### Research Question

> Can a multi-variable index based on rainfall, soil moisture, and land-surface temperature anomalies detect agricultural drought earlier than vegetation-based indicators in Eastern and Southern Rwanda?

### Research Objectives

1. Develop a reproducible workflow for processing environmental time-series data.
2. Calculate standardized anomalies for vegetation, rainfall, soil moisture, and land-surface temperature.
3. Construct ADEWI and CADI using environmental anomaly measurements.
4. Compare drought signal timing and estimate potential detection lead time.
5. Evaluate the sensitivity and reliability of the proposed indices using appropriate validation data.
6. Produce reproducible figures, tables, and an interactive research application.

## Study Area and Scope

| Attribute | Description |
|---|---|
| Study Area | Eastern and Southern Provinces, Rwanda |
| Study Period | January 2018 – December 2024 |
| Temporal Resolution | 16-day composites |
| Research Domain | Remote Sensing, Climate Analytics, Agricultural Drought Monitoring |
| Research Level | Independent Student Research |
| Current Version | `v0.2.0` |
| Intended Publication | Rwanda Journal of Agricultural Sciences or a relevant University of Rwanda agriculture journal |

---

## Methodology

The research follows a multi-stage analytical workflow, beginning with environmental data acquisition and preprocessing, followed by anomaly computation, index construction, drought classification, and lead-time analysis.

### 1. Environmental Data

The analysis is designed to use satellite-derived and climate-related environmental measurements.

| Variable | Purpose | Potential Data Source |
|---|---|---|
| NDVI | Measures vegetation greenness and condition | MODIS |
| EVI | Provides a complementary vegetation indicator | MODIS |
| Rainfall | Captures precipitation deficits | CHIRPS |
| Soil Moisture | Represents water availability in the soil | FLDAS or another documented product |
| Land Surface Temperature (LST) | Captures thermal conditions associated with water stress | MODIS |

The workflow uses provincial time-series data for the Eastern and Southern Provinces.

Dataset selection, spatial and temporal resolution, quality screening, and aggregation methods must be documented before interpreting the results.

### 2. Standardized Anomalies

Environmental variables are converted into standardized anomalies to make deviations from expected conditions comparable.

The conventional Z-score is calculated as:

$$
Z_t = \frac{X_t-\mu}{\sigma}
$$

Where:

- $X_t$ represents the observed value at time $t$.
- $\mu$ represents the reference-period mean.
- $\sigma$ represents the reference-period standard deviation.

For seasonal environmental data, the reference distribution accounts for seasonal variation using 16-day day-of-year composite climatological bins.

Anomaly interpretation:

| Variable | Negative Anomaly | Positive Anomaly |
|---|---|---|
| Rainfall | Below-reference precipitation | Above-reference precipitation |
| Soil Moisture | Drier-than-reference conditions | Wetter-than-reference conditions |
| NDVI | Below-reference vegetation greenness | Above-reference vegetation greenness |
| EVI | Below-reference vegetation condition | Above-reference vegetation condition |
| LST | Cooler-than-reference surface conditions | Warmer-than-reference surface conditions |

### 3. Agricultural Drought Early-Warning Index (ADEWI)

ADEWI combines rainfall, soil moisture, and land-surface temperature anomalies:

$$
\mathrm{ADEWI} =
0.40Z_{\mathrm{rain}} +
0.35Z_{\mathrm{SM}} -
0.25Z_{\mathrm{LST}}
$$

The initial formulation assigns:

- 40% weight to rainfall anomalies.
- 35% weight to soil moisture anomalies.
- 25% weight to land-surface temperature anomalies.

The negative temperature coefficient reflects the expectation that unusually high surface temperatures can accompany agricultural water stress.

**Note:** These coefficients are proposed starting values, not established optimal weights. Their suitability must be evaluated through sensitivity analysis and, where possible, independent validation.

ADEWI excludes vegetation variables so that its drought signals can be compared against vegetation-based indicators without directly incorporating the same vegetation measurements into both sides of the comparison.

### 4. Combined Agricultural Drought Index (CADI)

CADI incorporates vegetation indicators alongside rainfall, soil moisture, and land-surface temperature.

The proposed formulation is:

$$
\begin{aligned}
\mathrm{CADI} ={}&
0.30Z_{\mathrm{NDVI}} +
0.15Z_{\mathrm{EVI}} \\
&+ 0.30Z_{\mathrm{rain}} +
0.20Z_{\mathrm{SM}} \\
&- 0.20Z_{\mathrm{LST}}
\end{aligned}
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

The analysis examines detected events, seasonal lead-time distributions, and false-alarm statistics.

---

## Repository Features

The repository provides an end-to-end research workflow covering environmental data processing, index construction, statistical analysis, and visualization.

### Analytical Pipeline

- Environmental time-series loading and preprocessing.
- Standardized anomaly calculation.
- ADEWI and CADI construction.
- Drought classification and signal detection.
- Lead-time analysis and event matching.
- Data-quality checks and summary statistics.
- Sensitivity analysis.

### Research Outputs

- Publication-oriented figures and visualizations.
- Statistical summary tables.
- Lead-time event analysis.
- Excel workbooks.
- Machine-readable CSV outputs.
- JSON execution reports.

### Interactive Exploration

- Streamlit-based research dashboard.
- Geospatial drought exploration.
- Temporal severity visualization.
- Provincial comparisons.
- Adjustable index weights and sensitivity testing.
- Filtered data and event exports.

### Research Tools

- Python-based analytical pipeline.
- Google Earth Engine data extraction scripts.
- Jupyter notebooks for inspecting individual analysis stages.
- Configurable research parameters.

---

## Quick Start

Get from repository clone to the complete analytical pipeline and interactive dashboard in a few steps.

### 1. Clone the Repository

```bash
git clone https://github.com/usanasenicej/Satellite-drought-based-index.git

cd Satellite-drought-based-index
```

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip

pip install -e ".[dev]"
```

Alternatively:

```bash
pip install -r requirements.txt
```

### 4. Execute the ADEWI Pipeline

```bash
adewi
```

Alternatively:

```bash
python -m adewi
```

### 5. Launch the Interactive Dashboard

```bash
streamlit run app/streamlit_app.py
```

> **Windows PowerShell Tip:** You can also execute `./run.ps1` to automatically bootstrap the environment and run the complete pipeline.

---

## Running the Analysis

Run the main pipeline through the installed command-line entry point:

```bash
adewi
```

Or:

```bash
python -m adewi
```

The pipeline processes available environmental time-series data, calculates the drought indices, performs the configured analysis, and generates the corresponding outputs.

---

## Interactive Dashboard

The project includes a Streamlit application for exploring the analytical results interactively.

Launch the application:

```bash
streamlit run app/streamlit_app.py
```

### Dashboard Components

| Section | Functionality |
|---|---|
| **Time Series** | Explore multi-variable anomaly trajectories and yearly summaries. |
| **Lead-Time Analysis** | Examine detected events, seasonal lead-time distributions, and false-alarm statistics. |
| **Drought Map & Explorer** | Explore district-centroid geographic maps, temporal severity strips, and provincial comparisons. |
| **Sensitivity Analysis** | Adjust index weights, inspect normalization feedback, and compare alternative scenarios. |
| **Data Export** | Download filtered datasets and detected events as CSV files. |

---

## Expected Outputs

After successfully executing the pipeline, generated files are organized into the following locations:

| Output Path | Description |
|---|---|
| `results/figures/` | Generated time-series, lead-time, mapping, and validation figures (300 DPI PNG). |
| `results/tables/` | Summary statistics, lead-time events, quality checks, and Excel outputs. |
| `data/processed/adewi_index_timeseries.csv` | Processed time series containing calculated indices. |
| `results/run_report.json` | Machine-readable summary of the execution and generated outputs. |

---

## Configuration Reference

The analysis pipeline is configurable through:

```text
config/config.yaml
```

The configuration file controls study settings, index weights, drought classification thresholds, and synthetic data generation.

| Section | Parameter | Default | Description |
|---|---|---|---|
| `study` | `temporal_resolution` | `16D` | Temporal step aligned with MODIS composites. |
| `weights.adewi` | `rainfall / soil_moisture / lst` | `0.40 / 0.35 / 0.25` | Relative component weights for ADEWI. |
| `weights.cadi` | `ndvi / evi / rainfall / ...` | `0.30 / 0.15 / 0.30 / ...` | Component weights for CADI. |
| `drought.classes` | `Mild / Moderate / Severe / Extreme` | `-0.5 / -1.0 / -1.5 / -2.0` | Drought severity classification thresholds. |
| `drought` | `adewi_event_threshold` | `-1.0` | Threshold defining an ADEWI event. |
| `synthetic` | `enabled / seed` | `true / 42` | Controls synthetic data generation when raw CSV data is absent. |

---

## Obtaining Observational Data

The project includes Google Earth Engine scripts for obtaining environmental time-series data.

1. Set up a [Google Earth Engine](https://earthengine.google.com/) account.
2. Run `scripts/gee_export_code_editor.js` in the Earth Engine Code Editor, or use `scripts/gee_export_timeseries.py`.
3. Save the exported CSV to:

   ```text
   data/raw/provincial_timeseries.csv
   ```

4. Re-run the pipeline:

   ```bash
   adewi
   ```

The pipeline can then recompute the results using the configured observational dataset.

---

## Jupyter Notebooks

The repository includes Jupyter notebooks for inspecting individual research stages.

| Notebook | Stage | Description |
|---|---|---|
| `01_data_loading.ipynb` | Phase 1 | Load environmental data and clip to the study area. |
| `02_preprocessing.ipynb` | Phase 1–2 | Clean data, handle missing values, and calculate anomalies. |
| `03_combined_index.ipynb` | Phase 2–3 | Construct ADEWI and CADI and classify drought severity. |
| `04_lead_time_analysis.ipynb` | Phase 3 | Detect events, match lead times, and conduct seasonal analysis. |
| `05_final_figures.ipynb` | Phase 4 | Generate maps, graphs, and research tables. |

---

## Research Status and Limitations

**This repository is a research prototype, not a validated operational drought-warning service.**

The pipeline is designed to run with synthetic environmental data until observational datasets are obtained and configured.

Synthetic data allow the software workflow to be tested, but they are not observations of actual drought events in Rwanda and cannot establish the real-world predictive performance of ADEWI.

Further evaluation requires:

- Actual satellite-derived and climate observational datasets.
- Documented preprocessing and quality-control procedures.
- Sensitivity analysis of the proposed index coefficients.
- Independent validation against appropriate drought reference data.
- Evaluation of detection lead times and false alarms.

Research findings should be interpreted in accordance with the data sources and validation procedures used.

---

## Reproducibility and Integrity

Reproducibility and research integrity are central to this project.

For every reported result, preserve:

- Original environmental dataset metadata.
- Data preprocessing and quality-control procedures.
- Standardization reference periods.
- Index coefficients and configuration parameters.
- Drought classification thresholds.
- Analysis outputs and execution reports.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines, development practices, and testing procedures.

---

**Developed as an independent research project investigating the potential of satellite-derived environmental indicators for earlier agricultural drought detection in Rwanda.**
