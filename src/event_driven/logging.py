"""Load logging config from settings/logging.yaml and expose the app logger."""

import logging
import logging.config
from pathlib import Path

import yaml

LOGS_DIR = Path("logs")
LOGGING_CONFIG_FILE = Path(__file__).resolve().parent / "settings" / "logging.yaml"


def read_logging_config() -> dict:
    """Read the logging config (settings/logging.yaml) and return it as a dict."""
    with LOGGING_CONFIG_FILE.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging(role: str) -> logging.Logger:
    """Configure logging for `role` and return its logger."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config = read_logging_config()
    config["handlers"]["file"]["filename"] = str(LOGS_DIR / f"{role}.log")
    logging.config.dictConfig(config)
    return logging.getLogger(role)


__all__ = ["read_logging_config", "setup_logging"]
