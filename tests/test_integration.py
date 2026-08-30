"""Integration test: run start_queues end-to-end against a live broker."""

import socket
import subprocess
import sys

import pytest


def _broker_available() -> bool:
    """Return True if a Kafka broker is reachable on localhost:9092."""
    try:
        with socket.create_connection(("localhost", 9092), timeout=1):
            return True
    except OSError:
        return False


@pytest.mark.integration
def test_start_queues_subprocess() -> None:
    """start_queues creates the configured topics against a live broker."""
    if not _broker_available():
        pytest.skip("Kafka not available")
    result = subprocess.run(
        [sys.executable, "-m", "event_driven.start_queues"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
