"""Publication-oriented figures for the ADEWI / CADI study.

Figure inventory
----------------
fig01 – ADEWI and NDVI anomaly time series (both provinces)
fig02 – Component anomalies: Z_rainfall, Z_SM, Z_LST, Z_NDVI (Eastern)
fig03 – Lead-time bar chart per event
fig04 – ADEWI drought-class timeline (coloured strip)
fig05 – Spatial ADEWI snapshot map (one date)
fig06 – Lead-time distribution boxplot
fig07 – ADEWI vs NDVI scatter
fig08 – ADEWI during known drought periods (bar)
fig09 – EVI vs NDVI anomaly comparison (new)
fig10 – Province comparison: Eastern vs Southern ADEWI stacked (new)
fig11 – CADI vs ADEWI time series (new)

FIGURE_METADATA maps output filename → (figure number, caption).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams.update({
    "figure.constrained_layout.use": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "DejaVu Sans",
})

PROV_COLORS = {"Eastern": "#c0392b", "Southern": "#2980b9"}
DROUGHT_PALETTE = {
    "Extreme": "#6b0000",
    "Severe": "#c0392b",
    "Moderate": "#e67e22",
    "Mild": "#f1c40f",
    "Normal": "#2ecc71",
    "Missing": "#bdc3c7",
}

FIGURE_METADATA: dict[str, tuple[int, str]] = {
    "fig01_adewi_ndvi_timeseries.png": (
        1,
        "Time series of ADEWI (top) and NDVI standardized anomaly (bottom) for the "
        "Eastern and Southern Provinces of Rwanda, 2018–2024. "
        "Dashed line marks the drought detection threshold (−1.0).",
    ),
    "fig02_component_anomalies_eastern.png": (
        2,
        "Standardized anomalies of ADEWI component variables (rainfall, soil moisture, "
        "LST, and NDVI) for the Eastern Province, 2018–2024.",
    ),
    "fig03_lead_time_by_event.png": (
        3,
        "ADEWI lead time (weeks) ahead of NDVI drought onset for each detected event. "
        "Dashed vertical line indicates the mean lead time.",
    ),
    "fig04_drought_class_timeline.png": (
        4,
        "ADEWI drought severity classification over time for the Eastern and Southern "
        "Provinces. Colours follow the five-class scheme (Normal to Extreme).",
    ),
    "fig06_lead_time_distribution.png": (
        6,
        "Distribution of ADEWI lead times (weeks) ahead of NDVI drought onset, "
        "stratified by province.",
    ),
    "fig07_adewi_vs_ndvi_scatter.png": (
        7,
        "Concurrent relationship between ADEWI and NDVI standardized anomaly. "
        "Dashed lines mark the drought threshold (−1.0) on each axis.",
    ),
    "fig08_validation_known_periods.png": (
        8,
        "Minimum ADEWI value recorded during each documented drought period. "
        "Dashed line marks the event detection threshold (−1.0).",
    ),
    "fig09_evi_ndvi_comparison.png": (
        9,
        "EVI and NDVI standardized anomalies for both provinces, 2018–2024. "
        "The two indices track closely but EVI is more sensitive to canopy structural changes.",
    ),
    "fig10_province_comparison.png": (
        10,
        "Province-level comparison of ADEWI for Eastern and Southern Rwanda. "
        "Eastern Province exhibits stronger and more frequent drought signals.",
    ),
    "fig11_cadi_vs_adewi.png": (
        11,
        "CADI (Combined Agricultural Drought Index, vegetation-inclusive) vs ADEWI "
        "(vegetation-independent early-warning index) for the Eastern Province. "
        "ADEWI is expected to cross the threshold earlier than CADI/NDVI.",
    ),
}


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Original figures (improved aesthetics)
# ---------------------------------------------------------------------------

def fig_timeseries(index_df: pd.DataFrame, outdir: Path) -> Path:
    """Fig 01 – ADEWI and NDVI standardized anomaly time series."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 7.5), sharex=True)
    for ax, col, title in (
        (axes[0], "adewi", "ADEWI  (0.40·Z_rain + 0.35·Z_SM − 0.25·Z_LST)"),
        (axes[1], "z_ndvi", "NDVI standardized anomaly (Z-score)"),
    ):
        for prov, g in index_df.groupby("province"):
            ax.plot(
                g["time"], g[col],
                label=prov, color=PROV_COLORS[prov], lw=1.5, alpha=0.9,
            )
        ax.axhline(-1.0, color="k", ls="--", lw=0.9, label="Threshold (−1.0)")
        ax.axhline(0.0, color="0.6", ls=":", lw=0.7)
        ax.axhspan(-10, -1.0, alpha=0.04, color="red", zorder=0)
        ax.set_ylabel(title, fontsize=9)
        ax.legend(frameon=False, loc="lower left", fontsize=8)
    axes[1].set_xlabel("Date")
    fig.suptitle(
        "Agricultural drought early-warning vs vegetation stress — Rwanda 2018–2024",
        fontsize=11, fontweight="bold",
    )
    return _save(fig, outdir / "fig01_adewi_ndvi_timeseries.png")


def fig_components(index_df: pd.DataFrame, outdir: Path) -> Path:
    """Fig 02 – Component anomaly stack (Eastern Province)."""
    cols = ["z_rainfall", "z_soil_moisture", "z_lst", "z_ndvi"]
    titles = ["Rainfall Z-score", "Soil moisture Z-score", "LST Z-score", "NDVI Z-score"]
    east = index_df[index_df["province"] == "Eastern"]
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    clrs = ["#2471a3", "#1abc9c", "#e74c3c", "#27ae60"]
    for ax, c, t, clr in zip(axes, cols, titles, clrs):
        ax.fill_between(
            east["time"], east[c], 0,
            where=(east[c] < 0), alpha=0.35, color=clr, interpolate=True,
        )
        ax.plot(east["time"], east[c], color=clr, lw=1.2)
        ax.axhline(0, color="0.5", ls=":", lw=0.7)
        ax.axhline(-1, color="0.3", ls="--", lw=0.7)
        ax.set_ylabel(t, fontsize=8)
    axes[-1].set_xlabel("Date")
    fig.suptitle(
        "Eastern Province — standardized anomalies of ADEWI component variables",
        fontsize=11, fontweight="bold",
    )
    return _save(fig, outdir / "fig02_component_anomalies_eastern.png")


def fig_lead_bars(events: pd.DataFrame, outdir: Path) -> Path:
    """Fig 03 – Lead-time per event horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(10, 5))
    det = events[events["detected"]].copy() if not events.empty else pd.DataFrame()
    if det.empty:
        ax.text(0.5, 0.5, "No ADEWI detections", ha="center", va="center",
                transform=ax.transAxes, fontsize=11, color="0.5")
    else:
        det = det.sort_values("ndvi_onset")
        labels = [
            f"{r.province[:3]}  {pd.Timestamp(r.ndvi_onset).strftime('%Y-%m')}"
            for r in det.itertuples()
        ]
        colors = [PROV_COLORS[p] for p in det["province"]]
        bars = ax.barh(labels, det["lead_weeks"], color=colors, edgecolor="white", height=0.65)
        ax.bar_label(bars, fmt="%.1f wk", padding=3, fontsize=8)
        mean_lw = det["lead_weeks"].mean()
        ax.axvline(mean_lw, color="k", ls="--", lw=1.2,
                   label=f"Mean lead = {mean_lw:.1f} wk")
        ax.set_xlabel("Lead time (weeks)")
        ax.legend(frameon=False, fontsize=9)
    ax.set_title("ADEWI lead time ahead of NDVI drought onset", fontweight="bold")
    return _save(fig, outdir / "fig03_lead_time_by_event.png")


def fig_class_heatmap(index_df: pd.DataFrame, outdir: Path) -> Path:
    """Fig 04 – ADEWI drought-class colour strip per province."""
    order = ["Extreme", "Severe", "Moderate", "Mild", "Normal", "Missing"]
    score = {k: i for i, k in enumerate(order)}
    cmap_colors = [
        DROUGHT_PALETTE[k] for k in order
    ]
    import matplotlib.colors as mc
    cmap = mc.ListedColormap(cmap_colors)
    bounds = list(range(len(order) + 1))
    norm = mc.BoundaryNorm(bounds, cmap.N)

    fig, axes = plt.subplots(2, 1, figsize=(13, 3.5), sharex=True)
    for ax, prov in zip(axes, ["Eastern", "Southern"]):
        g = index_df[index_df["province"] == prov].copy()
        codes = g["adewi_class"].map(score).fillna(score["Missing"])
        sc = ax.scatter(
            g["time"], np.zeros(len(g)),
            c=codes, cmap=cmap, norm=norm, s=55, marker="s",
        )
        ax.set_yticks([])
        ax.set_ylabel(prov, fontsize=9)
        ax.set_ylim(-0.5, 0.5)
    axes[0].set_title("ADEWI drought severity class timeline", fontweight="bold")
    # Shared legend
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=DROUGHT_PALETTE[k])
        for k in order if k != "Missing"
    ]
    fig.legend(
        handles, [k for k in order if k != "Missing"],
        loc="lower center", ncol=5, frameon=False, fontsize=8,
        bbox_to_anchor=(0.5, -0.05),
    )
    return _save(fig, outdir / "fig04_drought_class_timeline.png")


def fig_spatial_snapshot(
    cube: dict[str, Any],
    adewi_cube: np.ndarray,
    date: pd.Timestamp,
    outdir: Path,
) -> Path:
    """Fig 05 – Spatial ADEWI map for a given date."""
    times = list(cube["time"])
    idx = int(np.argmin([abs((t - date).days) for t in times]))
    field = adewi_cube[idx]
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    lon, lat = cube["lon"], cube["lat"]
    im = ax.pcolormesh(lon, lat, field, cmap="RdYlBu", vmin=-2.5, vmax=2.5, shading="auto")
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    actual_date = pd.Timestamp(times[idx]).strftime("%Y-%m-%d")
    ax.set_title(f"ADEWI spatial map — {actual_date}", fontweight="bold")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("ADEWI (standardized)")
    return _save(fig, outdir / f"fig05_adewi_map_{pd.Timestamp(times[idx]).strftime('%Y%m%d')}.png")


def fig_lead_distribution(events: pd.DataFrame, outdir: Path) -> Path:
    """Fig 06 – Lead-time distribution boxplot by province."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    det = events[events["detected"]] if not events.empty else pd.DataFrame()
    if not det.empty:
        sns.boxplot(
            data=det, x="province", y="lead_weeks", hue="province",
            palette=PROV_COLORS, ax=ax, legend=False, width=0.45,
        )
        sns.stripplot(
            data=det, x="province", y="lead_weeks",
            color="k", ax=ax, size=5, jitter=True, alpha=0.7,
        )
        ax.axhline(det["lead_weeks"].mean(), color="navy", ls="--", lw=1,
                   label=f"Overall mean = {det['lead_weeks'].mean():.1f} wk")
        ax.legend(frameon=False, fontsize=9)
    ax.set_ylabel("Lead time (weeks)")
    ax.set_xlabel("Province")
    ax.set_title("Distribution of ADEWI lead times ahead of NDVI drought onset",
                 fontweight="bold")
    return _save(fig, outdir / "fig06_lead_time_distribution.png")


def fig_scatter_adewi_ndvi(index_df: pd.DataFrame, outdir: Path) -> Path:
    """Fig 07 – ADEWI vs NDVI Z-score scatter."""
    fig, ax = plt.subplots(figsize=(6.5, 6))
    for prov, g in index_df.groupby("province"):
        ax.scatter(
            g["adewi"], g["z_ndvi"],
            s=14, alpha=0.5, label=prov, color=PROV_COLORS[prov],
        )
    ax.axhline(-1, color="k", ls="--", lw=0.8, alpha=0.7)
    ax.axvline(-1, color="k", ls="--", lw=0.8, alpha=0.7)
    ax.fill_between([-5, -1], [-1, -1], [-5, -5], alpha=0.07, color="red",
                    label="Both in drought zone")
    ax.set_xlabel("ADEWI (standardized)")
    ax.set_ylabel("NDVI Z-score")
    ax.legend(frameon=False, fontsize=9)
    ax.set_title("Concurrent relationship: ADEWI vs NDVI standardized anomaly",
                 fontweight="bold")
    lims = [-3, 2]
    ax.set_xlim(lims); ax.set_ylim(lims)
    return _save(fig, outdir / "fig07_adewi_vs_ndvi_scatter.png")


def fig_validation_bars(period_df: pd.DataFrame, outdir: Path) -> Path:
    """Fig 08 – Minimum ADEWI during known drought periods."""
    vis = period_df[period_df["in_study_window"]].copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if vis.empty:
        ax.text(0.5, 0.5, "No overlapping validation periods in study window",
                ha="center", va="center", transform=ax.transAxes, color="0.5")
    else:
        colors = [
            "#922b21" if v <= -1.0 else "#e67e22" if v <= -0.5 else "#2ecc71"
            for v in vis["min_adewi"]
        ]
        ax.bar(range(len(vis)), vis["min_adewi"], color=colors, edgecolor="white")
        ax.axhline(-1.0, color="k", ls="--", lw=1.0, label="Drought threshold (−1.0)")
        ax.set_xticks(range(len(vis)))
        ax.set_xticklabels(list(vis["period"]), rotation=25, ha="right", fontsize=8)
        ax.set_ylabel("Minimum ADEWI during period")
        ax.legend(frameon=False, fontsize=9)
    ax.set_title("ADEWI during documented / hypothesized drought periods",
                 fontweight="bold")
    return _save(fig, outdir / "fig08_validation_known_periods.png")


# ---------------------------------------------------------------------------
# New figures
# ---------------------------------------------------------------------------

def fig_evi_ndvi_comparison(index_df: pd.DataFrame, outdir: Path) -> Path:
    """Fig 09 – EVI vs NDVI anomaly comparison (both provinces).

    Justifies EVI inclusion in CADI by showing where the two indices diverge.
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    for ax, prov in zip(axes, ["Eastern", "Southern"]):
        g = index_df[index_df["province"] == prov]
        ax.plot(g["time"], g["z_ndvi"], color=PROV_COLORS[prov],
                lw=1.4, label="NDVI Z-score", alpha=0.9)
        ax.plot(g["time"], g["z_evi"], color=PROV_COLORS[prov],
                lw=1.2, ls="--", label="EVI Z-score", alpha=0.75)
        ax.axhline(-1.0, color="k", ls=":", lw=0.8)
        ax.axhline(0, color="0.7", ls=":", lw=0.6)
        ax.set_ylabel(f"{prov} — Z-score", fontsize=9)
        ax.legend(frameon=False, fontsize=8, loc="lower left")
    axes[-1].set_xlabel("Date")
    fig.suptitle(
        "EVI vs NDVI standardized anomaly — Eastern and Southern Rwanda 2018–2024",
        fontsize=11, fontweight="bold",
    )
    return _save(fig, outdir / "fig09_evi_ndvi_comparison.png")


def fig_province_comparison(index_df: pd.DataFrame, outdir: Path) -> Path:
    """Fig 10 – Side-by-side ADEWI comparison: Eastern vs Southern Province.

    Highlights how drought severity and timing differ between provinces.
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    for prov, g in index_df.groupby("province"):
        ax.fill_between(
            g["time"], g["adewi"], 0,
            where=(g["adewi"] < 0),
            alpha=0.40, color=PROV_COLORS[prov], label=f"{prov} (drought)",
            interpolate=True,
        )
        ax.plot(g["time"], g["adewi"], color=PROV_COLORS[prov], lw=1.2, alpha=0.9)
    ax.axhline(-1.0, color="k", ls="--", lw=0.9, label="Threshold (−1.0)")
    ax.axhline(0.0, color="0.6", ls=":", lw=0.6)
    ax.set_ylabel("ADEWI (standardized anomaly)")
    ax.set_xlabel("Date")
    ax.legend(frameon=False, fontsize=9)
    ax.set_title(
        "Province comparison — ADEWI drought signal: Eastern vs Southern Rwanda",
        fontweight="bold",
    )
    return _save(fig, outdir / "fig10_province_comparison.png")


def fig_cadi_vs_adewi(index_df: pd.DataFrame, outdir: Path) -> Path:
    """Fig 11 – CADI vs ADEWI time series (Eastern Province).

    Key interpretive figure: shows whether ADEWI (vegetation-free) crosses
    the threshold before CADI (vegetation-inclusive).
    """
    east = index_df[index_df["province"] == "Eastern"]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(east["time"], east["adewi"], color="#e74c3c", lw=1.5,
            label="ADEWI (vegetation-independent)", alpha=0.9)
    ax.plot(east["time"], east["cadi"], color="#8e44ad", lw=1.4, ls="--",
            label="CADI (vegetation-inclusive)", alpha=0.85)
    ax.plot(east["time"], east["z_ndvi"], color="#27ae60", lw=1.1, ls=":",
            label="NDVI Z-score (reference)", alpha=0.75)
    ax.axhline(-1.0, color="k", ls="--", lw=0.8, label="Drought threshold (−1.0)")
    ax.axhline(0.0, color="0.6", ls=":", lw=0.6)
    ax.set_ylabel("Standardized index value")
    ax.set_xlabel("Date")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.set_title(
        "CADI vs ADEWI vs NDVI — Eastern Province 2018–2024\n"
        "(ADEWI is expected to cross −1.0 before CADI/NDVI)",
        fontweight="bold",
    )
    return _save(fig, outdir / "fig11_cadi_vs_adewi.png")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def make_all_figures(
    index_df: pd.DataFrame,
    events: pd.DataFrame,
    period_df: pd.DataFrame,
    outdir: Path,
    cube: dict[str, Any] | None = None,
    adewi_cube: np.ndarray | None = None,
) -> list[Path]:
    """Generate all publication figures and return their paths.

    Parameters
    ----------
    index_df:
        Full index DataFrame (all provinces, all timesteps).
    events:
        Lead-time event table.
    period_df:
        Known-drought-period validation table.
    outdir:
        Directory to save figures.
    cube:
        Optional spatial data cube (for map figures).
    adewi_cube:
        Optional pre-computed spatial ADEWI array.

    Returns
    -------
    List of saved figure file paths.
    """
    paths = [
        fig_timeseries(index_df, outdir),
        fig_components(index_df, outdir),
        fig_lead_bars(events, outdir),
        fig_class_heatmap(index_df, outdir),
        fig_lead_distribution(events, outdir),
        fig_scatter_adewi_ndvi(index_df, outdir),
        fig_validation_bars(period_df, outdir),
        fig_evi_ndvi_comparison(index_df, outdir),
        fig_province_comparison(index_df, outdir),
        fig_cadi_vs_adewi(index_df, outdir),
    ]
    if cube is not None and adewi_cube is not None:
        for d in ("2022-01-01", "2023-02-15"):
            paths.append(fig_spatial_snapshot(cube, adewi_cube, pd.Timestamp(d), outdir))
    return paths
