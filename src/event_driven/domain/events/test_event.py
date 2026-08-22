"""Random event to test queues"""

from .base_events import AbstractEvent


class TestEvent(AbstractEvent):
    """Random test event"""

    value: int
