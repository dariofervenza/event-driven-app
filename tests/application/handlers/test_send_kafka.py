"""Tests for the send_event handler (producer delegation)."""

import pytest
from tests.fakes import FakeEventProducer

from event_driven.application.handlers.topics.send_kafka import send_event
from event_driven.domain.events import TestEvent


@pytest.mark.application
@pytest.mark.unit
def test_send_event_delegates_and_flushes() -> None:
    """send_event sends via the producer and flushes."""
    producer = FakeEventProducer()
    event = TestEvent(user_id="u", event_key="k", value=1)
    send_event("test_queue", event, producer)
    assert len(producer.sent) == 1
    assert producer.flushed == 1
