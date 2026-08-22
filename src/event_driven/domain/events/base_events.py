"""Define general event class"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field


def utc_now() -> datetime:
    """Default timestamp closure"""
    return datetime.now(UTC)


class AbstractEvent(BaseModel):
    """Base class for all events"""

    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=utc_now)
    user_id: str
    event_key: str

    @computed_field
    def event_class_name(self) -> str:
        """Identifier of the event class"""
        return self.__class__.__name__
