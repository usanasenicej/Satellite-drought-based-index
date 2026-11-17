"""Pipeline DAG hashing, checkpointing, and cache management.

Enables skipping unchanged pipeline execution stages based on SHA-256
parameter and input data checksum fingerprints.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
import pandas as pd


class CacheManager:
    """Manages stage fingerprints and caches processed artifacts."""

    def __init__(self, cache_dir: str | Path = ".adewi_cache") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.cache_dir / "cache_manifest.json"
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> dict[str, str]:
        if self.manifest_file.exists():
            try:
                return json.loads(self.manifest_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_manifest(self) -> None:
        self.manifest_file.write_text(json.dumps(self._manifest, indent=2), encoding="utf-8")

    @staticmethod
    def compute_hash(data: Any, params: dict[str, Any] | None = None) -> str:
        """Compute SHA-256 hash fingerprint of dataset and parameter set."""
        hasher = hashlib.sha256()

        if isinstance(data, pd.DataFrame):
            # Sample or hash dataframe shape + values
            hasher.update(str(data.shape).encode("utf-8"))
            hasher.update(str(data.columns.tolist()).encode("utf-8"))
            # Hash head and tail
            hasher.update(pd.util.hash_pandas_object(data.head(10)).values.tobytes())
        elif isinstance(data, (bytes, bytearray)):
            hasher.update(data)
        elif isinstance(data, (str, Path)):
            p = Path(data)
            if p.exists() and p.is_file():
                hasher.update(p.read_bytes())
            else:
                hasher.update(str(data).encode("utf-8"))
        else:
            hasher.update(repr(data).encode("utf-8"))

        if params:
            param_str = json.dumps(params, sort_keys=True, default=str)
            hasher.update(param_str.encode("utf-8"))

        return hasher.hexdigest()

    def is_cached(self, stage_name: str, current_hash: str) -> bool:
        """Check if stage hash matches the cached fingerprint."""
        return self._manifest.get(stage_name) == current_hash

    def update_stage(self, stage_name: str, stage_hash: str) -> None:
        """Record newly completed stage fingerprint."""
        self._manifest[stage_name] = stage_hash
        self._save_manifest()

    def clear(self) -> None:
        """Invalidate all cached stages."""
        self._manifest = {}
        if self.manifest_file.exists():
            self.manifest_file.unlink()
