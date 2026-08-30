"""Tests for the bootstrap DependencyContainer (DI wiring)."""

import pytest

from event_driven.bootstrap import DependencyContainer
from event_driven.domain.events import TestEvent
from event_driven.infrastructure.messagebus.inmemory import ListenerThread, TestHandler, ThreadSafeQueue
from event_driven.infrastructure.messagebus.kafka import KafkaInitQueues, KafkaProducer, KafkaReceiver


@pytest.fixture(autouse=True)
def _reset_container():
    """Reset the DependencyContainer singleton state around each test."""
    DependencyContainer._singleton = None
    DependencyContainer._default_queue = None
    yield
    DependencyContainer._singleton = None
    DependencyContainer._default_queue = None


@pytest.mark.unit
def test_get_container_is_singleton() -> None:
    """DependencyContainer.get_container returns the same singleton instance."""
    c = DependencyContainer.get_container()
    assert c is DependencyContainer.get_container()


@pytest.mark.unit
def test_get_container_with_queue_has_queue() -> None:
    """DependencyContainer.get_container_with_queue returns a container with an in-memory queue."""
    c = DependencyContainer.get_container_with_queue()
    assert c._default_queue is not None
    assert isinstance(c.queue, ThreadSafeQueue)


@pytest.mark.unit
def test_properties_lazily_create_components() -> None:
    """Each DependencyContainer property lazily builds its component."""
    c = DependencyContainer()
    assert isinstance(c.init_queues, KafkaInitQueues)
    assert isinstance(c.producer, KafkaProducer)
    assert isinstance(c.receiver, KafkaReceiver)
    assert isinstance(c.queue, ThreadSafeQueue)
    assert isinstance(c.listener_thread, ListenerThread)
    assert isinstance(c.test_handler, TestHandler)


@pytest.mark.unit
def test_event_classes_lists_registered_events() -> None:
    """DependencyContainer.event_classes lists all registered event classes."""
    c = DependencyContainer()
    assert TestEvent in c.event_classes


@pytest.mark.unit
def test_current_topic_getter_setter() -> None:
    """DependencyContainer.current_topic get/set works."""
    c = DependencyContainer()
    c.current_topic = "test_queue"
    assert c.current_topic == "test_queue"


@pytest.mark.unit
def test_get_all_returns_components() -> None:
    """DependencyContainer.get_all returns the component dict."""
    c = DependencyContainer()
    all_components = c.get_all()
    assert set(all_components) == {"init_queues", "producer", "receiver", "queue", "event_classes"}
