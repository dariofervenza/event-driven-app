"""Order aggregate (core)."""

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from event_driven.domain.value_objects import (
    DeliveryFee,
    OrderLine,
    Payment,
    PaymentStatus,
    Rating,
)


class OrderStatus(StrEnum):
    """Lifecycle state of an order."""

    CREATED = "created"
    PLACED = "placed"
    PREPARING = "preparing"
    READY = "ready"
    HANDED_TO_COURIER = "handed_to_courier"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUSED = "refused"


class InvalidTransitionError(ValueError):
    """Raised when an order transition violates its lifecycle invariants."""


class Order(BaseModel):
    """A food order placed by a customer at a restaurant."""

    id: UUID = Field(default_factory=uuid4, description="The unique identifier of the order.")
    customer_id: UUID = Field(description="The id of the customer placing the order.")
    restaurant_id: UUID = Field(description="The id of the restaurant the order is placed at.")
    courier_id: UUID | None = Field(
        default=None,
        description="The id of the courier assigned to the order, if any.",
    )
    lines: list[OrderLine] = Field(description="The order lines captured at order time.")
    payment: Payment = Field(description="The up-front payment collected for the order.")
    delivery_fee: DeliveryFee = Field(description="The delivery fee applied to the order.")
    status: OrderStatus = Field(default=OrderStatus.CREATED, description="The order lifecycle state.")
    rating: Rating | None = Field(default=None, description="The rating given after delivery, if any.")

    def place(self) -> None:
        """Place the order; requires the up-front payment to have been collected."""
        if self.status is not OrderStatus.CREATED:
            msg = f"Cannot place an order in state {self.status.value}"
            raise InvalidTransitionError(msg)
        if self.payment.status is not PaymentStatus.PAID:
            msg = "Cannot place an order without collected payment"
            raise InvalidTransitionError(msg)
        self.status = OrderStatus.PLACED

    def start_preparation(self) -> None:
        """Begin preparing the placed order."""
        if self.status is not OrderStatus.PLACED:
            msg = f"Cannot start preparation in state {self.status.value}"
            raise InvalidTransitionError(msg)
        self.status = OrderStatus.PREPARING

    def mark_ready(self) -> None:
        """Mark the preparing order as ready."""
        if self.status is not OrderStatus.PREPARING:
            msg = f"Cannot mark ready in state {self.status.value}"
            raise InvalidTransitionError(msg)
        self.status = OrderStatus.READY

    def assign_courier(self, courier_id: UUID) -> None:
        """Hand the ready order to a courier."""
        if self.status is not OrderStatus.READY:
            msg = f"Cannot assign a courier in state {self.status.value}"
            raise InvalidTransitionError(msg)
        self.courier_id = courier_id
        self.status = OrderStatus.HANDED_TO_COURIER

    def mark_delivered(self) -> None:
        """Mark the in-transit order as delivered."""
        if self.status is not OrderStatus.HANDED_TO_COURIER:
            msg = f"Cannot mark delivered in state {self.status.value}"
            raise InvalidTransitionError(msg)
        self.status = OrderStatus.DELIVERED

    def cancel(self) -> None:
        """Cancel the order; only allowed while it is still being prepared."""
        if self.status not in {OrderStatus.PLACED, OrderStatus.PREPARING}:
            msg = f"Cannot cancel an order in state {self.status.value}"
            raise InvalidTransitionError(msg)
        self.status = OrderStatus.CANCELLED

    def refuse(self) -> None:
        """Refuse the order (restaurant); refunds the up-front payment."""
        if self.status in {OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.REFUSED}:
            msg = f"Cannot refuse an order in state {self.status.value}"
            raise InvalidTransitionError(msg)
        self.status = OrderStatus.REFUSED
        self.payment = self.payment.model_copy(update={"status": PaymentStatus.REFUNDED})

    def rate(self, score: int) -> None:
        """Rate the delivered order."""
        if self.status is not OrderStatus.DELIVERED:
            msg = f"Cannot rate an order in state {self.status.value}"
            raise InvalidTransitionError(msg)
        self.rating = Rating(score=score)
