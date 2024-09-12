from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt, StrictFloat, StrictStr


class Falcon(BaseModel):
    model_config = ConfigDict(extra="forbid")

    autonomy: PositiveInt = 1
    departure: StrictStr = "Tatooine"
    arrival: StrictStr = "Endor"
    routes_db: Path = Path("placeholder.db")


class Route(BaseModel):
    origin: StrictStr
    destination: StrictStr
    travel_time: PositiveInt


class BountyHunter(BaseModel):
    planet: StrictStr
    day: PositiveInt


class Communication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    countdown: NonNegativeInt = 0
    bounty_hunters: list[BountyHunter] = Field(default_factory=list)


class SafePath(BaseModel):
    odds: StrictFloat
