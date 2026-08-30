"""Tests for the domain command value objects (queue/topic commands)."""

import pytest
from pydantic import ValidationError

from event_driven.domain.commands import CreateTopicsCommand, DeleteTopicsCommand, QueueConfig


@pytest.mark.domain
@pytest.mark.unit
def test_queue_config_fields() -> None:
    """QueueConfig stores queue_name/num_partitions/replication_factor."""
    cfg = QueueConfig(queue_name="q", num_partitions=3, replication_factor=1)
    assert cfg.queue_name == "q"
    assert cfg.num_partitions == 3
    assert cfg.replication_factor == 1


@pytest.mark.domain
@pytest.mark.unit
def test_create_topics_command_fields() -> None:
    """CreateTopicsCommand stores the queues and the server URL."""
    queues = [QueueConfig(queue_name="q", num_partitions=1, replication_factor=1)]
    command = CreateTopicsCommand(queues=queues, server_url="url")
    assert command.queues == queues
    assert command.server_url == "url"


@pytest.mark.domain
@pytest.mark.unit
def test_delete_topics_command_fields() -> None:
    """DeleteTopicsCommand stores the topic names and the server URL."""
    command = DeleteTopicsCommand(topic_names=["a", "b"], server_url="url")
    assert command.topic_names == ["a", "b"]
    assert command.server_url == "url"


@pytest.mark.domain
@pytest.mark.unit
def test_commands_require_fields() -> None:
    """Constructing a command without required fields raises ValidationError."""
    with pytest.raises(ValidationError):
        CreateTopicsCommand.model_validate({})
