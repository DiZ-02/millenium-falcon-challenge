from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt, StrictFloat, StrictStr

from falcon import DB_PLACEHOLDER


class ForbidExtraFieldsModel(BaseModel):
    """Forbid extra fields in models interacting with the user."""

    model_config = ConfigDict(extra="forbid")


class Falcon(ForbidExtraFieldsModel):
    autonomy: PositiveInt = 1
    departure: StrictStr = "Tatooine"
    arrival: StrictStr = "Endor"
    routes_db: Path = DB_PLACEHOLDER


class Route(ForbidExtraFieldsModel):
    origin: StrictStr
    destination: StrictStr
    travel_time: PositiveInt


class BountyHunter(ForbidExtraFieldsModel):
    planet: StrictStr
    day: NonNegativeInt


class Communication(ForbidExtraFieldsModel):
    countdown: NonNegativeInt = 0
    bounty_hunters: list[BountyHunter] = Field(default_factory=list)


class SafePath(ForbidExtraFieldsModel):
    odds: StrictFloat
