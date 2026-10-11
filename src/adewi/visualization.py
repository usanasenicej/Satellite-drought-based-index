"""Publication-oriented figures for the ADEWI study."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", font_scale=1.05)
PROV_COLORS = {"Eastern": "#c0392b", "Southern": "#2980b9"}


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_timeseries(index_df: pd.DataFrame, outdir: Path) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
    for ax, col, title in (
        (axes[0], "adewi", "ADEWI (rainfall + soil moisture − LST)"),
        (axes[1], "z_ndvi", "NDVI standardized anomaly"),
    ):
        for prov, g in index_df.groupby("province"):
            ax.plot(g["time"], g[col], label=prov, color=PROV_COLORS[prov], lw=1.4)
        ax.axhline(-1.0, color="k", ls="--", lw=0.8, label="Threshold (−1.0)")
        ax.axhline(0.0, color="0.5", ls=":", lw=0.7)
        ax.set_ylabel(title)
        ax.legend(frameon=False, loc="lower left")
    axes[1].set_xlabel("Date")
    fig.suptitle("Agricultural drought early-warning vs vegetation stress, Rwanda 2018–2024")
    return _save(fig, outdir / "fig01_adewi_ndvi_timeseries.png")


def fig_components(index_df: pd.DataFrame, outdir: Path) -> Path:
    cols = ["z_rainfall", "z_soil_moisture", "z_lst", "z_ndvi"]
    titles = ["Rainfall Z", "Soil moisture Z", "LST Z", "NDVI Z"]
    fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)
    east = index_df[index_df["province"] == "Eastern"]
    for ax, c, t in zip(axes, cols, titles):
        ax.plot(east["time"], east[c], color="#1a5276", lw=1.2)
        ax.axhline(0, color="0.5", ls=":", lw=0.7)
        ax.set_ylabel(t)
    axes[-1].set_xlabel("Date")
    fig.suptitle("Eastern Province: standardized anomalies of ADEWI components")
    return _save(fig, outdir / "fig02_component_anomalies_eastern.png")


def fig_lead_bars(events: pd.DataFrame, outdir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    det = events[events["detected"]].copy()
    if det.empty:
        ax.text(0.5, 0.5, "No ADEWI detections", ha="center")
    else:
        det = det.sort_values("ndvi_onset")
        labels = [
            f"{r.province[:3]} {pd.Timestamp(r.ndvi_onset).strftime('%Y-%m')}"
            for r in det.itertuples()
        ]
        colors = [PROV_COLORS[p] for p in det["province"]]
        ax.barh(labels, det["lead_weeks"], color=colors)
        ax.axvline(det["lead_weeks"].mean(), color="k", ls="--", label="Mean lead")
        ax.set_xlabel("Lead time (weeks)")
        ax.legend(frameon=False)
    ax.set_title("ADEWI lead time ahead of NDVI drought onset")
    return _save(fig, outdir / "fig03_lead_time_by_event.png")


def fig_class_heatmap(index_df: pd.DataFrame, outdir: Path) -> Path:
    order = ["Extreme", "Severe", "Moderate", "Mild", "Watch", "Normal"]
    score = {k: i for i, k in enumerate(order)}
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    for ax, prov in zip(axes, ["Eastern", "Southern"]):
        g = index_df[index_df["province"] == prov].copy()
        g["code"] = g["adewi_class"].map(score)
        ax.scatter(g["time"], np.zeros(len(g)), c=g["code"], cmap="RdYlGn", s=40, marker="s")
        ax.set_yticks([])
        ax.set_ylabel(prov)
    axes[0].set_title("ADEWI drought class through time")
    return _save(fig, outdir / "fig04_drought_class_timeline.png")


def fig_spatial_snapshot(cube: dict[str, Any], adewi_cube: np.ndarray, date: pd.Timestamp, outdir: Path) -> Path:
    times = list(cube["time"])
    # nearest date
    idx = int(np.argmin([abs((t - date).days) for t in times]))
    field = adewi_cube[idx]
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    lon, lat = cube["lon"], cube["lat"]
    im = ax.pcolormesh(lon, lat, field, cmap="RdYlBu", vmin=-2.5, vmax=2.5, shading="auto")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"ADEWI map — {pd.Timestamp(times[idx]).strftime('%Y-%m-%d')}")
    cb = fig.colorbar(im, ax=ax, fraction=0.046)
    cb.set_label("ADEWI (standardized)")
    return _save(fig, outdir / f"fig05_adewi_map_{pd.Timestamp(times[idx]).strftime('%Y%m%d')}.png")


def fig_lead_distribution(events: pd.DataFrame, outdir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    det = events[events["detected"]]
    if not det.empty:
        sns.boxplot(data=det, x="province", y="lead_weeks", hue="province", palette=PROV_COLORS, ax=ax, legend=False)
        sns.stripplot(data=det, x="province", y="lead_weeks", color="k", ax=ax, size=5)
    ax.set_ylabel("Lead time (weeks)")
    ax.set_title("Distribution of ADEWI lead times")
    return _save(fig, outdir / "fig06_lead_time_distribution.png")


def fig_scatter_adewi_ndvi(index_df: pd.DataFrame, outdir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(6.5, 6))
    for prov, g in index_df.groupby("province"):
        ax.scatter(g["adewi"], g["z_ndvi"], s=12, alpha=0.45, label=prov, color=PROV_COLORS[prov])
    ax.axhline(-1, color="k", ls="--", lw=0.7)
    ax.axvline(-1, color="k", ls="--", lw=0.7)
    ax.set_xlabel("ADEWI")
    ax.set_ylabel("NDVI Z-score")
    ax.legend(frameon=False)
    ax.set_title("Concurrent relationship between ADEWI and NDVI anomaly")
    ax.set_aspect("equal", adjustable="box")
    return _save(fig, outdir / "fig07_adewi_vs_ndvi_scatter.png")


def fig_validation_bars(period_df: pd.DataFrame, outdir: Path) -> Path:
    vis = period_df[period_df["in_study_window"]].copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if vis.empty:
        ax.text(0.5, 0.5, "No overlapping validation periods", ha="center")
    else:
        ax.bar(vis["period"], vis["min_adewi"], color="#922b21")
        ax.axhline(-1.0, color="k", ls="--")
        ax.set_ylabel("Minimum ADEWI during period")
        ax.set_xticks(range(len(vis)))
        ax.set_xticklabels(list(vis["period"]), rotation=20, ha="right")
    ax.set_title("ADEWI during known / hypothesized drought periods")
    return _save(fig, outdir / "fig08_validation_known_periods.png")


def make_all_figures(
    index_df: pd.DataFrame,
    events: pd.DataFrame,
    period_df: pd.DataFrame,
    outdir: Path,
    cube: dict[str, Any] | None = None,
    adewi_cube: np.ndarray | None = None,
) -> list[Path]:
    paths = [
        fig_timeseries(index_df, outdir),
        fig_components(index_df, outdir),
        fig_lead_bars(events, outdir),
        fig_class_heatmap(index_df, outdir),
        fig_lead_distribution(events, outdir),
        fig_scatter_adewi_ndvi(index_df, outdir),
        fig_validation_bars(period_df, outdir),
    ]
    if cube is not None and adewi_cube is not None:
        for d in ("2022-01-01", "2023-02-15"):
            paths.append(fig_spatial_snapshot(cube, adewi_cube, pd.Timestamp(d), outdir))
    return paths
