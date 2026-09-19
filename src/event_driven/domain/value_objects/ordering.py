"""Ordering value objects."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .common import Money


class OrderLine(BaseModel):
    """Snapshot of a menu item captured on an order."""

    model_config: ClassVar = ConfigDict(frozen=True)

    item_id: str = Field(description="The menu item identifier this line refers to.")
    name: str = Field(description="The item name captured at order time.")
    unit_price: Money = Field(description="The price of a single unit captured at order time.")
    quantity: int = Field(gt=0, description="The number of units ordered.")

    @computed_field
    def total(self) -> Money:
        """Total cost of this line (unit price times quantity)."""
        return self.unit_price * self.quantity
