# Development of a Satellite-Based Agricultural Drought Early-Warning Index for Rwanda: Assessing the Lead Time of Combined Vegetation, Rainfall and Soil Moisture Anomalies in the Eastern and Southern Provinces

**Target journal:** Rwanda Journal of Agricultural Sciences (RJAS) / UR CAFF agriculture journal  
**Author:** [Student name]  
**Affiliation:** [School]; optional mentor: [University / UR CAFF]  
**Data window:** January 2018 – December 2024  
**Study area:** Eastern and Southern Provinces of Rwanda

> **Manuscript status.** Methods match the open code in this repository. Results tables below must be overwritten with figures from `results/tables/` **after** `data/raw/provincial_timeseries.csv` is replaced by a Google Earth Engine or Digital Earth Africa export. Do not publish numbers generated from the synthetic demonstration cube.

---

## Abstract

Agricultural drought is a recurring threat to rain-fed farming in Rwanda, particularly in the Eastern and Southern Provinces. Vegetation indices such as the Normalized Difference Vegetation Index (NDVI) typically decline only after crops are already stressed, which limits their value for early warning. This study develops a transparent Agricultural Drought Early-Warning Index (ADEWI) that combines standardized anomalies of CHIRPS rainfall, soil moisture and land-surface temperature, and tests whether ADEWI identifies emerging drought before severe NDVI decline. Using 16-day composites for 2018–2024, drought events are defined when the NDVI Z-score remains at or below −1.0 for at least two composites. Lead time is the lag, in weeks, between the first ADEWI crossing of the same threshold and NDVI onset. **[Insert observed mean lead time, success rate, and Eastern vs Southern contrast after the satellite run.]** If the combined index systematically leads NDVI by several weeks, a fully open-data approach can strengthen provincial agricultural drought early warning without proprietary models.

**Keywords:** agricultural drought; early warning; NDVI; CHIRPS; soil moisture; land surface temperature; Rwanda; lead time

---

## 1. Introduction

Rwanda’s crop production is overwhelmingly rain-fed. The Eastern Province, in the rain-shadow of the highlands, and parts of the Southern Province experience high rainfall variability, dry spells within Season A (September–January) and Season B (February–June), and periodic agricultural drought that reduces maize and bean yields and undermines rural livelihoods (NISR seasonal agricultural surveys; MINAGRI reports).

Operational drought monitoring in East Africa often relies on rainfall deficits (SPI/SPEI), vegetation indices (NDVI, VCI, VHI), or blended products. A 2024 Rwanda study combining SPEI and vegetation health indices showed that meteorological and vegetation signals are complementary, but vegetation-only indicators remain lagging. Soil moisture and land-surface temperature (LST) respond faster to rainfall failure than greenness, and are therefore physically plausible precursors of NDVI decline.

The research gap addressed here is **quantitative lead time** for a simple, fully open, multi-variable index over Eastern and Southern Rwanda: *how many weeks before NDVI indicates severe agricultural stress does a rainfall–soil moisture–temperature combination cross a drought threshold?*

The study aims to:

1. Assemble consistent 16-day series of NDVI, EVI, CHIRPS rainfall, soil moisture and LST for the two provinces (2018–2024).
2. Compute climatological standardized anomalies.
3. Construct ADEWI (early warning) and CADI (status index including vegetation).
4. Estimate event-wise lead time of ADEWI relative to NDVI.
5. Compare Eastern vs Southern performance and check consistency with known dry periods and, where official statistics allow, crop production.

The working hypothesis is that ADEWI provides an **average 3–6 week lead** over NDVI-only detection, with higher success during moderate-to-severe events.

---

## 2. Study area and period

Eastern Province (Nyagatare, Gatsibo, Kayonza, Kirehe, Ngoma, Rwamagana, Bugesera) and Southern Province (Gisagara, Huye, Kamonyi, Muhanga, Nyamagabe, Nyanza, Nyaruguru, Ruhango) were selected because they combine high agricultural dependence with documented exposure to dry spells. The analysis period is 1 January 2018 to 31 December 2024, long enough to sample several Season A/B cycles and recent dry episodes (including 2021–23) while remaining within readily available MODIS Collection 6.1 and CHIRPS v2 coverage.

---

## 3. Data and methods

### 3.1 Datasets

| Variable | Product | Native resolution | Composite used |
|---|---|---|---|
| NDVI, EVI | MODIS MOD13Q1 Collection 6.1 | 250 m, 16-day | 16-day mean over province |
| Rainfall | CHIRPS v2.0 pentads | ~5 km | Sum over each 16-day window |
| Soil moisture (0–10 cm) | FLDAS Noah (GEE) *or* ESA CCI SM | ~10 km / 0.25° | Mean over window |
| LST (day) | MODIS MOD11A2 | 1 km, 8-day | Mean, scale factor 0.02 |
| Boundaries | FAO GAUL 2015 level 1 | polygons | Eastern, Southern |

All products are free. Provincial spatial means (reducer scale 5 km in the GEE script) are used so that a high-school workflow remains reproducible without desktop GIS. Pixel-level maps can be added later from the same collections.

### 3.2 Preprocessing

Short gaps (≤2 composites) are linearly interpolated. NDVI/EVI are clipped to [0, 1], rainfall to ≥0, soil moisture to [0, 0.6] m³ m⁻³, and LST to a physical Kelvin range. Rwanda agricultural seasons A/B/C are attached for reporting, but climatology is computed on the 16-day calendar, not on a coarse monthly bin.

### 3.3 Standardized anomalies

For each province, variable and 16-day day-of-year bin:

\[
Z_{v}(t) = \frac{x_{v}(t) - \mu_{v,d}}{\sigma_{v,d}}
\]

where \(\mu_{v,d}\) and \(\sigma_{v,d}\) are the 2018–2024 mean and sample standard deviation of variable \(v\) in that calendar bin. This removes the bimodal seasonal cycle so that negative Z-scores indicate conditions drier (or, for LST, hotter) than normal for that time of year.

### 3.4 ADEWI and CADI

The **Agricultural Drought Early-Warning Index** deliberately excludes vegetation so that it can lead NDVI rather than merely echo it:

\[
\mathrm{ADEWI} = 0.40\,Z_{\mathrm{rain}} + 0.35\,Z_{\mathrm{SM}} - 0.25\,Z_{\mathrm{LST}}
\]

The **Combined Agricultural Drought Index** (status) is:

\[
\mathrm{CADI} = 0.20\,Z_{\mathrm{NDVI}} + 0.15\,Z_{\mathrm{EVI}} + 0.25\,Z_{\mathrm{rain}} + 0.25\,Z_{\mathrm{SM}} - 0.15\,Z_{\mathrm{LST}}
\]

Weights sum to 1. Equal-weight and leave-one-variable-out tests can be reported as sensitivity. Negative values indicate drought-favourable conditions. Classes follow: Mild < −0.5, Moderate < −1.0, Severe < −1.5, Extreme < −2.0.

### 3.5 Lead-time definition (core contribution)

An **NDVI drought event** starts at the first of ≥2 consecutive 16-day composites with \(Z_{\mathrm{NDVI}} \le -1.0\). For each event, the algorithm searches backward up to 12 composites (~6 months) for the first ADEWI value ≤ −1.0.  

\[
\text{lead (weeks)} = \frac{t_{\mathrm{NDVI onset}} - t_{\mathrm{ADEWI onset}}}{7}
\]

Success rate is the fraction of NDVI events with a prior ADEWI crossing. Mean, median, minimum and maximum lead times are reported by province and pooled.

### 3.6 Validation

ADEWI during literature-reported dry windows (2016–17 if overlapping; 2021/22 Season A; early 2023) is summarised (mean, minimum, fraction below −1.0). Optional Pearson correlation is computed between annual mean ADEWI and official maize (or beans) production (NISR/MINAGRI). Placeholder production numbers in the repository **must be replaced** before this section is treated as evidence.

### 3.7 Software

Analysis is implemented in Python 3 (`numpy`, `pandas`, `matplotlib`, `seaborn`) and is fully specified in the companion repository. GEE JavaScript/Python scripts export the observational CSV; a Streamlit app demonstrates the index for a selected province and year.

---

## 4. Results

*[Rewrite this entire section using `results/run_report.json` and `results/tables/` from the observational run. The bullets below are the required reporting template.]*

### 4.1 Data completeness

- Number of 16-day steps per province: ____  
- Missing-value percentages after QC: NDVI ____ %, rainfall ____ %, SM ____ %, LST ____ %  
- Target of 85–90% high-quality coverage: **met / not met**

### 4.2 Behaviour of ADEWI and NDVI

Describe Figure 1 (time series) and Figure 2 (component anomalies). Note whether rainfall and soil moisture Z-scores turn negative before NDVI during 2022 and 2023.

### 4.3 Lead time (main result)

From `table_lead_time_summary.csv`:

| Province | NDVI events | Detected by ADEWI | Success rate | Mean lead (weeks) | Median | Max |
|---|---|---|---|---|---|---|
| Eastern |  |  |  |  |  |  |
| Southern |  |  |  |  |  |  |
| Pooled |  |  |  |  |  |  |

State whether the 3–6 week hypothesis is supported, partially supported, or rejected. Report any events where ADEWI failed (lead missing or negative — negative lead would mean ADEWI lagged NDVI and should be discussed honestly).

### 4.4 Spatial pattern

Describe ADEWI maps for peak dry composites (e.g. January 2022, February 2023). Expect stronger deficits in the Eastern lowlands than in the Southern highlands if the observational data behave as climatology suggests.

### 4.5 Validation against known dry periods and crops

Complete `table_known_drought_validation.csv`. For crop correlation, report *r* and sample size; do not claim causation. If official statistics are unavailable, omit this subsection rather than using placeholders.

---

## 5. Discussion

A multi-variable index can precede NDVI because the soil and atmosphere dry before canopy greenness collapses. That physical order is why ADEWI omits NDVI: including vegetation in the *warning* index would shrink measured lead time by construction.

Limitations to state clearly:

- Provincial means hide district and hillside heterogeneity.
- 2018–2024 climatology is short; Z-scores will change as the record lengthens.
- FLDAS soil moisture is modelled, not in-situ; ESA CCI has gaps.
- GEE 5 km reducers mix cropland with woodland and wetlands unless a cropland mask (e.g. WorldCereal / DE Africa crop mask) is added.
- Lead-time skill in a synthetic cube is **not** evidence of operational skill.

If observed mean lead time falls in the 3–6 week band with success rate above ~70%, ADEWI is a credible candidate for MINAGRI / district agronomist briefing products. If lead time is near zero, the paper’s contribution is still useful: it documents that, for this period and these provinces, vegetation and hydro-thermal anomalies are nearly concurrent, which itself informs early-warning design.

---

## 6. Conclusion

This study specifies a fully open Agricultural Drought Early-Warning Index for Eastern and Southern Rwanda and a reproducible definition of lead time versus NDVI. **[One sentence with the observational mean lead time and success rate.]** The workflow can be updated each 16-day MODIS composite at no data cost. Next steps are cropland masking, district-level reduction, weight optimisation against yield, and comparison with SPEI/VHI products already used in Rwanda.

---

## Acknowledgements

[School, optional UR CAFF mentor, Digital Earth Africa / Google Earth Engine for data access.]

## Data and code availability

Code: this repository. Satellite products: MODIS (NASA LP DAAC), CHIRPS (UCSB / USGS), FLDAS (NASA), FAO GAUL. Crop statistics: NISR / MINAGRI (official tables only).

## References (starter list — expand in the journal’s style)

1. Funk, C. et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. *Scientific Data*.
2. Kogan, F. N. (1995). Application of vegetation index and brightness temperature for drought detection. *Advances in Space Research*.
3. McKee, T. B., Doesken, N. J., & Kleist, J. (1993). The relationship of drought frequency and duration to time scales. *8th Conference on Applied Climatology*.
4. Didan, K. MODIS Vegetation Index Product (MOD13) Algorithm Theoretical Basis Document.
5. Rwanda NISR. Seasonal Agricultural Survey reports (multiple years).
6. [Add the 2024 Rwanda SPEI + VHI paper the student identified.]
7. Enenkel, M. et al. work on soil moisture for agricultural drought (select 1–2).
8. FAO. GAUL administrative boundaries.

---

## Figure list (files in `results/figures/`)

1. ADEWI vs NDVI time series  
2. Component Z-scores, Eastern Province  
3. Lead time by event  
4. Drought-class timeline  
5–6. ADEWI maps for key dates  
7. ADEWI vs NDVI scatter  
8. ADEWI during known dry periods  
9. Lead-time distribution (boxplots)

## Table list (`results/tables/`)

1. Data quality  
2. Lead-time events  
3. Lead-time summary  
4. Known-period validation  
5. Crop correlation (only with official statistics)
