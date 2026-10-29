"""ADEWI Rwanda – Interactive Drought Early-Warning Explorer.

This Streamlit application provides an exploratory interface for the
Agricultural Drought Early-Warning Index (ADEWI) and Combined Agricultural
Drought Index (CADI) results for Eastern and Southern Rwanda (2018–2024).

⚠️  Research prototype only — NOT a validated operational warning service.

Tabs
----
1. Time Series    – Province / district / year filter; ADEWI + CADI + NDVI chart.
2. Lead-Time      – Per-event lead-time table, seasonal breakdown, KPI metrics.
3. Drought Map    – ADEWI drought-class colour strip and severity statistics.
4. Sensitivity    – Compare lead times under different index weight scenarios.
5. About          – Study metadata, data sources, and scientific disclaimers.

Usage
-----
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from adewi.config import load_config
from adewi.regions import DISTRICTS
from adewi.run_pipeline import run

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Rwanda ADEWI — Drought Early-Warning Explorer",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {background-color: #1a2535;}
    [data-testid="stSidebar"] * {color: #e8eaf6 !important;}
    .stMetric label {font-size: 0.78rem; color: #546e7a;}
    .stMetric [data-testid="stMetricValue"] {font-size: 1.45rem; font-weight: 700;}
    h1 {color: #1a2535; font-size: 1.6rem;}
    h2 {color: #2c3e50; font-size: 1.2rem;}
    .drought-badge {
        display: inline-block; padding: 2px 10px; border-radius: 12px;
        font-size: 0.82rem; font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Drought-class colour helpers
# ---------------------------------------------------------------------------

CLASS_COLORS = {
    "Extreme": "#6b0000",
    "Severe": "#c0392b",
    "Moderate": "#e67e22",
    "Mild": "#f1c40f",
    "Normal": "#2ecc71",
    "Missing": "#bdc3c7",
}

CLASS_ORDER = ["Extreme", "Severe", "Moderate", "Mild", "Normal"]


def badge(label: str) -> str:
    color = CLASS_COLORS.get(label, "#ccc")
    return f'<span class="drought-badge" style="background:{color};color:#fff">{label}</span>'


# ---------------------------------------------------------------------------
# Load / compute index
# ---------------------------------------------------------------------------

cfg = load_config()
index_path = Path(cfg["paths"]["data_processed"]) / "adewi_index_timeseries.csv"
events_path = Path(cfg["paths"]["tables"]) / "table_lead_time_events.csv"
summary_path = Path(cfg["paths"]["tables"]) / "table_lead_time_summary.csv"
seasonal_path = Path(cfg["paths"]["tables"]) / "table_seasonal_lead_time.csv"
fa_path = Path(cfg["paths"]["tables"]) / "table_false_alarms.csv"

if not index_path.exists():
    st.info("No processed index found. Running the analysis pipeline once…")
    with st.spinner("Computing ADEWI — this takes about 30 seconds…"):
        run()

index_df = pd.read_csv(index_path, parse_dates=["time"])

# Data-source warning banner
source = index_df["data_source"].iloc[0] if "data_source" in index_df.columns else "unknown"
if source == "synthetic":
    st.warning(
        "🔬 **Synthetic demonstration data active.** "
        "Export real observations from Google Earth Engine or Digital Earth Africa, "
        "save to `data/raw/provincial_timeseries.csv`, and re-run the pipeline "
        "before citing any results.",
        icon="⚠️",
    )

# ---------------------------------------------------------------------------
# Sidebar controls (shared across tabs)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🌿 Rwanda ADEWI")
    st.markdown(
        "**Agricultural Drought Early-Warning Index**  \n"
        "Eastern & Southern Provinces · 2018–2024"
    )
    st.divider()

    province = st.selectbox(
        "Province",
        sorted(index_df["province"].unique()),
        index=0,
        key="province_sel",
    )
    district_opts = ["All districts"] + DISTRICTS.get(province, [])
    district = st.selectbox("District (informational)", district_opts, key="district_sel")
    years = sorted(index_df["time"].dt.year.unique())
    year = st.selectbox(
        "Focus year", years,
        index=len(years) - 3 if len(years) >= 3 else 0,
        key="year_sel",
    )
    st.divider()
    drought_thr = st.slider(
        "Drought threshold", min_value=-3.0, max_value=-0.5,
        value=-1.0, step=0.1,
        help="Change the detection threshold for exploratory purposes only.",
    )
    st.caption(
        "Threshold used in the paper: −1.0  \n"
        "Slide to see how detection changes — does not alter saved results."
    )

# Filter helpers
prov_df = index_df[index_df["province"] == province].copy()
year_df = prov_df[prov_df["time"].dt.year == year].copy()

# ---------------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------------

st.title("Agricultural Drought Early-Warning Index — Rwanda")
col_h1, col_h2, col_h3 = st.columns(3)
worst_class = year_df.loc[year_df["adewi"].idxmin(), "adewi_class"] if len(year_df) else "—"
col_h1.metric("Province", province)
col_h2.metric("Year in focus", str(year))
col_h3.markdown(f"**Worst ADEWI class ({year}):** {badge(worst_class)}", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------

tab_ts, tab_lt, tab_map, tab_sens, tab_about = st.tabs(
    ["📈 Time Series", "⏱️ Lead-Time Analysis", "🗺️ Drought Map", "⚙️ Sensitivity", "ℹ️ About"]
)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — Time Series
# ═══════════════════════════════════════════════════════════════════════════

with tab_ts:
    st.subheader(f"{province} Province — ADEWI · CADI · NDVI over time")

    series_opts = st.multiselect(
        "Show series",
        ["adewi", "cadi", "z_ndvi", "z_evi", "z_rainfall", "z_soil_moisture", "z_lst"],
        default=["adewi", "cadi", "z_ndvi"],
        key="series_sel",
    )

    SERIES_LABELS = {
        "adewi": "ADEWI",
        "cadi": "CADI",
        "z_ndvi": "NDVI Z-score",
        "z_evi": "EVI Z-score",
        "z_rainfall": "Rainfall Z-score",
        "z_soil_moisture": "Soil moisture Z-score",
        "z_lst": "LST Z-score",
    }
    SERIES_COLORS = {
        "adewi": "#e74c3c",
        "cadi": "#8e44ad",
        "z_ndvi": "#27ae60",
        "z_evi": "#1abc9c",
        "z_rainfall": "#2980b9",
        "z_soil_moisture": "#16a085",
        "z_lst": "#e67e22",
    }
    SERIES_DASH = {
        "adewi": "solid",
        "cadi": "dash",
        "z_ndvi": "dot",
        "z_evi": "dot",
        "z_rainfall": "solid",
        "z_soil_moisture": "solid",
        "z_lst": "solid",
    }

    fig_ts = go.Figure()
    for s in series_opts:
        if s in prov_df.columns:
            fig_ts.add_trace(go.Scatter(
                x=prov_df["time"], y=prov_df[s],
                name=SERIES_LABELS.get(s, s),
                line=dict(color=SERIES_COLORS.get(s, "#333"), dash=SERIES_DASH.get(s, "solid"), width=1.8),
                opacity=0.9,
            ))
    fig_ts.add_hline(
        y=drought_thr, line_dash="dash", line_color="black",
        annotation_text=f"Threshold ({drought_thr})",
        annotation_position="bottom right",
    )
    fig_ts.add_vrect(
        x0=f"{year}-01-01", x1=f"{year}-12-31",
        fillcolor="rgba(52,152,219,0.08)", layer="below",
        annotation_text=str(year), annotation_position="top left",
    )
    fig_ts.update_layout(
        title=f"{province} Province — Drought Index Time Series 2018–2024",
        xaxis_title="Date",
        yaxis_title="Standardized anomaly",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(t=80),
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    # Yearly summary table
    st.markdown(f"**Data for selected year ({year})**")
    display_cols = ["time", "adewi", "adewi_class", "cadi", "cadi_class",
                    "z_ndvi", "ndvi_class", "z_rainfall", "z_soil_moisture", "z_lst"]
    display_cols = [c for c in display_cols if c in year_df.columns]
    st.dataframe(
        year_df[display_cols].rename(columns={"time": "Date"}),
        use_container_width=True, hide_index=True,
    )

    # KPI strip for selected year
    if len(year_df):
        st.divider()
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Mean ADEWI", f"{year_df['adewi'].mean():.2f}")
        k2.metric("Min ADEWI", f"{year_df['adewi'].min():.2f}")
        if "cadi" in year_df.columns:
            k3.metric("Mean CADI", f"{year_df['cadi'].mean():.2f}")
            k4.metric("Min CADI", f"{year_df['cadi'].min():.2f}")
        drought_frac = (year_df["adewi"] <= drought_thr).mean()
        k5.metric("Drought fraction", f"{drought_frac:.0%}")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — Lead-Time Analysis
# ═══════════════════════════════════════════════════════════════════════════

with tab_lt:
    st.subheader("ADEWI lead time ahead of NDVI drought onset")

    # KPIs from summary table
    if summary_path.exists():
        sm = pd.read_csv(summary_path)
        overall = sm[sm["province"] == "Eastern+Southern"]
        prov_row = sm[sm["province"] == province]

        kk1, kk2, kk3, kk4 = st.columns(4)
        if len(overall):
            kk1.metric("Mean lead (pooled)", f"{overall['mean_lead_weeks'].iloc[0]:.1f} wk")
            kk2.metric("Median lead (pooled)", f"{overall['median_lead_weeks'].iloc[0]:.1f} wk")
            kk3.metric("Success rate (pooled)", f"{overall['success_rate'].iloc[0]:.0%}")
            kk4.metric("NDVI events detected", f"{int(overall['n_detected'].iloc[0])} / {int(overall['n_ndvi_events'].iloc[0])}")
        if len(prov_row):
            st.caption(
                f"**{province}:** mean lead = {prov_row['mean_lead_weeks'].iloc[0]:.1f} wk · "
                f"success rate = {prov_row['success_rate'].iloc[0]:.0%}"
            )

    col_ev, col_ss = st.columns([3, 2])
    with col_ev:
        st.markdown("**Per-event lead times**")
        if events_path.exists():
            ev = pd.read_csv(events_path, parse_dates=["ndvi_onset", "ndvi_end", "adewi_onset"])
            pev = ev[ev["province"] == province] if "province" in ev.columns else ev
            if not pev.empty:
                fig_bars = px.bar(
                    pev[pev["detected"]], y="lead_weeks",
                    x=pev[pev["detected"]]["ndvi_onset"].dt.strftime("%Y-%m"),
                    color_discrete_sequence=["#c0392b"],
                    labels={"x": "NDVI onset", "lead_weeks": "Lead (weeks)"},
                    title=f"{province} — lead time per event",
                )
                fig_bars.add_hline(
                    y=pev[pev["detected"]]["lead_weeks"].mean() if pev["detected"].any() else 0,
                    line_dash="dash", annotation_text="Mean",
                )
                st.plotly_chart(fig_bars, use_container_width=True)
            st.dataframe(pev, use_container_width=True, hide_index=True)

    with col_ss:
        st.markdown("**Seasonal breakdown (A / B / C)**")
        if seasonal_path.exists():
            sea = pd.read_csv(seasonal_path)
            st.dataframe(sea, use_container_width=True, hide_index=True)
            if "mean_lead_weeks" in sea.columns and not sea["mean_lead_weeks"].isna().all():
                fig_sea = px.bar(
                    sea.dropna(subset=["mean_lead_weeks"]),
                    x="season", y="mean_lead_weeks",
                    color="season",
                    color_discrete_map={"A": "#2980b9", "B": "#27ae60", "C": "#e67e22"},
                    labels={"mean_lead_weeks": "Mean lead (wk)", "season": "Season"},
                    title="Mean lead time by season",
                )
                st.plotly_chart(fig_sea, use_container_width=True)

    # False-alarm summary
    if fa_path.exists():
        fa_df = pd.read_csv(fa_path, parse_dates=["adewi_onset"])
        st.divider()
        st.markdown("**False-alarm analysis** (ADEWI events with no matching NDVI response)")
        fa_prov = fa_df[fa_df["province"] == province] if "province" in fa_df.columns else fa_df
        if not fa_prov.empty:
            fa_rate = fa_prov["false_alarm"].mean()
            fa1, fa2 = st.columns(2)
            fa1.metric("False-alarm rate", f"{fa_rate:.0%}")
            fa2.metric("Total ADEWI events", len(fa_prov))
            st.dataframe(fa_prov, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — Drought Map (timeline strip)
# ═══════════════════════════════════════════════════════════════════════════

with tab_map:
    st.subheader("ADEWI drought severity through time")

    sel_index = st.radio(
        "Index to visualise",
        ["adewi", "cadi", "z_ndvi"],
        horizontal=True,
        format_func=lambda x: {"adewi": "ADEWI", "cadi": "CADI", "z_ndvi": "NDVI Z"}[x],
    )
    col_class = sel_index.replace("z_", "") + "_class" if sel_index.startswith("z_") else sel_index + "_class"
    if col_class not in prov_df.columns:
        col_class = "adewi_class"

    # Heatmap using plotly
    strip_df = prov_df[["time", sel_index, col_class]].copy()
    strip_df["y"] = province
    strip_df["month_label"] = strip_df["time"].dt.strftime("%Y-%m")

    fig_heat = px.scatter(
        strip_df, x="time", y="y",
        color=col_class,
        color_discrete_map=CLASS_COLORS,
        category_orders={col_class: CLASS_ORDER + ["Missing"]},
        hover_data={sel_index: ":.2f", "month_label": True, "y": False},
        height=180,
        title=f"{province} Province — {sel_index.upper()} drought severity",
    )
    fig_heat.update_traces(marker=dict(size=12, symbol="square"))
    fig_heat.update_layout(
        yaxis_title="", xaxis_title="",
        showlegend=True,
        legend_title="Drought class",
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Class frequency table
    st.markdown("**Class frequency (all years)**")
    freq = prov_df[col_class].value_counts().reindex(CLASS_ORDER).dropna().reset_index()
    freq.columns = ["Drought class", "Count"]
    freq["Share (%)"] = (freq["Count"] / freq["Count"].sum() * 100).round(1)
    st.dataframe(freq, use_container_width=True, hide_index=True)

    # Both provinces side-by-side
    st.divider()
    st.markdown("**Both provinces — annual drought fraction (ADEWI ≤ threshold)**")
    ann = (
        index_df.assign(drought=(index_df["adewi"] <= drought_thr))
        .groupby(["province", index_df["time"].dt.year])["drought"]
        .mean()
        .reset_index()
    )
    ann.columns = ["Province", "Year", "Drought fraction"]
    fig_ann = px.bar(
        ann, x="Year", y="Drought fraction", color="Province",
        barmode="group",
        color_discrete_map={"Eastern": "#c0392b", "Southern": "#2980b9"},
        title="Annual drought fraction (ADEWI) by province",
    )
    st.plotly_chart(fig_ann, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — Sensitivity
# ═══════════════════════════════════════════════════════════════════════════

with tab_sens:
    st.subheader("Index weight sensitivity analysis")
    st.info(
        "Select custom weights for ADEWI and click **Run scenario** to see how "
        "lead-time results change. This does not overwrite the saved results.",
        icon="ℹ️",
    )

    col_w1, col_w2, col_w3 = st.columns(3)
    w_rain = col_w1.slider("w_rainfall", 0.0, 1.0, 0.40, 0.05)
    w_sm = col_w2.slider("w_soil_moisture", 0.0, 1.0, 0.35, 0.05)
    w_lst = col_w3.slider("w_lst", 0.0, 1.0, 0.25, 0.05)
    total_w = w_rain + w_sm + w_lst
    st.caption(f"Weight total: **{total_w:.2f}** (does not need to sum to 1.0)")

    if st.button("▶ Run scenario", key="sens_run"):
        with st.spinner("Running custom scenario…"):
            from adewi.anomalies import compute_anomalies as _ca
            from adewi.combined_index import compute_indices as _ci
            from adewi.lead_time import analyze_lead_time as _lt
            from adewi.preprocessing import preprocess as _pre
            from adewi.data_loading import load_provincial_timeseries as _dl
            import copy

            _cfg = load_config()
            _cfg_local = copy.deepcopy(_cfg)
            _cfg_local["weights"]["adewi"] = {
                "rainfall": w_rain, "soil_moisture": w_sm, "lst": w_lst,
            }
            _raw, _ = _dl(_cfg_local)
            _clean, _ = _pre(_raw)
            _zdf, _ = _ca(_clean)
            _idx = _ci(_zdf, _cfg_local)
            _, _summary = _lt(_idx, _cfg_local)
            st.markdown("**Scenario lead-time summary:**")
            st.dataframe(_summary, use_container_width=True, hide_index=True)

    # Show pre-computed sensitivity table if it exists
    sens_path = Path(cfg["paths"]["tables"]) / "table_sensitivity_analysis.csv"
    if sens_path.exists():
        st.divider()
        st.markdown("**Pre-computed sensitivity table** (from `scripts/sensitivity_analysis.py`)")
        st.dataframe(pd.read_csv(sens_path), use_container_width=True, hide_index=True)
    else:
        st.caption(
            "Run `python scripts/sensitivity_analysis.py` to generate a full "
            "multi-scenario comparison table."
        )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 — About
# ═══════════════════════════════════════════════════════════════════════════

with tab_about:
    st.subheader("About this study")
    st.markdown(
        """
**Title:** Development of a Satellite-Based Agricultural Drought Early-Warning Index
for Rwanda: Assessing Lead Time of Combined Vegetation, Rainfall and Soil Moisture
Anomalies in the Eastern and Southern Provinces

**Target journal:** Rwanda Journal of Agricultural Sciences (RJAS)

**Study area:** Eastern Province and Southern Province, Rwanda

**Study period:** January 2018 – December 2024

**Research question:** Can a multi-variable index based on rainfall, soil moisture,
and land-surface temperature anomalies detect agricultural drought earlier than
vegetation-based indicators in Eastern and Southern Rwanda?

---

### Index formulas

| Index | Formula |
|-------|---------|
| **ADEWI** | `0.40 · Z(rain) + 0.35 · Z(SM) − 0.25 · Z(LST)` |
| **CADI** | `0.30 · Z(NDVI) + 0.15 · Z(EVI) + 0.30 · Z(rain) + 0.20 · Z(SM) − 0.20 · Z(LST)` |

ADEWI is **vegetation-independent** so its signal can be compared with NDVI
without circularity.

### Drought classification
| Value | Class |
|-------|-------|
| ≥ −0.5 | Normal |
| −0.5 to −1.0 | Mild |
| −1.0 to −1.5 | Moderate |
| −1.5 to −2.0 | Severe |
| < −2.0 | Extreme |

### Data sources

| Variable | Dataset | Platform |
|----------|---------|---------|
| NDVI / EVI | MODIS MOD13Q1 (250 m, 16-day) | Google Earth Engine |
| Rainfall | CHIRPS v2.0 (5 km, pentad) | GEE / Digital Earth Africa |
| Soil moisture | FLDAS or ESA CCI | GEE / Copernicus |
| LST | MODIS MOD11A2 (1 km, 8-day) | GEE |

---

### Disclaimers

* **Synthetic data warning:** until real GEE / DE Africa exports are loaded,
  all outputs are from a synthetic test generator and **must not be reported
  as observational findings**.
* **Operational readiness:** this application is a research prototype and has
  NOT been validated as an operational early-warning service.
* **Crop statistics:** the placeholder crop file contains schematic values.
  Replace with official NISR / MINAGRI Seasonal Agricultural Survey data
  before conducting or reporting crop-production validation.
        """
    )
