"""Customer aggregate."""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Customer(BaseModel):
    """A customer who places orders."""

    id: UUID = Field(default_factory=uuid4, description="The unique identifier of the customer.")
    name: str = Field(description="The customer's name.")
    contact: str = Field(description="The customer's contact details.")
    address: str = Field(description="The customer's delivery address.")
