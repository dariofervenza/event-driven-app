"""Menu value objects."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from .common import Money


class MenuItem(BaseModel):
    """A single item a restaurant can sell."""

    model_config: ClassVar = ConfigDict(frozen=True)

    id: str = Field(description="The menu item identifier.")
    name: str = Field(description="The human-readable item name.")
    price: Money = Field(description="The price of a single unit.")
