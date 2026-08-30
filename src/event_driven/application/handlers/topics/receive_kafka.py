"""Produce or consume test events"""

from collections.abc import Sequence

from event_driven.domain.events import AbstractEvent
from event_driven.domain.ports import AbstractReceiver


def receive_events(receiver: AbstractReceiver, event_classes: Sequence[type[AbstractEvent]]):
    """Receive events and transform them into model instances"""
    receiver.start_listening(event_classes)
