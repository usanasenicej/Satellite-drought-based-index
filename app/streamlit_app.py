"""Minimal ADEWI demonstrator: province + year → drought class, time series, lead time."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import plotly.express as px
import streamlit as st

from adewi.config import load_config
from adewi.run_pipeline import run

st.set_page_config(page_title="Rwanda ADEWI", layout="wide")
st.title("Agricultural Drought Early-Warning Index — Rwanda")
st.caption("Eastern and Southern Provinces · 2018–2024")

cfg = load_config()
index_path = Path(cfg["paths"]["data_processed"]) / "adewi_index_timeseries.csv"
events_path = Path(cfg["paths"]["tables"]) / "table_lead_time_events.csv"
summary_path = Path(cfg["paths"]["tables"]) / "table_lead_time_summary.csv"

if not index_path.exists():
    st.info("No processed index found. Running the analysis pipeline once…")
    with st.spinner("Computing ADEWI…"):
        run()

index_df = pd.read_csv(index_path, parse_dates=["time"])
source = index_df["data_source"].iloc[0] if "data_source" in index_df.columns else "unknown"
if source == "synthetic":
    st.warning(
        "Currently showing **synthetic demonstration data**. "
        "Export real GEE/DE Africa series to `data/raw/provincial_timeseries.csv` "
        "and re-run the pipeline before using this for research claims."
    )

col1, col2 = st.columns(2)
province = col1.selectbox("Province", sorted(index_df["province"].unique()))
years = sorted(index_df["time"].dt.year.unique())
year = col2.selectbox("Year", years, index=len(years) - 3 if len(years) >= 3 else 0)

g = index_df[(index_df["province"] == province) & (index_df["time"].dt.year == year)]
full = index_df[index_df["province"] == province]

m1, m2, m3 = st.columns(3)
if len(g):
    m1.metric("Mean ADEWI (selected year)", f"{g['adewi'].mean():.2f}")
    m2.metric("Minimum ADEWI", f"{g['adewi'].min():.2f}")
    worst = g.loc[g["adewi"].idxmin(), "adewi_class"]
    m3.metric("Worst class", str(worst))

fig = px.line(
    full,
    x="time",
    y=["adewi", "z_ndvi"],
    labels={"value": "Standardized index", "time": "Date", "variable": "Series"},
    title=f"{province} Province — ADEWI vs NDVI anomaly",
)
fig.add_hline(y=-1.0, line_dash="dash", annotation_text="Drought threshold")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Drought class (selected year)")
    st.dataframe(
        g[["time", "adewi", "adewi_class", "z_ndvi", "ndvi_class", "z_rainfall", "z_soil_moisture", "z_lst"]],
        use_container_width=True,
        hide_index=True,
    )
with right:
    st.subheader("Lead-time events")
    if events_path.exists():
        ev = pd.read_csv(events_path, parse_dates=["ndvi_onset", "ndvi_end", "adewi_onset"])
        st.dataframe(ev[ev["province"] == province], use_container_width=True, hide_index=True)
    if summary_path.exists():
        sm = pd.read_csv(summary_path)
        st.markdown("**Summary**")
        st.dataframe(sm, use_container_width=True, hide_index=True)

st.markdown(
    """
**How to read ADEWI.** Negative values mean rainfall and soil moisture are below
normal and/or land surface temperature is above normal. The research question is
whether ADEWI crosses −1.0 several weeks before NDVI does.

**Formula.** ADEWI = 0.40·Z(rainfall) + 0.35·Z(soil moisture) − 0.25·Z(LST)
"""
)
