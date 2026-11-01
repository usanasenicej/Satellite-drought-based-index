
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
| Intended publication | Rwanda Journal of Agricultural Sciences or a relevant University of Rwanda agriculture journal |

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

For seasonal environmental data, the reference distribution should account for seasonal variation.

Negative rainfall and soil-moisture anomalies indicate drier-than-reference conditions. Negative NDVI and EVI anomalies indicate below-reference vegetation greenness, while positive LST anomalies can indicate unusually warm surface conditions.

### 3. Agricultural Drought Early-Warning Index (ADEWI)

ADEWI combines rainfall, soil moisture, and land-surface temperature anomalies:

$$
\mathrm{ADEWI}
=0.40Z_{\mathrm{rain}}
+0.35Z_{\mathrm{SM}}
-0.25Z_{\mathrm{LST}}
$$

The initial formulation assigns the highest weight to rainfall, followed by soil moisture and land-surface temperature.

The negative temperature coefficient reflects the expectation that unusually high surface temperatures can accompany agricultural water stress.

**These coefficients are proposed starting values, not established optimal weights.** Their suitability must be evaluated through sensitivity analysis and, where possible, independent validation.

ADEWI excludes vegetation variables so that its drought signals can be compared with vegetation-based indicators without directly incorporating the same vegetation measurements into both sides of the comparison.

### 4. Combined Agricultural Drought Index (CADI)

CADI incorporates vegetation indicators alongside rainfall, soil moisture, and land-surface temperature.

The implementation uses a weighted combination of NDVI, EVI, rainfall, soil moisture, and LST anomalies.

Its exact coefficients and sign conventions should be taken from the project configuration and documented alongside the ADEWI formulation.

Because CADI includes vegetation variables, it is intended as a broader assessment of agricultural drought conditions rather than an independent predictor for evaluating lead time against NDVI.

### 5. Drought Classification

The initial drought classification thresholds are:

| Index Value | Classification |
|---|---|
| $>-0.5$ | No drought signal |
| $-1.0 < x \leq -0.5$ | Mild |
| $-1.5 < x \leq -1.0$ | Moderate |
| $-2.0 < x \leq -1.5$ | Severe |
| $x \leq -2.0$ | Extreme |

These thresholds are provisional analytical choices and should be evaluated against the implementation, relevant literature, and the statistical properties of the index.

### 6. Lead-Time Analysis

The pipeline compares the timing of ADEWI threshold crossings with vegetation-based drought signals.

Lead time is calculated as:

$$
L=t_{\mathrm{vegetation}}-t_{\mathrm{ADEWI}}
$$

Where:

- $t_{\mathrm{ADEWI}}$ is the date of the qualifying ADEWI signal.
- $t_{\mathrm{vegetation}}$ is the date of the corresponding vegetation-based signal.
- $L>0$ indicates that ADEWI signaled earlier.
- $L=0$ indicates simultaneous signals.
- $L<0$ indicates that ADEWI signaled later.

A valid lead-time estimate requires consistent temporal resolution, explicit event-matching rules, and defined thresholds.

Earlier threshold crossing alone does not establish successful forecasting. Detected events should also be evaluated against independent drought evidence where suitable data are available.

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
- Interactive Streamlit exploration.
- Jupyter notebooks for inspecting individual analysis stages.

The exact outputs depend on the configured workflow and the input data available.

## Research Status

**This repository is a research prototype, not a validated operational drought-warning service.**

The pipeline is designed to run with synthetic environmental data until observational datasets are obtained and configured.

Synthetic data allow the software workflow to be tested, but they are not observations of actual drought events in Rwanda.

Consequently, synthetic outputs must not be used as evidence of real drought occurrence, measured lead time, agricultural impacts, or index performance.

The scientific conclusions of this project must follow from actual data and analyses performed.

## Installation

### Requirements

- Python version compatible with the project's package configuration.
- Git.
- Required Python dependencies.
- Optional: Google Earth Engine access for exporting observational data.
- Optional: Jupyter for notebook-based analysis.

### Windows Setup

Open PowerShell and navigate to the repository directory:

```powershell
cd D:\Codes\Backend\Research

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e .
```

If PowerShell blocks virtual-environment activation, use an approved environment-specific alternative or configure the execution policy according to your system's security requirements.

## Running the Analysis

Run the main pipeline:

```powershell
python -m adewi
```

The workflow processes the available inputs and writes the configured outputs.

### Expected Outputs

| Path | Purpose |
|---|---|
| `results/figures/` | Generated time-series, lead-time, mapping, and validation figures where supported by the available data |
| `results/tables/` | Summary statistics, lead-time events, quality checks, and Excel outputs |
| `data/processed/adewi_index_timeseries.csv` | Processed time series containing calculated indices |
| `results/run_report.json` | Machine-readable summary of the run and generated outputs |

Output filenames and the availability of individual figures depend on the implementation and the inputs supplied.

## Interactive Exploration

Launch the Streamlit application:

```powershell
streamlit run app/streamlit_app.py
```

The prototype is designed to support exploration of:

- The selected province and year.
- ADEWI and NDVI behavior.
- Drought classifications.
- Detected lead-time events.

The application is an exploratory interface, not a validated operational drought-warning service.

## Obtaining Observational Data

The project is designed to support data acquisition through Google Earth Engine.

1. Set up a [Google Earth Engine](https://earthengine.google.com/) account and review the relevant dataset access requirements.
2. Run `scripts/gee_export_code_editor.js` in the Earth Engine Code Editor, or use `scripts/gee_export_timeseries.py` after configuring and authenticating the Earth Engine Python environment.
3. Export and inspect the resulting time series.
4. Save the prepared file to `data/raw/provincial_timeseries.csv`.
5. Verify column names, units, dates, missing values, quality flags, and province labels.
6. Run the analysis again and inspect the provenance of the generated outputs.

### Expected Data Format

```text
time, province, ndvi, evi, rainfall, soil_moisture, lst
```

The `province` field should identify the Eastern or Southern Province.

Variable units, time intervals, and missing-value conventions must be consistent with the loader's expectations.

A software label indicating that data are observed is not proof of observational provenance. Preserve source metadata and independently verify the origin of all inputs before reporting results.

### Agricultural Production Validation

The file `data/raw/nisr_crop_production_placeholder.csv` is a placeholder, not a verified source of official agricultural statistics.

Before conducting crop-production validation, replace it with documented data from the National Institute of Statistics of Rwanda (NISR), the Ministry of Agriculture and Animal Resources (MINAGRI), or another appropriate authoritative source.

Document crop type, geographic coverage, reporting period, units, and any mismatch between annual production statistics and the index's spatial or temporal resolution.

Do not claim crop validation until the data have been obtained, processed, and analyzed.

## Jupyter Notebooks

The notebooks in `notebooks/` provide a step-by-step view of the analysis.

| Notebook | Stage | Description |
|---|---|---|
| `01_data_loading.ipynb` | Phase 1 | Load environmental data and clip to the study area |
| `02_preprocessing.ipynb` | Phase 1–2 | Clean data, handle missing values, and compute anomalies |
| `03_combined_index.ipynb` | Phase 2–3 | Construct ADEWI and CADI and classify drought severity |
| `04_lead_time_analysis.ipynb` | Phase 3 | Detect events, match lead times, and conduct seasonal analysis |
| `05_final_figures.ipynb` | Phase 4 | Generate maps, graphs, and tables |

Use `python -m adewi` when a complete configured run is preferred over notebook-by-notebook execution.

## Suggested Research Workflow

| Phase | Activities |
|---|---|
| 1. Data acquisition | Export environmental time series and document data provenance, units, resolution, and coverage. |
| 2. Preprocessing | Inspect missingness, outliers, seasonal coverage, spatial aggregation, and quality flags. |
| 3. Anomaly calculation | Verify Z-score distributions and seasonal climatology. |
| 4. Index construction | Inspect ADEWI and CADI behavior and compare their drought signals. |
| 5. Sensitivity analysis | Run `python scripts/sensitivity_analysis.py` and compare lead times across weight scenarios. |
| 6. Validation | Compare detected events with independent drought records and obtain documented crop-production statistics where appropriate. |
| 7. Interpretation | Report lead-time distributions, false alarms, missed events, uncertainty, and regional differences. |
| 8. Manuscript preparation | Populate `paper/manuscript_template.md` with verified observational results, figures, and tables. |
| 9. Demonstration | Use the Streamlit prototype to communicate findings while clarifying its research status. |

## Scientific Integrity and Limitations

The interpretation of this research depends on the quality of the underlying datasets and analytical decisions.

Key considerations include:

- **Data provenance:** Distinguish synthetic test data from observational datasets and retain metadata needed to reproduce the analysis.
- **Index design:** Justify the direction and weights of each component and evaluate alternative formulations.
- **Seasonality:** Use an appropriate reference distribution for seasonal variables and document the baseline.
- **Temporal resolution:** Ensure that lead-time comparisons use compatible timestamps and explicit event-matching procedures.
- **Independent validation:** Do not treat agreement with an index component as independent validation when that same component contributes to the index.
- **Spatial aggregation:** Provincial averages can hide localized drought conditions.
- **Agricultural interpretation:** Vegetation stress and meteorological dryness are related but distinct. A drought signal does not, by itself, establish crop losses or causation.
- **Uncertainty:** Report data gaps, sensitivity to parameter choices, unmatched events, false alarms, and other limitations.
- **Generalizability:** Results from two provinces and the 2018–2024 study period should not automatically be generalized to all of Rwanda or future climate conditions.
- **Operational readiness:** A research prototype should not be described as a validated early-warning service without appropriate evaluation and independent evidence.

## Reproducibility

For every reported result, retain:

- Dataset names, versions, access dates, and citations.
- Preprocessing and quality-screening decisions.
- Spatial and temporal aggregation methods.
- Anomaly reference periods and standardization procedures.
- Index coefficients and classification thresholds.
- Event-matching and lead-time definitions.
- Software dependencies and configuration settings.
- Generated tables, figures, and run reports.

Relevant data documentation includes:

- [Google Earth Engine](https://earthengine.google.com/)
- [MODIS](https://modis.gsfc.nasa.gov/)
- [CHIRPS](https://www.chc.ucsb.edu/data/chirps)
- [NASA FLDAS](https://ldas.gsfc.nasa.gov/fldas)
- [FAO GAUL](https://data.apps.fao.org/map/catalog/srv/eng/catalog.search#/metadata/9c35ba3e-3e9b-4a4c-9f5e-7a4c7b9a4a5a)

Include citations for the datasets actually used in the analysis and in the research manuscript.

## Research Direction

ADEWI explores whether environmental signals can be combined to identify potentially adverse agricultural conditions before vegetation indicators show a comparable response.

By providing a reproducible workflow for index construction, event comparison, and validation, this project aims to support further investigation into satellite-based agricultural drought monitoring in Rwanda.
