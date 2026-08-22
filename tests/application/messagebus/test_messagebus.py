"""Test that the message bus creates, send and recevies topics"""

import pytest

from event_driven.application.handlers import (
    handle_queue_creation,
    handle_queue_deletion,
)
from event_driven.domain.commands import CreateTopicsCommand, DeleteTopicsCommand, QueueConfig
from event_driven.domain.ports import AbstractInitQueues


@pytest.fixture
def fake_initializator_fixture() -> AbstractInitQueues:
    """Helper to test application handler calls proper methods"""

    class FakeInitQueues:
        """Fake initializator"""

        def __init__(self):
            self.registered_topics = {}

        def create_queues(self, queues: list[QueueConfig], server_url: str):
            self.registered_topics[server_url] = queues

        def delete_queues(self, topic_names: list[str], server_url: str):
            del topic_names
            if server_url in self.registered_topics:
                self.registered_topics.pop(server_url)

    return FakeInitQueues()


def test_topic_creaton(request: pytest.FixtureRequest):
    """Tests that applicaiton handler actually calls the creation contract method"""
    initializator = request.getfixturevalue("fake_initializator_fixture")
    queues = [QueueConfig(queue_name="test", num_partitions=1, replication_factor=1)]
    command = CreateTopicsCommand(queues=queues, server_url="dummy")
    handle_queue_creation(command, initializator)
    assert len(initializator.registered_topics) == 1
    assert initializator.registered_topics["dummy"] == queues


def test_topic_deletion(request: pytest.FixtureRequest):
    """Tests that applicaiton handler actually calls the creation contract method"""
    initializator = request.getfixturevalue("fake_initializator_fixture")
    queues = [
        QueueConfig(queue_name="test", num_partitions=1, replication_factor=1),
        QueueConfig(queue_name="test2", num_partitions=1, replication_factor=1),
    ]
    command = CreateTopicsCommand(queues=queues, server_url="dummy")
    handle_queue_creation(command, initializator)
    assert len(initializator.registered_topics["dummy"]) == 2
    handle_queue_deletion(DeleteTopicsCommand(topic_names=["a"], server_url="dummy"), initializator)
    assert len(initializator.registered_topics) == 0
