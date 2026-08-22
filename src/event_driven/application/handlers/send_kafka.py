"""Produce or consume test events"""

from event_driven.domain.events.base_events import AbstractEvent
from event_driven.infrastructure.messagebus.producer import AbstractProducer


def send_event(topic: str, event: AbstractEvent, producer: AbstractProducer):
    """Send any event with a producer"""
    producer.send_event(topic, event)
    producer.flush()
