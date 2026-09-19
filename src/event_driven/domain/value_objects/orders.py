"""Order-scoped value objects."""

from decimal import Decimal
from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, computed_field

from event_driven.settings import CFG

from .common import Money

_ZERO: Decimal = Decimal(0)


class MenuItem(BaseModel):
    """A single item a restaurant can sell."""

    model_config: ClassVar = ConfigDict(frozen=True)

    id: str = Field(description="The menu item identifier.")
    name: str = Field(description="The human-readable item name.")
    price: Money = Field(description="The price of a single unit.")


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


class PaymentStatus(StrEnum):
    """Lifecycle of an up-front payment."""

    PAID = "paid"
    REFUNDED = "refunded"


class Payment(BaseModel):
    """Up-front payment collected when an order is placed."""

    model_config: ClassVar = ConfigDict(frozen=True)

    amount: Money = Field(description="The amount collected up front.")
    status: PaymentStatus = Field(default=PaymentStatus.PAID, description="The payment state.")


class DeliveryFee(BaseModel):
    """Fee applied to an order; waived for large enough orders."""

    model_config: ClassVar = ConfigDict(frozen=True)

    amount: Money = Field(description="The fee amount to charge.")
    waived: bool = Field(default=False, description="Whether the fee was waived for a large enough order.")

    @classmethod
    def for_subtotal(cls, subtotal: Money, base_fee: Money, free_threshold: Money) -> DeliveryFee:
        """Compute the fee from the order subtotal and the free-delivery threshold."""
        if subtotal.amount >= free_threshold.amount:
            return cls(amount=Money(amount=_ZERO, currency=subtotal.currency), waived=True)
        return cls(amount=base_fee, waived=False)


class Rating(BaseModel):
    """Customer rating captured after delivery."""

    model_config: ClassVar = ConfigDict(frozen=True)

    score: int = Field(
        ge=CFG.application.rating_min_score,
        le=CFG.application.rating_max_score,
        description="The rating score given by the customer.",
    )
