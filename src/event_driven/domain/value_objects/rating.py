"""Rating value objects."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from event_driven.settings import CFG


class Rating(BaseModel):
    """Customer rating captured after delivery."""

    model_config: ClassVar = ConfigDict(frozen=True)

    score: int = Field(
        ge=CFG.application.rating_min_score,
        le=CFG.application.rating_max_score,
        description="The rating score given by the customer.",
    )
