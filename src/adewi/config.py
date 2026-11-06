"""Configuration loading, validation, and directory management for ADEWI.

Provides utilities to read and validate the YAML configuration, resolve file paths
relative to the repository root, and ensure required output directories exist.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "config.yaml"


@lru_cache(maxsize=4)
def _read_yaml(cfg_path_str: str) -> dict[str, Any]:
    """Read raw YAML file from disk with simple LRU caching."""
    with Path(cfg_path_str).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    """Load and resolve study configuration.

    Reads the YAML configuration file, converts relative directory paths in
    the ``paths`` and ``validation`` sections to absolute paths relative to
    the project root, and validates key configuration sections.

    Parameters
    ----------
    path : Path or str, optional
        Path to a custom YAML configuration file. If omitted, defaults to
        ``config/config.yaml`` at the repository root.

    Returns
    -------
    dict of str -> Any
        Resolved configuration dictionary.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    ValueError
        If required configuration sections are missing.
    """
    cfg_file = Path(path).resolve() if path else DEFAULT_CONFIG
    if not cfg_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {cfg_file}")

    # Deep copy the cached dictionary so caller mutations don't corrupt cache
    raw_dict = _read_yaml(str(cfg_file))
    import copy
    cfg = copy.deepcopy(raw_dict)

    # Resolve paths under 'paths' section
    for key, rel in cfg.get("paths", {}).items():
        cfg["paths"][key] = str((ROOT / rel).resolve())

    # Resolve crop_stats_file if specified
    if "validation" in cfg and "crop_stats_file" in cfg["validation"]:
        crop_file = cfg["validation"]["crop_stats_file"]
        cfg["validation"]["crop_stats_file"] = str((ROOT / crop_file).resolve())

    # Validate essential sections
    required_sections = ("paths", "weights", "drought")
    missing = [sec for sec in required_sections if sec not in cfg]
    if missing:
        raise ValueError(f"Missing required configuration section(s): {', '.join(missing)}")

    return cfg


def ensure_dirs(cfg: dict[str, Any]) -> None:
    """Ensure all configured output directories exist on disk.

    Parameters
    ----------
    cfg : dict of str -> Any
        Configuration dictionary containing the ``paths`` mapping.
    """
    paths_dict = cfg.get("paths", {})
    for path_str in paths_dict.values():
        Path(path_str).mkdir(parents=True, exist_ok=True)
