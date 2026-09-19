"""Generic value objects shared across the ordering domain."""

from decimal import Decimal
from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class Currency(StrEnum):
    """ISO 4217 currency codes."""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"
    CAD = "CAD"
    AUD = "AUD"
    NZD = "NZD"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    INR = "INR"
    BRL = "BRL"
    ZAR = "ZAR"
    MXN = "MXN"
    KRW = "KRW"
    SGD = "SGD"
    AED = "AED"
    HKD = "HKD"


class Money(BaseModel):
    """Immutable monetary amount value object."""

    model_config: ClassVar = ConfigDict(frozen=True)

    amount: Decimal = Field(description="The monetary amount.")
    currency: Currency = Field(default=Currency.USD, description="The ISO currency code.")

    def __add__(self, other: Money) -> Money:
        """Sum two amounts that share the same currency."""
        if self.currency != other.currency:
            msg = "Cannot add amounts in different currencies"
            raise ValueError(msg)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __mul__(self, quantity: int) -> Money:
        """Scale an amount by a quantity."""
        return Money(amount=self.amount * quantity, currency=self.currency)
