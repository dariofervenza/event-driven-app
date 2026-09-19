"""Courier aggregate."""

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CourierState(StrEnum):
    """State of a courier."""

    AVAILABLE = "available"
    ON_DELIVERY = "on_delivery"


class Courier(BaseModel):
    """A courier who delivers orders."""

    id: UUID = Field(default_factory=uuid4, description="The unique identifier of the courier.")
    name: str = Field(description="The courier's name.")
    state: CourierState = Field(default=CourierState.AVAILABLE, description="The courier's current state.")
    active_order_id: UUID | None = Field(
        default=None,
        description="The id of the active (undelivered) order, if any.",
    )
