"""Order aggregate (core)."""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from event_driven.domain.value_objects import DeliveryFee, OrderLine, Payment, Rating


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
    rating: Rating | None = Field(default=None, description="The rating given after delivery, if any.")
