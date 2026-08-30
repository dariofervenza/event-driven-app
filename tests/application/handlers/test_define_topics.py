"""Tests for the topic (queue) creation/deletion handlers."""

import pytest
from tests.fakes import FakeInitQueues

from event_driven.application.handlers import handle_queue_creation, handle_queue_deletion
from event_driven.domain.commands import CreateTopicsCommand, DeleteTopicsCommand, QueueConfig


@pytest.mark.application
@pytest.mark.unit
def test_handle_queue_creation() -> None:
    """handle_queue_creation forwards queues/server_url to the initializer."""
    fake = FakeInitQueues()
    queues = [QueueConfig(queue_name="test", num_partitions=1, replication_factor=1)]
    command = CreateTopicsCommand(queues=queues, server_url="dummy")
    handle_queue_creation(command, fake)
    assert fake.created["dummy"] == queues


@pytest.mark.application
@pytest.mark.unit
def test_handle_queue_deletion() -> None:
    """handle_queue_deletion forwards topic_names/server_url to the initializer."""
    fake = FakeInitQueues()
    command = DeleteTopicsCommand(topic_names=["a"], server_url="dummy")
    handle_queue_deletion(command, fake)
    assert fake.deleted["dummy"] == ["a"]
