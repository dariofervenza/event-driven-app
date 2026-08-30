"""Tests for the in-memory ListenerThread."""

import pytest
from tests.fakes import FakeEventReceiver

from event_driven.domain.events import TestEvent
from event_driven.infrastructure.messagebus.inmemory import ListenerThread


@pytest.mark.infrastructure
@pytest.mark.unit
def test_run_delegates_to_receiver() -> None:
    """ListenerThread.run calls receiver.start_listening with the event classes."""
    receiver = FakeEventReceiver()
    listener = ListenerThread(receiver=receiver, event_classes=[TestEvent])
    listener.run()
    assert receiver.event_classes == [TestEvent]


@pytest.mark.infrastructure
@pytest.mark.unit
def test_is_daemon() -> None:
    """The listener thread is configured as a daemon thread."""
    receiver = FakeEventReceiver()
    listener = ListenerThread(receiver=receiver, event_classes=[TestEvent])
    assert listener.daemon is True
