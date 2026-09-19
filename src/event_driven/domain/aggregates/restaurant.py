"""Restaurant aggregate and its menu."""

from typing import ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from event_driven.domain.value_objects import MenuItem


class Menu(BaseModel):
    """A restaurant's menu: an immutable bag of items."""

    model_config: ClassVar = ConfigDict(frozen=True)

    items: list[MenuItem] = Field(default_factory=list, description="The menu items.")


class Restaurant(BaseModel):
    """A restaurant that serves menu items."""

    id: UUID = Field(default_factory=uuid4, description="The unique identifier of the restaurant.")
    name: str = Field(description="The restaurant's name.")
    is_open: bool = Field(default=True, description="Whether the restaurant is open for ordering.")
    menu: Menu = Field(default_factory=Menu, description="The restaurant's menu.")
