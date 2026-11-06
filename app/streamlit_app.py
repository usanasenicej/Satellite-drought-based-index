"""ADEWI Rwanda – Interactive Drought Early-Warning Explorer.

This Streamlit application provides an exploratory interface for the
Agricultural Drought Early-Warning Index (ADEWI) and Combined Agricultural
Drought Index (CADI) results for Eastern and Southern Rwanda (2018–2024).

⚠️  Research prototype only — NOT a validated operational warning service.

Tabs
----
1. Time Series    – Province / district / year filter; ADEWI + CADI + NDVI chart & CSV export.
2. Lead-Time      – Per-event lead-time table, seasonal breakdown, KPI metrics & CSV export.
3. Drought Map    – Geospatial interactive district map, temporal strip & severity statistics.
4. Sensitivity    – Custom weight sliders, normalization check, and comparative scenario charts.
5. About          – Study metadata, index formulas, data sources, and scientific disclaimers.

Usage
-----
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from adewi.anomalies import compute_anomalies as _ca
from adewi.combined_index import compute_indices as _ci
from adewi.config import ensure_dirs, load_config
from adewi.data_loading import load_provincial_timeseries as _dl
from adewi.lead_time import analyze_lead_time as _lt
from adewi.preprocessing import preprocess as _pre
from adewi.regions import DISTRICT_CENTROIDS, DISTRICTS, load_district_table
from adewi.run_pipeline import run

# ---------------------------------------------------------------------------
# Page configuration & custom styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Rwanda ADEWI — Drought Early-Warning Explorer",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #1a2535;
    }
    [data-testid="stSidebar"] * {
        color: #e8eaf6 !important;
    }
    .stMetric label {
        font-size: 0.82rem;
        color: #546e7a;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.45rem;
        font-weight: 700;
    }
    .drought-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 700;
        color: #ffffff;
    }
    .district-card {
        background-color: #f8f9fa;
        border-left: 4px solid #2980b9;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Constants & Color Palette
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

SERIES_LABELS = {
    "adewi": "ADEWI (Early Warning)",
    "cadi": "CADI (Combined Status)",
    "z_ndvi": "NDVI Anomaly (Z-score)",
    "z_evi": "EVI Anomaly (Z-score)",
    "z_rainfall": "Rainfall Anomaly (Z-score)",
    "z_soil_moisture": "Soil Moisture Anomaly (Z-score)",
    "z_lst": "LST Anomaly (Z-score)",
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


def render_badge(label: str) -> str:
    """Return styled HTML pill for drought classification."""
    color = CLASS_COLORS.get(label, "#7f8c8d")
    return f'<span class="drought-badge" style="background:{color};">{label}</span>'


# ---------------------------------------------------------------------------
# Cached Data Loader
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_app_data() -> tuple[dict, pd.DataFrame]:
    """Load configuration and processed time-series, running pipeline if missing."""
    cfg_data = load_config()
    ensure_dirs(cfg_data)
    idx_path = Path(cfg_data["paths"]["data_processed"]) / "adewi_index_timeseries.csv"

    if not idx_path.exists():
        run()

    df = pd.read_csv(idx_path, parse_dates=["time"])
    return cfg_data, df


cfg, index_df = load_app_data()

# Data-source warning banner
data_source = index_df["data_source"].iloc[0] if "data_source" in index_df.columns else "unknown"
if data_source == "synthetic":
    st.warning(
        "🔬 **Synthetic demonstration data active.** "
        "Export observational time-series from Google Earth Engine or Digital Earth Africa to "
        "`data/raw/provincial_timeseries.csv` and re-run `adewi` before citing empirical findings.",
        icon="⚠️",
    )

# ---------------------------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🌿 Rwanda ADEWI")
    st.markdown(
        "**Agricultural Drought Early-Warning Index**  \n"
        "Eastern & Southern Provinces · 2018–2024"
    )
    st.divider()

    provinces = sorted(index_df["province"].unique())
    province = st.selectbox("Province", provinces, index=0, key="province_sel")

    district_options = ["All districts"] + DISTRICTS.get(province, [])
    district = st.selectbox(
        "District Explorer",
        district_options,
        key="district_sel",
        help="Select a district to inspect its coordinates and geographic focal location.",
    )

    available_years = sorted(index_df["time"].dt.year.unique())
    default_year_idx = len(available_years) - 3 if len(available_years) >= 3 else 0
    year = st.selectbox(
        "Focus Year",
        available_years,
        index=default_year_idx,
        key="year_sel",
    )

    st.divider()
    drought_thr = st.slider(
        "Drought threshold",
        min_value=-3.0,
        max_value=-0.5,
        value=-1.0,
        step=0.1,
        help="Defines the standardized anomaly cutoff below which conditions are classified as drought.",
    )
    st.caption("Standard operational threshold: **−1.0** (Moderate drought)")

# Filter data
prov_df = index_df[index_df["province"] == province].copy()
year_df = prov_df[prov_df["time"].dt.year == year].copy()

# ---------------------------------------------------------------------------
# Top Header Metrics
# ---------------------------------------------------------------------------

st.title("Agricultural Drought Early-Warning Index — Rwanda")

if district != "All districts" and district in DISTRICT_CENTROIDS:
    d_lat, d_lon = DISTRICT_CENTROIDS[district]
    st.markdown(
        f'<div class="district-card">'
        f'📍 <strong>District Context:</strong> {district} ({province} Province) — '
        f'Centroid: <code>{d_lat:.2f}° N, {d_lon:.2f}° E</code>. '
        f'Showing aggregate provincial observations and local spatial mapping below.'
        f'</div>',
        unsafe_allow_html=True,
    )

col_h1, col_h2, col_h3, col_h4 = st.columns(4)
worst_class = year_df.loc[year_df["adewi"].idxmin(), "adewi_class"] if len(year_df) else "Normal"
mean_adewi_val = year_df["adewi"].mean() if len(year_df) else 0.0
drought_fraction = (year_df["adewi"] <= drought_thr).mean() if len(year_df) else 0.0

col_h1.metric("Province", province)
col_h2.metric("Focus Year", str(year))
col_h3.metric("Annual Mean ADEWI", f"{mean_adewi_val:.2f}")
with col_h4:
    st.markdown(f"**Peak Drought Severity ({year}):**<br>{render_badge(worst_class)}", unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------------------------
# Application Tabs
# ---------------------------------------------------------------------------

tab_ts, tab_lt, tab_map, tab_sens, tab_about = st.tabs(
    [
        "📈 Time Series",
        "⏱️ Lead-Time Analysis",
        "🗺️ Drought Map & Spatial Explorer",
        "⚙️ Sensitivity Analysis",
        "ℹ️ About & Methodology",
    ]
)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — Time Series
# ═══════════════════════════════════════════════════════════════════════════

with tab_ts:
    st.subheader(f"{province} Province — Environmental Anomalies & Indices")

    col_ctrl1, col_ctrl2 = st.columns([3, 1])
    with col_ctrl1:
        series_opts = st.multiselect(
            "Select series to plot",
            list(SERIES_LABELS.keys()),
            default=["adewi", "cadi", "z_ndvi"],
            format_func=lambda s: SERIES_LABELS.get(s, s),
            key="series_sel",
        )
    with col_ctrl2:
        compare_prov = st.checkbox("Overlay both provinces (ADEWI)", value=False)

    fig_ts = go.Figure()

    if compare_prov:
        for p_name, p_color in [("Eastern", "#c0392b"), ("Southern", "#2980b9")]:
            p_data = index_df[index_df["province"] == p_name]
            fig_ts.add_trace(
                go.Scatter(
                    x=p_data["time"],
                    y=p_data["adewi"],
                    name=f"ADEWI ({p_name})",
                    line=dict(color=p_color, width=2.0),
                )
            )
    else:
        for s in series_opts:
            if s in prov_df.columns:
                fig_ts.add_trace(
                    go.Scatter(
                        x=prov_df["time"],
                        y=prov_df[s],
                        name=SERIES_LABELS.get(s, s),
                        line=dict(
                            color=SERIES_COLORS.get(s, "#333333"),
                            dash=SERIES_DASH.get(s, "solid"),
                            width=2.0 if s == "adewi" else 1.6,
                        ),
                        opacity=0.95,
                    )
                )

    fig_ts.add_hline(
        y=drought_thr,
        line_dash="dash",
        line_color="#2c3e50",
        annotation_text=f"Drought threshold ({drought_thr})",
        annotation_position="bottom right",
    )
    fig_ts.add_vrect(
        x0=f"{year}-01-01",
        x1=f"{year}-12-31",
        fillcolor="rgba(52, 152, 219, 0.08)",
        layer="below",
        annotation_text=f"Focus year: {year}",
        annotation_position="top left",
    )
    fig_ts.update_layout(
        title=f"{province} Province — Standardized Time Series (2018–2024)",
        xaxis_title="Date",
        yaxis_title="Standardized Anomaly (Z-score)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        margin=dict(t=80, b=40),
        template="plotly_white",
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    # Detailed Table & Download
    st.markdown(f"**Observations for {province} ({year})**")
    display_cols = [
        "time", "adewi", "adewi_class", "cadi", "cadi_class",
        "z_ndvi", "ndvi_class", "z_rainfall", "z_soil_moisture", "z_lst"
    ]
    display_cols = [c for c in display_cols if c in year_df.columns]
    tbl_display = year_df[display_cols].rename(columns={"time": "Date"}).copy()
    st.dataframe(tbl_display, use_container_width=True, hide_index=True)

    csv_data = year_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Download {province} {year} Data (CSV)",
        data=csv_data,
        file_name=f"adewi_{province.lower()}_{year}.csv",
        mime="text/csv",
    )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — Lead-Time Analysis
# ═══════════════════════════════════════════════════════════════════════════

with tab_lt:
    st.subheader("ADEWI Lead Time Ahead of NDVI Vegetation Drought")

    summary_path = Path(cfg["paths"]["tables"]) / "table_lead_time_summary.csv"
    events_path = Path(cfg["paths"]["tables"]) / "table_lead_time_events.csv"
    seasonal_path = Path(cfg["paths"]["tables"]) / "table_seasonal_lead_time.csv"
    fa_path = Path(cfg["paths"]["tables"]) / "table_false_alarms.csv"

    if summary_path.exists():
        sm = pd.read_csv(summary_path)
        overall = sm[sm["province"] == "Eastern+Southern"]
        prov_row = sm[sm["province"] == province]

        k1, k2, k3, k4 = st.columns(4)
        if len(overall):
            k1.metric("Mean Lead Time (Pooled)", f"{overall['mean_lead_weeks'].iloc[0]:.1f} weeks")
            k2.metric("Median Lead Time", f"{overall['median_lead_weeks'].iloc[0]:.1f} weeks")
            k3.metric("Detection Rate", f"{overall['success_rate'].iloc[0]:.0%}")
            k4.metric(
                "Events Detected",
                f"{int(overall['n_detected'].iloc[0])} / {int(overall['n_ndvi_events'].iloc[0])}",
            )

    st.write("")
    col_ev, col_ss = st.columns([3, 2])

    with col_ev:
        st.markdown(f"**Detected Drought Events in {province}**")
        if events_path.exists():
            ev = pd.read_csv(events_path, parse_dates=["ndvi_onset", "ndvi_end", "adewi_onset"])
            pev = ev[ev["province"] == province] if "province" in ev.columns else ev
            if not pev.empty:
                detected_events = pev[pev["detected"]].copy()
                if not detected_events.empty:
                    detected_events["onset_label"] = detected_events["ndvi_onset"].dt.strftime("%Y-%m")
                    fig_bars = px.bar(
                        detected_events,
                        x="onset_label",
                        y="lead_weeks",
                        color_discrete_sequence=["#e74c3c"],
                        labels={"onset_label": "NDVI Drought Onset", "lead_weeks": "Lead Time (Weeks)"},
                        title=f"{province} Province — Lead Time per Detected Event",
                    )
                    mean_val = detected_events["lead_weeks"].mean()
                    fig_bars.add_hline(
                        y=mean_val,
                        line_dash="dash",
                        line_color="#2c3e50",
                        annotation_text=f"Mean: {mean_val:.1f} wk",
                    )
                    fig_bars.update_layout(template="plotly_white", height=320)
                    st.plotly_chart(fig_bars, use_container_width=True)

                st.dataframe(pev, use_container_width=True, hide_index=True)

                csv_ev = pev.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"📥 Download {province} Lead-Time Events (CSV)",
                    data=csv_ev,
                    file_name=f"lead_time_events_{province.lower()}.csv",
                    mime="text/csv",
                )

    with col_ss:
        st.markdown("**Seasonal Breakdown (Season A, B, C)**")
        if seasonal_path.exists():
            sea = pd.read_csv(seasonal_path)
            st.dataframe(sea, use_container_width=True, hide_index=True)
            if "mean_lead_weeks" in sea.columns and not sea["mean_lead_weeks"].isna().all():
                fig_sea = px.bar(
                    sea.dropna(subset=["mean_lead_weeks"]),
                    x="season",
                    y="mean_lead_weeks",
                    color="season",
                    color_discrete_map={"A": "#2980b9", "B": "#27ae60", "C": "#e67e22"},
                    labels={"mean_lead_weeks": "Mean Lead (Weeks)", "season": "Agricultural Season"},
                    title="Mean Lead Time Across Rwandan Agricultural Seasons",
                )
                fig_sea.update_layout(template="plotly_white", height=320, showlegend=False)
                st.plotly_chart(fig_sea, use_container_width=True)

    if fa_path.exists():
        fa_df = pd.read_csv(fa_path, parse_dates=["adewi_onset"])
        st.divider()
        st.markdown("**False-Alarm Evaluation (ADEWI Alerts without Subsequent Vegetation Response)**")
        fa_prov = fa_df[fa_df["province"] == province] if "province" in fa_df.columns else fa_df
        if not fa_prov.empty:
            fa_rate = fa_prov["false_alarm"].mean()
            fa_col1, fa_col2 = st.columns(2)
            fa_col1.metric("False-Alarm Ratio", f"{fa_rate:.0%}")
            fa_col2.metric("Total ADEWI Signal Episodes", len(fa_prov))
            st.dataframe(fa_prov, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — Drought Map & Spatial Explorer
# ═══════════════════════════════════════════════════════════════════════════

with tab_map:
    st.subheader("Geographic & Temporal Drought Mapping")

    district_table = load_district_table()
    current_year_status = worst_class

    # Build district geographic dataframe
    district_table["worst_status"] = district_table["province"].map(
        lambda p: year_df.loc[year_df["adewi"].idxmin(), "adewi_class"]
        if p == province and len(year_df)
        else "Normal"
    )
    district_table["is_selected"] = district_table["district"] == district
    district_table["marker_size"] = np.where(district_table["is_selected"], 16, 10)

    st.markdown(
        f"**Study Districts Map — Eastern & Southern Rwanda ({year})**  \n"
        f"Districts are positioned by centroid coordinates and colored by current provincial drought classification."
    )

    fig_map = px.scatter_mapbox(
        district_table,
        lat="lat",
        lon="lon",
        hover_name="district",
        hover_data={"province": True, "lat": ":.2f", "lon": ":.2f", "marker_size": False},
        color="province",
        color_discrete_map={"Eastern": "#c0392b", "Southern": "#2980b9"},
        size="marker_size",
        size_max=16,
        zoom=7.8,
        center=dict(lat=-2.15, lon=30.05),
        mapbox_style="carto-positron",
        title=f"Districts of {province} & Southern/Eastern Rwanda",
    )
    fig_map.update_layout(height=420, margin=dict(t=40, b=10, l=10, r=10))
    st.plotly_chart(fig_map, use_container_width=True)

    # Temporal Severity Strip
    st.divider()
    st.markdown(f"**Temporal Severity Strip — {province} Province**")

    sel_index = st.radio(
        "Index for timeline view",
        ["adewi", "cadi", "z_ndvi"],
        horizontal=True,
        format_func=lambda x: {"adewi": "ADEWI", "cadi": "CADI", "z_ndvi": "NDVI Z-score"}[x],
    )
    col_class = sel_index.replace("z_", "") + "_class" if sel_index.startswith("z_") else sel_index + "_class"
    if col_class not in prov_df.columns:
        col_class = "adewi_class"

    strip_df = prov_df[["time", sel_index, col_class]].copy()
    strip_df["province_label"] = province
    strip_df["formatted_date"] = strip_df["time"].dt.strftime("%Y-%m-%d")

    fig_heat = px.scatter(
        strip_df,
        x="time",
        y="province_label",
        color=col_class,
        color_discrete_map=CLASS_COLORS,
        category_orders={col_class: CLASS_ORDER + ["Missing"]},
        hover_data={sel_index: ":.2f", "formatted_date": True, "province_label": False},
        height=190,
        title=f"{province} Province — {sel_index.upper()} Severity Timeline",
    )
    fig_heat.update_traces(marker=dict(size=14, symbol="square"))
    fig_heat.update_layout(
        yaxis_title="",
        xaxis_title="Date",
        showlegend=True,
        legend_title="Drought Class",
        margin=dict(t=40, b=20),
        template="plotly_white",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Side-by-side annual drought fractions
    st.markdown("**Annual Drought Fraction by Province (ADEWI ≤ threshold)**")
    ann = (
        index_df.assign(drought=(index_df["adewi"] <= drought_thr))
        .groupby(["province", index_df["time"].dt.year])["drought"]
        .mean()
        .reset_index()
    )
    ann.columns = ["Province", "Year", "Drought Fraction"]
    fig_ann = px.bar(
        ann,
        x="Year",
        y="Drought Fraction",
        color="Province",
        barmode="group",
        color_discrete_map={"Eastern": "#c0392b", "Southern": "#2980b9"},
        title="Proportion of Composites in Drought per Year",
    )
    fig_ann.update_layout(template="plotly_white", height=320)
    st.plotly_chart(fig_ann, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — Sensitivity Analysis
# ═══════════════════════════════════════════════════════════════════════════

with tab_sens:
    st.subheader("Component Weight Sensitivity Analysis")
    st.info(
        "Explore how varying the weights of Rainfall, Soil Moisture, and LST affects "
        "drought detection lead times and event counts without altering default saved outputs.",
        icon="ℹ️",
    )

    col_w1, col_w2, col_w3 = st.columns(3)
    w_rain = col_w1.slider("Rainfall Weight (w_rainfall)", 0.0, 1.0, 0.40, 0.05)
    w_sm = col_w2.slider("Soil Moisture Weight (w_soil_moisture)", 0.0, 1.0, 0.35, 0.05)
    w_lst = col_w3.slider("LST Weight (w_lst)", 0.0, 1.0, 0.25, 0.05)

    sum_w = w_rain + w_sm + w_lst
    if abs(sum_w - 1.0) < 0.01:
        st.success(f"Weight sum: **{sum_w:.2f}** (Normalized)")
    else:
        st.caption(f"Current weight sum: **{sum_w:.2f}** (Normalized weights: rain={w_rain/max(sum_w,1e-6):.2f}, SM={w_sm/max(sum_w,1e-6):.2f}, LST={w_lst/max(sum_w,1e-6):.2f})")

    if st.button("▶ Run Custom Scenario", key="sens_run"):
        with st.spinner("Recomputing index and lead times under custom weights…"):
            cfg_local = copy.deepcopy(cfg)
            cfg_local["weights"]["adewi"] = {
                "rainfall": w_rain,
                "soil_moisture": w_sm,
                "lst": w_lst,
            }
            raw_data, _ = _dl(cfg_local)
            cleaned_data, _ = _pre(raw_data)
            anom_data, _ = _ca(cleaned_data)
            idx_scenario = _ci(anom_data, cfg_local)
            _, summary_scenario = _lt(idx_scenario, cfg_local)

            # Compare against baseline
            base_summary_path = Path(cfg["paths"]["tables"]) / "table_lead_time_summary.csv"
            if base_summary_path.exists():
                base_sum = pd.read_csv(base_summary_path)
                base_pooled = base_sum[base_sum["province"] == "Eastern+Southern"]
                scen_pooled = summary_scenario[summary_scenario["province"] == "Eastern+Southern"]

                if not base_pooled.empty and not scen_pooled.empty:
                    st.markdown("### Comparative Performance: Baseline vs. Custom Scenario")
                    cmp_df = pd.DataFrame(
                        {
                            "Metric": ["Mean Lead (weeks)", "Success Rate (%)", "Events Detected"],
                            "Baseline (40/35/25)": [
                                round(base_pooled["mean_lead_weeks"].iloc[0], 1),
                                round(base_pooled["success_rate"].iloc[0] * 100, 1),
                                int(base_pooled["n_detected"].iloc[0]),
                            ],
                            "Custom Scenario": [
                                round(scen_pooled["mean_lead_weeks"].iloc[0], 1),
                                round(scen_pooled["success_rate"].iloc[0] * 100, 1),
                                int(scen_pooled["n_detected"].iloc[0]),
                            ],
                        }
                    )
                    st.dataframe(cmp_df, use_container_width=True, hide_index=True)

                    # Grouped chart
                    fig_cmp = px.bar(
                        pd.DataFrame({
                            "Scenario": ["Baseline", "Custom Scenario"],
                            "Mean Lead (Weeks)": [
                                base_pooled["mean_lead_weeks"].iloc[0],
                                scen_pooled["mean_lead_weeks"].iloc[0],
                            ]
                        }),
                        x="Scenario",
                        y="Mean Lead (Weeks)",
                        color="Scenario",
                        color_discrete_sequence=["#34495e", "#e67e22"],
                        title="Mean Lead Time Comparison",
                    )
                    fig_cmp.update_layout(template="plotly_white", height=280, showlegend=False)
                    st.plotly_chart(fig_cmp, use_container_width=True)

            st.markdown("**Scenario Summary Table:**")
            st.dataframe(summary_scenario, use_container_width=True, hide_index=True)

    # Show pre-computed sensitivity table from disk if available
    sens_path = Path(cfg["paths"]["tables"]) / "table_sensitivity_analysis.csv"
    if sens_path.exists():
        st.divider()
        st.markdown("**Pre-Computed Multi-Scenario Benchmark (from `scripts/sensitivity_analysis.py`)**")
        st.dataframe(pd.read_csv(sens_path), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 — About & Methodology
# ═══════════════════════════════════════════════════════════════════════════

with tab_about:
    st.subheader("Project Overview & Scientific Methodology")

    with st.expander("📖 Study Scope & Objectives", expanded=True):
        st.markdown(
            """
            - **Title:** Development of a Satellite-Based Agricultural Drought Early-Warning Index for Rwanda
            - **Study Area:** Eastern and Southern Provinces, Rwanda
            - **Temporal Coverage:** January 2018 – December 2024 (16-day MODIS composite intervals)
            - **Core Question:** Can combining rainfall, soil moisture, and land-surface temperature anomalies
              provide advance detection of agricultural drought before vegetation-based indicators (NDVI) respond?
            """
        )

    with st.expander("📐 Index Formulations & Weighting Schemes"):
        st.markdown(
            """
            #### 1. Agricultural Drought Early-Warning Index (ADEWI)
            $$\\mathrm{ADEWI} = 0.40 \\cdot Z_{\\mathrm{rain}} + 0.35 \\cdot Z_{\\mathrm{SM}} - 0.25 \\cdot Z_{\\mathrm{LST}}$$
            *Note:* Vegetation variables (NDVI, EVI) are intentionally excluded from ADEWI to enable unbiased,
            non-circular lead-time comparisons against vegetation stress onset.

            #### 2. Combined Agricultural Drought Index (CADI)
            $$\\mathrm{CADI} = 0.30 \\cdot Z_{\\mathrm{NDVI}} + 0.15 \\cdot Z_{\\mathrm{EVI}} + 0.30 \\cdot Z_{\\mathrm{rain}} + 0.20 \\cdot Z_{\\mathrm{SM}} - 0.20 \\cdot Z_{\\mathrm{LST}}$$
            """
        )

    with st.expander("📊 Drought Severity Classification"):
        st.markdown(
            """
            | Anomaly Range | Classification | Indicator Color |
            |---|---|---|
            | $x \\geq -0.5$ | Normal | 🟢 Green |
            | $-1.0 \\leq x < -0.5$ | Mild | 🟡 Yellow |
            | $-1.5 \\leq x < -1.0$ | Moderate | 🟠 Orange |
            | $-2.0 \\leq x < -1.5$ | Severe | 🔴 Red |
            | $x < -2.0$ | Extreme | 🟤 Dark Red |
            """
        )

    with st.expander("🛰️ Environmental Data Sources"):
        st.markdown(
            """
            | Parameter | Satellite / Sensor | Platform | Resolution |
            |---|---|---|---|
            | **NDVI & EVI** | MODIS MOD13Q1 v061 | Google Earth Engine | 250 m, 16-day |
            | **Precipitation** | CHIRPS Pentad v2.0 | GEE / DE Africa | 5 km, pentad |
            | **Soil Moisture** | NASA FLDAS / ESA CCI | GEE / Copernicus | 0.1° / 0.25°, monthly |
            | **LST** | MODIS MOD11A2 v061 | Google Earth Engine | 1 km, 8-day |
            """
        )

    with st.expander("⚠️ Scientific Disclaimers & Integrity"):
        st.markdown(
            """
            - **Research Prototype:** This software is an academic demonstration and is **not an operational warning service**.
            - **Synthetic Data Notice:** Outputs generated in the absence of real GEE exports reflect simulated data and
              must not be interpreted or reported as empirical drought findings.
            - **Crop Validation:** Agricultural statistics in placeholder files represent schematic values and must be replaced
              with authenticated NISR / MINAGRI agricultural surveys prior to publication.
            """
        )
