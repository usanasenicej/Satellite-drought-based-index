# Agricultural Drought Early-Warning Index (ADEWI) for Rwanda

Independent research pipeline for:

**Development of a Satellite-Based Agricultural Drought Early-Warning Index for Rwanda: Assessing Lead Time of Combined Vegetation, Rainfall and Soil Moisture Anomalies**

Study area: Eastern and Southern Provinces, January 2018 – December 2024.  
Target outlet: *Rwanda Journal of Agricultural Sciences* (or a UR CAFF agriculture journal).

## What this repository does

1. Loads NDVI, EVI, CHIRPS rainfall, soil moisture and land-surface temperature for the two provinces.
2. Converts each variable to a day-of-year standardized anomaly (Z-score).
3. Builds two indices:
   - **ADEWI** (early warning, no vegetation): `0.40·Z_rain + 0.35·Z_SM − 0.25·Z_LST`
   - **CADI** (status index, includes vegetation): weighted mix of NDVI, EVI, rain, SM and LST
4. Measures **lead time in weeks**: how much earlier ADEWI crosses −1.0 than NDVI.
5. Writes publication figures, CSV/Excel tables, a run report, and a Streamlit demo.

Drought classes (index value): Mild < −0.5, Moderate < −1.0, Severe < −1.5, Extreme < −2.0.

## Important: synthetic vs satellite data

On a fresh clone the pipeline **runs immediately** using a physically motivated **synthetic** cube (bimodal Rwanda seasons, dry pulses around 2022 and 2023, vegetation lagging rainfall/soil moisture). That is for software testing and learning the workflow.

**Do not submit synthetic numbers as observational results.** To produce the paper:

1. Create a [Google Earth Engine](https://earthengine.google.com/) account (and/or [Digital Earth Africa Sandbox](https://sandbox.digitalearthafrica.org)).
2. Run `scripts/gee_export_code_editor.js` in the GEE Code Editor (easiest) **or** `python scripts/gee_export_timeseries.py` after `earthengine authenticate`.
3. Download `provincial_timeseries.csv` and save it as `data/raw/provincial_timeseries.csv`.
4. Required columns: `time, province, ndvi, evi, rainfall, soil_moisture, lst` with `province` ∈ {Eastern, Southern}.
5. Re-run the pipeline. Outputs will be tagged `data_source = observed` if you add that column (otherwise leave it; the loader marks file-based inputs as observed).

Replace `data/raw/nisr_crop_production_placeholder.csv` with official NISR / MINAGRI production figures before claiming crop validation.

## Setup (Windows)

```powershell
cd D:\Codes\Backend\Research
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Run the analysis

```powershell
python -m adewi
```

Outputs:

| Path | Contents |
|---|---|
| `results/figures/` | Time series, lead-time bars, maps, validation plots |
| `results/tables/` | Lead-time events, summary, quality, known-drought table, Excel workbook |
| `data/processed/adewi_index_timeseries.csv` | Full index used by the paper and the app |
| `results/run_report.json` | Mean lead time, success rate, file list |

## Streamlit prototype

```powershell
streamlit run app/streamlit_app.py
```

Select province and year to see ADEWI vs NDVI, drought class, and lead-time events.

## Notebooks

`notebooks/01_data_loading.ipynb` … `05_final_figures.ipynb` mirror the modules under `src/adewi/`. Prefer `python -m adewi` when you want all figures at once.

## Suggested student workflow

| Phase | Action |
|---|---|
| 0 | Read 3–4 papers (Rwanda SPEI/VHI 2024 and CHIRPS/MODIS drought papers). Create GEE + DE Africa accounts. |
| 1 | Run GEE export; QC the CSV (missing %, range of NDVI 0–1, rainfall ≥ 0). |
| 2 | Run `python -m adewi`. Inspect figures. Optionally change weights in `config/config.yaml`. |
| 3 | Fill `paper/manuscript_draft.md` Results with **observed** numbers from `results/tables/`. |
| 4 | Swap placeholder crop statistics; report Pearson correlations honestly (including non-significant ones). |
| 5 | Demo the Streamlit app in a presentation. |

## Ethical / academic notes

- High-school independent research: keep the methods transparent; do not over-claim operational early-warning skill from one study.
- Cite dataset DOIs (MODIS, CHIRPS, FLDAS, FAO GAUL).
- Cloud/quality screening is only as good as the GEE reducer; document scale (5 km provincial means) as a limitation versus 250 m pixel maps.
