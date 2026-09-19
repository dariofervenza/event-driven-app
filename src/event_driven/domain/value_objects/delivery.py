"""Delivery value objects."""

from decimal import Decimal
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from .common import Money

_ZERO: Decimal = Decimal(0)


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
