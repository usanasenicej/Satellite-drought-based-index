import logging
import pytest

from adewi.logger import get_pipeline_logger, log_execution_time


def test_pipeline_logger():
    logger = get_pipeline_logger("test_adewi")
    assert isinstance(logger, logging.Logger)

    with log_execution_time(logger, "test_task") as info:
        x = sum(i for i in range(1000))
    assert "duration_sec" in info
    assert info["duration_sec"] >= 0.0
