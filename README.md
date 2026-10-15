# Agricultural Drought Early-Warning Index (ADEWI) for Rwanda

**Independent Research Project | Remote Sensing · Climate Analytics · Agricultural Drought Monitoring**

Development of a Satellite-Based Agricultural Drought Early-Warning Index for Rwanda: Assessing Lead Time of Combined Vegetation, Rainfall and Soil Moisture Anomalies

**Study area:** Eastern and Southern Provinces, Rwanda  
**Study period:** January 2018 – December 2024  
**Research level:** Independent student research  
**Intended publication:** *Rwanda Journal of Agricultural Sciences* or a relevant University of Rwanda agriculture journal

---

## Overview

Agricultural drought threatens crop productivity, food security, and rural livelihoods. However, vegetation-based drought indicators may respond only after crops have already experienced water stress.

This project investigates whether combining rainfall, soil moisture, and land-surface temperature anomalies can identify potential agricultural drought conditions earlier than vegetation-based indicators alone.

The project develops an analytical pipeline for calculating the **Agricultural Drought Early-Warning Index (ADEWI)** and comparing its drought signals with vegetation-based indicators across Rwanda's Eastern and Southern Provinces from 2018 to 2024.

The central research question is:

> Can a multi-variable index based on rainfall, soil moisture, and land-surface temperature anomalies detect agricultural drought earlier than vegetation-based indicators in Eastern and Southern Rwanda?

The analysis focuses on drought signal timing, lead time, temporal behavior, data quality, and the potential usefulness of combining multiple environmental indicators.

**Research objective:** Evaluate whether the proposed index provides earlier drought signals than vegetation-based indicators. The existence and magnitude of any lead time must be established using observational data rather than assumed in advance.

## Research objectives

1. Develop a reproducible pipeline for processing environmental time-series data for Eastern and Southern Rwanda.
2. Calculate standardized anomalies for vegetation, rainfall, soil moisture, and land-surface temperature.
3. Construct ADEWI and a complementary Combined Agricultural Drought Index (CADI).
4. Compare ADEWI drought signals with vegetation-based drought signals and estimate detection lead time.
5. Evaluate the robustness of the results through data-quality checks, sensitivity analysis, and independent validation where suitable data are available.
6. Produce reproducible figures, tables, and a demonstration application for exploring the results.

## Methodology

### 1. Environmental data

The pipeline is designed to work with the following variables:

| Variable | Role in the analysis | Potential data source |
|---|---|---|
| NDVI | Measures vegetation greenness and condition | MODIS |
| EVI | Provides a complementary vegetation indicator | MODIS |
| Rainfall | Captures precipitation deficits | CHIRPS |
| Soil moisture | Represents water availability in the soil | FLDAS or another documented soil-moisture product |
| Land-surface temperature (LST) | Captures thermal conditions associated with water stress | MODIS |

The workflow uses provincial time-series data for the Eastern and Southern Provinces. Dataset selection, temporal resolution, spatial resolution, quality screening, and aggregation methods should be documented in the final study.

Data-source availability does not itself establish that a dataset has already been downloaded, processed, or validated.

### 2. Standardized anomalies

Environmental variables are converted into standardized anomalies to make their deviations from expected conditions comparable.

A conventional Z-score is:

\[
Z_t = \frac{X_t-\mu}{\sigma}
\]

where:

- \(X_t\) is the observed value at time \(t\).
- \(\mu\) is the reference-period mean.
- \(\sigma\) is the reference-period standard deviation.

For seasonal environmental data, the reference distribution should account for seasonal variation. The exact temporal grouping, baseline period, missing-data treatment, and minimum sample requirements must be specified in the implementation and documented in the manuscript.

For rainfall and soil moisture, negative anomalies indicate drier-than-reference conditions. For NDVI and EVI, negative anomalies indicate below-reference vegetation greenness. Positive LST anomalies can indicate unusually warm surface conditions.

### 3. Agricultural Drought Early-Warning Index (ADEWI)

The initial ADEWI formulation combines rainfall, soil moisture, and land-surface temperature anomalies:

\[
\mathrm{ADEWI}
=0.40Z_{\mathrm{rain}}
+0.35Z_{\mathrm{SM}}
-0.25Z_{\mathrm{LST}}
\]

The formulation assigns a higher weight to rainfall, followed by soil moisture and land-surface temperature. The negative temperature coefficient reflects the expectation that unusually high surface temperatures can accompany agricultural water stress.

**Important:** These weights are proposed starting values, not established optimal coefficients. Their suitability should be evaluated through sensitivity analysis and, where possible, independent validation.

ADEWI excludes vegetation variables so that its signals can be compared with vegetation-based indicators without directly incorporating the same vegetation measurements into both sides of the comparison.

### 4. Combined Agricultural Drought Index (CADI)

CADI incorporates vegetation indicators alongside rainfall, soil moisture, and land-surface temperature.

The implementation uses a weighted combination of NDVI, EVI, rainfall, soil moisture, and LST anomalies. Its exact coefficients and sign conventions should be taken from the project configuration and documented alongside the ADEWI formulation.

CADI represents a broader assessment of agricultural drought conditions. Because it includes vegetation variables, it should not be treated as an independent predictor when evaluating lead time against NDVI.

### 5. Drought classification

The initial classification thresholds are:

| Index value | Initial classification |
|---|---|
| \(>-0.5\) | No drought signal under the proposed classification |
| \(-1.0 < x \leq -0.5\) | Mild |
| \(-1.5 < x \leq -1.0\) | Moderate |
| \(-2.0 < x \leq -1.5\) | Severe |
| \(x \leq -2.0\) | Extreme |

These thresholds are provisional analytical choices. They should be checked against the implementation, relevant literature, and the statistical properties of the index before being used for scientific interpretation.

### 6. Lead-time analysis

The pipeline compares the timing of ADEWI threshold crossings with vegetation-based drought signals.

Lead time is measured in weeks:

\[
L=t_{\mathrm{vegetation}}-t_{\mathrm{ADEWI}}
\]

where:

- \(t_{\mathrm{ADEWI}}\) is the date of the qualifying ADEWI signal.
- \(t_{\mathrm{vegetation}}\) is the date of the corresponding vegetation-based signal.
- \(L>0\) indicates that ADEWI signaled earlier.
- \(L=0\) indicates simultaneous signals.
- \(L<0\) indicates that ADEWI signaled later.

A valid lead-time estimate requires an explicit event-matching method, consistent temporal resolution, defined thresholds, and rules for unmatched events. Earlier threshold crossing alone does not prove successful forecasting: detected events should also be evaluated against independent drought evidence, where available.

---

## Repository features

The repository provides an end-to-end analysis workflow intended to support reproducible research.

- Environmental time-series loading and preprocessing.
- Standardized anomaly calculation.
- ADEWI and CADI construction.
- Drought classification and signal detection.
- Lead-time analysis.
- Data-quality checks and summary statistics.
- Publication-oriented figures and tables.
- Excel workbook and machine-readable CSV outputs.
- JSON run report.
- Streamlit demonstration application.
- Jupyter notebooks for inspecting individual analysis stages.

The exact outputs depend on the configured workflow and the input data available.

## Data status: synthetic versus observed

**Synthetic data are for testing, not scientific evidence.**

A fresh clone is designed to run using a synthetic environmental dataset representing plausible seasonal patterns and drought-like disturbances. This allows the software workflow to be tested before external datasets are obtained.

Synthetic data may include simulated rainfall and soil-moisture variation, vegetation responses, and dry-period scenarios. These patterns are assumptions for testing; they are not observations of actual drought events in Rwanda.

Never use synthetic outputs as evidence of real drought occurrence, measured lead time, agricultural impacts, or index performance in a research manuscript.

### Obtaining observational data

1. Set up a [Google Earth Engine](https://earthengine.google.com/) account and review the relevant dataset access requirements.
2. Run `scripts/gee_export_code_editor.js` in the Earth Engine Code Editor, or use `scripts/gee_export_timeseries.py` after configuring and authenticating the Earth Engine Python environment.
3. Export and inspect the resulting time series.
4. Save the prepared file to `data/raw/provincial_timeseries.csv`.
5. Verify column names, units, dates, missing values, quality flags, and province labels.
6. Run the analysis again and inspect the provenance of the generated outputs.

Expected columns:

```text
time, province, ndvi, evi, rainfall, soil_moisture, lst
```

The `province` field should identify the Eastern or Southern Province. Variable units, time intervals, and missing-value conventions must be consistent with the loader's expectations.

The loader's current behavior determines whether a file-based dataset is tagged as observed. **A software label is not proof of observational provenance.** Preserve source metadata and independently verify the origin of all inputs before reporting results.

### Agricultural production validation

The file `data/raw/nisr_crop_production_placeholder.csv` is a placeholder, not a verified source of official agricultural statistics.

Before conducting crop-production validation, replace it with documented data from the National Institute of Statistics of Rwanda (NISR), the Ministry of Agriculture and Animal Resources (MINAGRI), or another appropriate authoritative source.

Document crop type, geographic coverage, reporting period, units, and any mismatch between annual production statistics and the index's spatial or temporal resolution.

Do not claim crop validation until the data have been obtained, processed, and analyzed.

---

## Installation

### Requirements

- Python version compatible with the project's package configuration.
- Git.
- Required Python dependencies.
- Optional: Google Earth Engine access for exporting observational data.
- Optional: Jupyter for notebook-based analysis.

### Windows setup

Open PowerShell and navigate to the repository directory:

```powershell
cd D:\Codes\Backend\Research

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e .
```

If PowerShell blocks virtual-environment activation, use an approved environment-specific alternative or configure the execution policy according to your system's security requirements.

## Running the analysis

Run the main pipeline:

```powershell
python -m adewi
```

The workflow processes the available inputs and writes the configured outputs.

### Expected outputs

| Path | Purpose |
|---|---|
| `results/figures/` | Generated time-series, lead-time, mapping, and validation figures where supported by the available data |
| `results/tables/` | Summary statistics, lead-time events, quality checks, drought-event tables, and Excel outputs |
| `data/processed/adewi_index_timeseries.csv` | Processed time series containing the calculated indices |
| `results/run_report.json` | Machine-readable summary of the run, including reported metrics and output files |

Output filenames and the availability of individual figures depend on the implementation and the inputs supplied.

## Streamlit demonstration

Launch the interactive application:

```powershell
streamlit run app/streamlit_app.py
```

The prototype is designed to support exploration of the selected province and year, ADEWI and NDVI behavior, drought classifications, and detected lead-time events.

The application is an exploratory interface, not a validated operational drought-warning service.

## Jupyter notebooks

The notebooks in `notebooks/` provide a step-by-step view of the analysis, from loading data through generating final figures.

The notebook sequence includes:

- `01_data_loading.ipynb`
- `05_final_figures.ipynb`

Intermediate notebooks cover the stages implemented in the repository. Use the main command, `python -m adewi`, when a complete configured run is preferred.

## Suggested research workflow

| Phase | Activities |
|---|---|
| 1. Literature review | Review research on agricultural drought indicators, rainfall anomalies, vegetation indices, soil moisture, and drought monitoring in Rwanda and East Africa. |
| 2. Data acquisition | Obtain the required environmental datasets and document their provenance, units, resolution, and coverage. |
| 3. Quality control | Inspect missingness, outliers, seasonal coverage, spatial aggregation, and product-specific quality flags. |
| 4. Index construction | Run the pipeline and inspect anomaly distributions, index behavior, and drought-event timing. |
| 5. Sensitivity analysis | Test alternative index weights, anomaly baselines, drought thresholds, and event-matching rules. |
| 6. Validation | Compare detected events with independent drought records and suitable agricultural statistics, where available. |
| 7. Interpretation | Report lead-time distributions, missed events, false alarms, uncertainty, and regional differences. |
| 8. Manuscript preparation | Populate the manuscript with verified observational results, methods, figures, limitations, and reproducibility details. |
| 9. Demonstration | Use the Streamlit prototype to communicate the method and findings without presenting it as an operational warning system. |

## Scientific integrity and limitations

This project is an independent research effort. Its scientific conclusions must follow from the actual data and analyses performed.

Key considerations include:

- **Data provenance:** Clearly distinguish synthetic test data from observational datasets and retain the metadata needed to reproduce the analysis.
- **Index design:** Justify the direction and weights of each component and test whether conclusions change under reasonable alternatives.
- **Seasonality:** Use an appropriate reference distribution for seasonal variables and document how the baseline is defined.
- **Temporal resolution:** Ensure that lead-time comparisons use compatible timestamps and an explicit event-matching procedure.
- **Independent validation:** Do not treat agreement with an index component as independent validation when that same component contributes to the index.
- **Spatial aggregation:** Provincial averages can hide localized drought conditions. A provincial time series does not provide the same information as a pixel-level drought map.
- **Agricultural interpretation:** Vegetation stress and meteorological dryness are related but distinct. A drought signal does not, by itself, establish crop losses or causation.
- **Uncertainty:** Report data gaps, sensitivity to parameter choices, unmatched events, false alarms, and other limitations.
- **Generalizability:** Results from two provinces and the 2018–2024 study period should not automatically be generalized to all of Rwanda or future climate conditions.
- **Operational readiness:** A research prototype should not be described as a validated early-warning service without appropriate evaluation, reliability testing, and independent evidence.

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

Dataset documentation and citations should be included in the manuscript. Relevant sources include [Google Earth Engine](https://earthengine.google.com/), [MODIS](https://modis.gsfc.nasa.gov/), [CHIRPS](https://www.chc.ucsb.edu/data/chirps), [NASA FLDAS](https://ldas.gsfc.nasa.gov/fldas), and [FAO GAUL](https://data.apps.fao.org/map/catalog/srv/eng/catalog.search#/metadata/9c35ba3e-3e9b-4a4c-9f5e-7a4c7b9a4a5a), as applicable to the actual datasets used.

## Research direction

ADEWI explores a practical question in climate-informed agriculture: whether environmental signals can be combined to identify potentially adverse agricultural conditions before vegetation indicators show a comparable response.

By providing a reproducible workflow for index construction, event comparison, and validation, the project aims to support further investigation into satellite-based agricultural drought monitoring in Rwanda.

**The intended contribution is a testable methodology, not a predetermined result.** Whether ADEWI provides a useful early-warning advantage remains an empirical question.

---

*Independent student research project. Methods, findings, and conclusions should be reported transparently and supported by verifiable data and reproducible analysis.*