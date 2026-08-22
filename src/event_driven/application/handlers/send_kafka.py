"""Produce or consume test events"""

from event_driven.domain.events import AbstractEvent
from event_driven.domain.ports import AbstractProducer


def send_event(topic: str, event: AbstractEvent, producer: AbstractProducer):
    """Send any event with a producer"""
    producer.send_event(topic, event)
    producer.flush()
