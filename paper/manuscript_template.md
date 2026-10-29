# Development of a Satellite-Based Agricultural Drought Early-Warning Index for Rwanda: Assessing Lead Time of Combined Vegetation, Rainfall and Soil Moisture Anomalies in the Eastern and Southern Provinces

<!-- RJAS submission template · target word count: 4,000–7,000 words (body only) -->
<!-- Replace all [PLACEHOLDER] blocks with verified observational results.        -->
<!-- Never submit values generated from the synthetic test dataset.               -->

**Authors:** [Author Name(s)]  
**Affiliation:** [Institution / School name]  
**Corresponding author:** [email]  
**Target journal:** Rwanda Journal of Agricultural Sciences (RJAS)  
**Submitted:** [Date]

---

## Abstract

<!-- 200–300 words. Summarise: background, objective, data, methods, key results, conclusion. -->

Agricultural drought threatens food security across Rwanda, particularly in the
Eastern and Southern Provinces where rain-fed smallholder farming predominates.
Conventional vegetation-based drought indicators — most notably the Normalized
Difference Vegetation Index (NDVI) — detect water stress only after crop damage
has become visible, limiting early intervention.

This study developed a satellite-based Agricultural Drought Early-Warning Index
(ADEWI) that combines standardized anomalies of rainfall (CHIRPS), soil moisture
(FLDAS), and land-surface temperature (MODIS MOD11A2) for the Eastern and Southern
Provinces of Rwanda over the period 2018–2024. The central objective was to
determine whether ADEWI crosses a drought detection threshold (Z-score ≤ −1.0)
earlier than vegetation-based indicators (NDVI and EVI from MODIS MOD13Q1).

A complementary Combined Agricultural Drought Index (CADI) incorporating all five
variables was constructed for status monitoring. Lead time was measured as the
difference in weeks between the ADEWI and NDVI event onsets across
[NUMBER]-identified drought events.

Results showed that ADEWI detected drought conditions an average of [MEAN_LEAD]
weeks (median: [MEDIAN_LEAD] weeks) ahead of NDVI onset, with a detection success
rate of [SUCCESS_RATE]%. Lead times were longest during [SEASON] events and highest
in the Eastern Province. ADEWI showed [DETECTION] out of [TOTAL] events across both
provinces and produced a false-alarm rate of [FA_RATE]%.

These findings suggest that a simple, transparent, and fully open-data index can
improve agricultural drought early warning in Rwanda by [3–6] weeks on average,
supporting climate-resilient farming and food security planning at provincial and
district levels.

**Keywords:** agricultural drought, early warning, NDVI, ADEWI, CADI, Rwanda,
satellite remote sensing, CHIRPS, MODIS, soil moisture, lead time

---

## 1. Introduction

<!-- 600–800 words. Problem statement → gap in literature → study objective. -->

Agricultural drought is defined as a period in which soil water availability falls
below the levels required for normal crop growth, leading to reduced yields and
food insecurity (FAO, [YEAR]). In sub-Saharan Africa, rain-fed agriculture accounts
for more than 95% of cultivated area (IPCC, [YEAR]), making smallholder farmers
acutely vulnerable to rainfall variability and drought.

Rwanda relies almost entirely on rain-fed agriculture, with two main growing seasons
(Season A: September–January; Season B: February–June) governing the production of
staple crops including maize (*Zea mays*) and beans (*Phaseolus vulgaris*). The Eastern
and Southern Provinces have experienced recurrent dry spells and below-normal rainfall
events in recent years, including documented droughts in 2016–17, 2021–22, and 2023
(MINAGRI, [YEAR]; NISR, [YEAR]).

Despite the availability of free satellite data from platforms such as Google Earth
Engine (GEE) and Digital Earth Africa (DE Africa), drought monitoring in Rwanda still
relies predominantly on vegetation indices such as the NDVI and the Vegetation Health
Index (VHI). While effective at quantifying vegetation stress, these indicators respond
only after crop damage has already occurred — typically several weeks after the onset
of rainfall deficits and soil moisture depletion (Kogan, 1995; Sheffield et al., 2014).
This temporal lag limits the window for early intervention by farmers, extension officers,
and decision-makers.

Several multi-variable drought indices have been developed for sub-Saharan Africa
(e.g., Nicholson et al., [YEAR]; [add 2-3 more references]), but few have been
specifically tailored to Rwanda's bimodal rainfall regime and provincial administrative
boundaries. A recent study by [CITE 2024 Rwanda SPEI+VHI paper] assessed drought
trends in Rwanda using SPEI and VHI but did not explicitly quantify lead time between
early warning signals and vegetation stress.

This study therefore developed the Agricultural Drought Early-Warning Index (ADEWI)
— a weighted combination of rainfall, soil moisture, and land-surface temperature
anomalies that deliberately excludes vegetation to maximize the temporal separation
between early warning and observed crop stress. The study addresses the following
research question:

> **Can ADEWI, a vegetation-independent multi-variable index, detect agricultural
> drought conditions earlier than NDVI-based indicators in Eastern and Southern Rwanda,
> and if so, by how many weeks?**

Specific objectives were to:
1. Download and process satellite and climate data for Eastern and Southern Rwanda (2018–2024).
2. Calculate standardized anomalies for five environmental variables.
3. Construct ADEWI and CADI.
4. Measure the lead time (weeks) by which ADEWI detects drought before NDVI.
5. Validate results against documented drought years and available crop-production statistics.
6. Assess performance differences between the Eastern and Southern Provinces.

---

## 2. Study Area

<!-- 200–300 words. + 1 study-area map. -->

The study was conducted in the Eastern Province (*Province de l'Est*) and Southern
Province (*Province du Sud*) of Rwanda (Figure 1). Together these provinces cover
approximately [AREA] km² and support approximately [POPULATION] of Rwanda's rural
agricultural population (NISR, [YEAR]).

The Eastern Province is characterized by savanna landscapes, lower and more variable
annual rainfall (700–900 mm/year), and is considered the most drought-prone region of
Rwanda. The Southern Province receives higher rainfall (900–1,200 mm/year) and has
more diverse agro-ecological zones. Both provinces rely primarily on Season A and
Season B for maize and bean production.

<!-- Insert Figure 1 here: Study area map showing Eastern and Southern Provinces,
     district boundaries, elevation, and main agro-ecological zones. -->

**Figure 1.** Study area: Eastern Province and Southern Province of Rwanda, showing
district boundaries, main agro-ecological zones, and the 2018–2024 study period
coverage of the satellite datasets used.

---

## 3. Data and Methods

### 3.1 Satellite and Climate Datasets

Five environmental variables were obtained from freely available satellite and
climate datasets for the period January 2018 – December 2024 (Table 1).

**Table 1.** Environmental datasets used in the study.

| Variable | Dataset | Spatial resolution | Temporal resolution | Platform |
|---|---|---|---|---|
| NDVI | MODIS MOD13Q1 v061 | 250 m | 16-day | Google Earth Engine |
| EVI | MODIS MOD13Q1 v061 | 250 m | 16-day | Google Earth Engine |
| Rainfall | CHIRPS v2.0 | ≈ 5 km | Pentad (5-day) | GEE / Digital Earth Africa |
| Soil moisture | FLDAS NOAH01 | 10 km | Monthly | Google Earth Engine |
| LST (daytime) | MODIS MOD11A2 v061 | 1 km | 8-day | Google Earth Engine |

All datasets were aggregated to 16-day composites to match the MODIS NDVI/EVI
temporal resolution. Provincial mean time series were extracted for the Eastern and
Southern Provinces using administrative boundaries from [HDX / geoBoundaries].
Cloud-contaminated and low-quality retrievals were excluded using product-specific
quality flags prior to aggregation. Approximately [85–90]% of composites passed
quality control for both provinces.

### 3.2 Standardized Anomalies (Z-scores)

Each variable was converted to a standardized anomaly (Z-score) relative to the
2018–2024 climatology:

$$Z_t = \frac{X_t - \mu_{doy}}{\sigma_{doy}}$$

where $X_t$ is the observed value at time $t$, $\mu_{doy}$ and $\sigma_{doy}$ are
the long-term mean and standard deviation for the same day-of-year bin (16-day),
computed separately for each province. Seasonal means were used rather than annual
means to remove the bimodal rainfall cycle before drought detection.

For rainfall and soil moisture, negative Z-scores indicate drier-than-normal
conditions. For NDVI and EVI, negative Z-scores indicate below-normal greenness.
For LST, positive Z-scores indicate above-normal surface temperatures.

### 3.3 Agricultural Drought Early-Warning Index (ADEWI)

ADEWI was constructed by combining the rainfall, soil moisture, and LST anomalies
using fixed weights:

$$\text{ADEWI} = 0.40 \cdot Z_{\text{rain}} + 0.35 \cdot Z_{\text{SM}} - 0.25 \cdot Z_{\text{LST}}$$

Rainfall received the highest weight (0.40) as the primary driver of agricultural
water availability in Rwanda. Soil moisture (0.35) reflects short-term water storage
available to crops. LST (0.25) captures thermal stress and is subtracted because
unusually high surface temperatures accompany drought stress (high $Z_{\text{LST}}$
therefore reduces ADEWI). Vegetation variables were deliberately excluded from ADEWI
to preserve independence between the early warning signal and the reference indicator
(NDVI).

Negative ADEWI values indicate drought-favourable conditions. The proposed sensitivity
of the chosen weights was assessed in Section 3.6.

### 3.4 Combined Agricultural Drought Index (CADI)

CADI incorporates all five variables and serves as a comprehensive drought status index:

$$\text{CADI} = 0.30 \cdot Z_{\text{NDVI}} + 0.15 \cdot Z_{\text{EVI}} + 0.30 \cdot Z_{\text{rain}} + 0.20 \cdot Z_{\text{SM}} - 0.20 \cdot Z_{\text{LST}}$$

Unlike ADEWI, CADI is not suitable as the early warning indicator because it
incorporates vegetation. It is used here to characterize the overall drought status
when vegetation has responded.

### 3.5 Drought Classification

Both indices were classified using the thresholds:

**Table 2.** Drought classification thresholds applied to ADEWI and CADI.

| Index value | Drought class |
|---|---|
| ≥ −0.5 | Normal |
| −0.5 to −1.0 | Mild |
| −1.0 to −1.5 | Moderate |
| −1.5 to −2.0 | Severe |
| < −2.0 | Extreme |

### 3.6 Lead-Time Analysis

An NDVI drought event was defined as a sustained period of two or more consecutive
16-day composites with $Z_{\text{NDVI}} \leq -1.0$. For each such event, the analysis
searched backward up to 12 composites (approximately 6 months) for the first ADEWI
crossing of the same threshold (−1.0). Lead time was calculated as:

$$L = t_{\text{NDVI onset}} - t_{\text{ADEWI onset}}$$

expressed in weeks. Positive values indicate ADEWI signalled earlier; zero indicates
simultaneous detection; negative values indicate ADEWI was slower. A detection
success rate was calculated as the fraction of NDVI events preceded by a qualifying
ADEWI signal.

To assess false alarms, ADEWI events not followed by an NDVI drought onset within
eight subsequent composites (≈ 4 months) were counted as false alarms. Lead times
were also stratified by Rwanda agricultural season (Season A: September–January;
Season B: February–June; Season C: July–August).

### 3.7 Validation

Results were validated against three documented drought episodes: the 2022 Season A
dry spell, the 2023 Eastern Province dry conditions, and the 2018 mid-season dry
period. Index values were compared with published NISR Seasonal Agricultural Survey
crop-production statistics for maize and beans where available.

### 3.8 Sensitivity Analysis

To evaluate robustness, seven weight combinations for ADEWI were tested (Table S1 in
Supplementary Material), including equal weights, leave-one-variable-out scenarios,
and rainfall-dominant and soil-moisture-dominant configurations. Mean lead time and
success rate were compared across scenarios.

---

## 4. Results

<!-- 1,200–1,800 words. Replace all [PLACEHOLDER] values. -->

### 4.1 Standardized Anomaly Time Series

Figure 2 shows the standardized anomalies for rainfall, soil moisture, LST, and NDVI
for the Eastern Province over 2018–2024. [DESCRIBE KEY PATTERNS: which years showed
the largest deficits, how LST co-varied with soil moisture, etc.]

<!-- Insert Figure 2 here (fig02_component_anomalies_eastern.png). -->

**Figure 2.** Standardized anomalies of ADEWI component variables (rainfall, soil
moisture, LST, and NDVI) for the Eastern Province of Rwanda, 2018–2024. Shaded
areas indicate periods with below-normal values. Dashed horizontal line marks
Z = −1.0.

### 4.2 ADEWI and CADI Time Series

Figure 3 presents the ADEWI and NDVI standardized anomaly time series for both
provinces. [DESCRIBE temporal patterns, drought events identified, and differences
between provinces.]

<!-- Insert Figure 3 here (fig01_adewi_ndvi_timeseries.png). -->

Figure 4 shows ADEWI alongside CADI and NDVI for the Eastern Province, illustrating
the temporal separation between the early-warning signal (ADEWI) and the vegetation
response (NDVI, CADI).

<!-- Insert Figure 4 here (fig11_cadi_vs_adewi.png). -->

**Figure 4.** ADEWI, CADI, and NDVI standardized anomaly for the Eastern Province
(2018–2024). ADEWI is expected to cross −1.0 earlier than NDVI during drought events.

### 4.3 Lead-Time Analysis

A total of [N] NDVI drought events were identified across both provinces.
Table 3 presents the lead-time summary.

**Table 3.** ADEWI lead-time summary by province.

<!-- Replace with verified table (table_lead_time_summary.csv). -->

| Province | NDVI events | Detected | Success rate | Mean lead (wk) | Median lead (wk) | Max lead (wk) |
|---|---|---|---|---|---|---|
| Eastern | [N] | [N] | [%] | [X.X] | [X.X] | [X.X] |
| Southern | [N] | [N] | [%] | [X.X] | [X.X] | [X.X] |
| **Combined** | **[N]** | **[N]** | **[%]** | **[X.X]** | **[X.X]** | **[X.X]** |

Figure 5 shows the lead time for each detected event. [DESCRIBE which events had
the longest lead times and any patterns.]

<!-- Insert Figure 5 here (fig03_lead_time_by_event.png). -->

Table 4 shows lead-time results stratified by agricultural season.

**Table 4.** ADEWI lead times by Rwanda growing season (A / B / C).

<!-- Replace with verified table (table_seasonal_lead_time.csv). -->

| Season | Events | Detected | Success rate | Mean lead (wk) |
|---|---|---|---|---|
| A (Sep–Jan) | [N] | [N] | [%] | [X.X] |
| B (Feb–Jun) | [N] | [N] | [%] | [X.X] |
| C (Jul–Aug) | [N] | [N] | [%] | [X.X] |

### 4.4 False-Alarm Analysis

ADEWI produced [N] early-warning events in total. Of these, [N] ([%]) were not
followed by a qualifying NDVI drought event within the forward search window,
giving an overall false-alarm rate of [%].

### 4.5 Validation Against Documented Drought Periods

Table 5 summarises ADEWI behaviour during the three documented drought episodes.

**Table 5.** ADEWI statistics during documented drought periods.

<!-- Replace with verified table (table_known_drought_validation.csv). -->

| Period | Min ADEWI | Mean ADEWI | Fraction below −1.0 | ADEWI detected? |
|---|---|---|---|---|
| 2022 Season A dry spell | [X.X] | [X.X] | [%] | [Yes/No] |
| 2023 Eastern dry conditions | [X.X] | [X.X] | [%] | [Yes/No] |
| 2018 mid-season dry period | [X.X] | [X.X] | [%] | [Yes/No] |

[DESCRIBE which periods were correctly identified and any mismatches.]

<!-- Insert Figure 6 here (fig08_validation_known_periods.png). -->

### 4.6 Province Comparison

Figure 7 compares ADEWI drought signals between the Eastern and Southern Provinces.
[DESCRIBE which province showed stronger signals, more events, longer lead times.]

<!-- Insert Figure 7 here (fig10_province_comparison.png). -->

---

## 5. Discussion

<!-- 800–1,200 words. -->

### 5.1 Lead-Time Performance

The observed mean lead time of [X.X] weeks [is consistent with / exceeds / falls
short of] the 3–6 week target proposed in the research brief. [INTERPRET: what does
this mean for practical early warning? How does it compare with similar studies?]

The highest lead times occurred during [SEASON] events in the [Eastern / Southern]
Province. This may reflect [POSSIBLE EXPLANATION: e.g., the rapid response of CHIRPS
rainfall anomalies to the onset of seasonal rainfall deficits before vegetation
responds].

### 5.2 False Alarms and Missed Events

A false-alarm rate of [%] indicates that approximately [1 in N] ADEWI threshold
crossings were not followed by a vegetation stress response. [INTERPRET: is this
acceptable? What conditions might trigger an ADEWI signal without a vegetation
response (e.g., brief dry spells outside the main cropping season)?]

[N] NDVI drought events ([%]) were not preceded by a qualifying ADEWI signal.
[INTERPRET: what conditions might cause NDVI to drop without prior ADEWI changes?
e.g., localized pest damage, cloud-contamination, or rapidly developing events.]

### 5.3 EVI as a Complementary Indicator

Figure [N] shows the comparison between EVI and NDVI standardized anomalies. The
Pearson correlation between the two indices was [r_Eastern] (Eastern) and [r_Southern]
(Southern). [INTERPRET: does EVI add independent information, or is it largely
redundant with NDVI? Does this justify its weight in CADI?]

### 5.4 Sensitivity to Index Weights

Table S1 (Supplementary) shows lead-time results under seven weight scenarios.
[DESCRIBE: does the mean lead time vary substantially across scenarios? Which weight
configuration performs best? Does the equal-weight scenario perform similarly to the
default?]

### 5.5 Limitations

Several limitations should be noted:

- **Synthetic data:** [IF APPLICABLE — remove this point when using real data]
  The current analysis uses a synthetic test dataset. Observational results may
  differ and should be obtained before drawing conclusions.
- **Spatial aggregation:** Provincial mean time series do not capture within-province
  spatial heterogeneity. A pixel-level drought map would provide more localized
  information.
- **Soil moisture product:** FLDAS provides monthly data at 10 km resolution, which
  may not capture rapid soil moisture changes between rainfall events.
- **Agricultural statistics:** Crop-production validation relied on [DESCRIBE source
  and any limitations].
- **Short record:** The 2018–2024 period contains [N] drought events, limiting the
  statistical robustness of lead-time estimates.
- **Index weights:** The default ADEWI weights (0.40/0.35/0.25) were based on
  physical reasoning rather than statistical optimisation against independent data.

---

## 6. Conclusions

<!-- 200–300 words. -->

This study developed and evaluated the Agricultural Drought Early-Warning Index
(ADEWI) for the Eastern and Southern Provinces of Rwanda using freely available
satellite and climate datasets for 2018–2024.

The key findings were:
1. ADEWI detected [N] out of [TOTAL] NDVI drought events (success rate: [%]).
2. The mean lead time was [X.X] weeks (median: [X.X] weeks), [meeting / exceeding /
   falling short of] the 3–6 week target.
3. Lead times were longest during [SEASON] and in the [Eastern / Southern] Province.
4. The false-alarm rate was [%], indicating that [INTERPRETATION].
5. Sensitivity analysis showed that lead-time results were [robust / sensitive] to
   the choice of index weights.

These results demonstrate that a simple, transparent, and fully open-data approach
can provide meaningful early warning of agricultural drought in Rwanda. The methodology
is reproducible using the Python analysis package accompanying this paper and does not
require specialized software or high-performance computing.

Future work should incorporate pixel-level analysis, higher-temporal-resolution soil
moisture products, and longer observational records to improve the statistical
robustness of lead-time estimates. Integration with Rwanda's existing early warning
systems and field validation with farmer reports would be important steps toward
operational deployment.

---

## Acknowledgements

The authors thank [NAME/INSTITUTION] for support. Data were obtained from Google Earth
Engine, the USGS MODIS archive, UCSB-CHG CHIRPS, NASA GSFC FLDAS, and [others].
Administrative boundaries were sourced from [HDX / geoBoundaries].

---

## References

<!-- Use the RJAS citation style. List all cited works here. -->

Kogan, F.N. (1995). Application of vegetation index and brightness temperature for
drought detection. *Advances in Space Research*, 15(11), 91–100.

Sheffield, J., Wood, E.F., & Roderick, M.L. (2014). Little change in global drought
over the past 60 years. *Nature*, 491(7424), 435–438.

[ADD ALL FURTHER REFERENCES — minimum 15–20 for RJAS]

---

## Supplementary Material

### Table S1. ADEWI sensitivity analysis results

<!-- Replace with verified table (table_sensitivity_analysis.csv). -->

| Scenario | w_rain | w_SM | w_LST | Events | Detected | Success rate | Mean lead (wk) |
|---|---|---|---|---|---|---|---|
| Default (0.40/0.35/0.25) | 0.40 | 0.35 | 0.25 | [N] | [N] | [%] | [X.X] |
| Equal weight (1/3 each) | 0.33 | 0.33 | 0.33 | [N] | [N] | [%] | [X.X] |
| Leave-out rainfall | 0.00 | 0.58 | 0.42 | [N] | [N] | [%] | [X.X] |
| Leave-out soil moisture | 0.62 | 0.00 | 0.38 | [N] | [N] | [%] | [X.X] |
| Leave-out LST | 0.53 | 0.47 | 0.00 | [N] | [N] | [%] | [X.X] |
| Rainfall-dominant | 0.60 | 0.30 | 0.10 | [N] | [N] | [%] | [X.X] |
| Soil-moisture-dominant | 0.25 | 0.60 | 0.15 | [N] | [N] | [%] | [X.X] |

### Data availability

All analysis code is available at: [GitHub repository URL]

The following datasets were used:
- MODIS MOD13Q1 v061 (DOI / citation)
- CHIRPS v2.0 (citation)
- FLDAS NOAH01 (citation)
- MODIS MOD11A2 v061 (citation)
- Administrative boundaries: [source and citation]
- Crop statistics: [NISR citation — replace placeholder]
