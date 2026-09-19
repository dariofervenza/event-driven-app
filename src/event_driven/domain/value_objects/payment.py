"""Payment value objects."""

from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from .common import Money


class PaymentStatus(StrEnum):
    """Lifecycle of an up-front payment."""

    PAID = "paid"
    REFUNDED = "refunded"


class Payment(BaseModel):
    """Up-front payment collected when an order is placed."""

    model_config: ClassVar = ConfigDict(frozen=True)

    amount: Money = Field(description="The amount collected up front.")
    status: PaymentStatus = Field(default=PaymentStatus.PAID, description="The payment state.")
