"""Load study configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "config.yaml"


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path else DEFAULT_CONFIG
    with cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for key, rel in cfg.get("paths", {}).items():
        cfg["paths"][key] = str((ROOT / rel).resolve())
    return cfg


def ensure_dirs(cfg: dict[str, Any]) -> None:
    for key in ("data_raw", "data_processed", "results", "figures", "tables", "maps"):
        Path(cfg["paths"][key]).mkdir(parents=True, exist_ok=True)
