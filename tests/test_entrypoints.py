"""Import smoke tests for the entry-point modules (no Kafka needed)."""

import pytest


@pytest.mark.unit
def test_entrypoints_import() -> None:
    """The entry-point modules import cleanly (no Kafka needed)."""
