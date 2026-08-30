"""Tests for the logging configuration helpers."""

from pathlib import Path

import pytest

from event_driven.logging import read_logging_config, setup_logging


@pytest.mark.unit
def test_read_logging_config_returns_dict() -> None:
    """read_logging_config parses settings/logging.yaml into a dict."""
    config = read_logging_config()
    assert "root" in config
    assert "handlers" in config


@pytest.mark.unit
def test_setup_logging_returns_role_logger() -> None:
    """setup_logging returns a logger named after the given role."""
    logger = setup_logging("unit_test_role")
    assert logger.name == "unit_test_role"


@pytest.mark.unit
def test_setup_logging_writes_file() -> None:
    """setup_logging creates a per-role log file under logs/."""
    setup_logging("unit_test_role")
    assert (Path("logs") / "unit_test_role.log").exists()
