from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt, StrictFloat, StrictStr, model_validator

from falcon import DB_PLACEHOLDER


class CaseInsensitiveModel(BaseModel):
    @model_validator(mode="before")
    def _lowercase_property_keys_(cls, values: Any) -> Any:  # noqa: N805
        def _lower_(value: Any) -> Any:
            if isinstance(value, dict):
                return {k.lower(): _lower_(v) for k, v in value.items()}
            return value

        return _lower_(values)


class ForbidExtraFieldsModel(CaseInsensitiveModel):
    """Forbid extra fields in models interacting with the user."""

    model_config = ConfigDict(extra="forbid")


class Falcon(ForbidExtraFieldsModel):
    autonomy: PositiveInt = 1
    departure: StrictStr = Field(min_length=1, default="Tatooine")
    arrival: StrictStr = Field(min_length=1, default="Endor")
    routes_db: Path = DB_PLACEHOLDER


class Route(ForbidExtraFieldsModel):
    origin: StrictStr = Field(min_length=1)
    destination: StrictStr = Field(min_length=1)
    travel_time: PositiveInt


class BountyHunter(ForbidExtraFieldsModel):
    planet: StrictStr = Field(min_length=1)
    day: NonNegativeInt


class Communication(ForbidExtraFieldsModel):
    countdown: NonNegativeInt = 0
    bounty_hunters: list[BountyHunter] = Field(default_factory=list)


class SafePath(ForbidExtraFieldsModel):
    odds: StrictFloat
