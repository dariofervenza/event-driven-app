"""Random event to test queues"""

from pydantic import Field

from .base_events import AbstractEvent


class TestEvent(AbstractEvent):
    """Random test event"""

    __test__ = False

    value: int = Field(description="The random value carried by the test event.")
