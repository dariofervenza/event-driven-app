"""Tests for the random test-event producer handlers."""

import pytest
from tests.fakes import FakeEventProducer

from event_driven.application.handlers import periodically_send_random_test_event
from event_driven.application.handlers.topics.random import send_random_test_event


@pytest.mark.application
@pytest.mark.unit
def test_send_random_test_event() -> None:
    """send_random_test_event sends a TestEvent via the producer."""
    producer = FakeEventProducer()
    send_random_test_event("test_queue", producer)
    assert len(producer.sent) == 1
    topic, event = producer.sent[0]
    assert topic == "test_queue"
    assert event.value >= 1
    assert event.user_id.startswith("random_user_")
    assert event.event_key.startswith("random_")


@pytest.mark.application
@pytest.mark.unit
def test_periodically_sends_until_interrupt() -> None:
    """periodically_send_random_test_event loops until KeyboardInterrupt."""
    producer = FakeEventProducer(send_raises=KeyboardInterrupt())
    periodically_send_random_test_event(0, "test_queue", producer)
