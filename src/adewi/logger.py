"""Structured telemetry, timing, and JSON execution logging."""

from __future__ import annotations

from contextlib import contextmanager
import json
import logging
from pathlib import Path
import time
from typing import Any, Generator


class JsonLogFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj.update(record.extra_data)
        return json.dumps(log_obj)


def get_pipeline_logger(name: str = "adewi", log_file: str | Path | None = None) -> logging.Logger:
    """Configure structured pipeline logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(JsonLogFormatter())
        logger.addHandler(ch)
        if log_file:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(JsonLogFormatter())
            logger.addHandler(fh)
    return logger


@contextmanager
def log_execution_time(logger: logging.Logger, task_name: str) -> Generator[dict[str, Any], None, None]:
    """Context manager measuring execution duration and logging telemetry."""
    start = time.perf_counter()
    info: dict[str, Any] = {"task": task_name}
    try:
        yield info
    finally:
        duration = time.perf_counter() - start
        info["duration_sec"] = round(duration, 4)
        logger.info(f"Finished {task_name} in {duration:.4f}s", extra={"extra_data": info})
