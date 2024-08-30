from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, PositiveInt, StrictStr


class Falcon(BaseModel):
    autonomy: PositiveInt = 0
    departure: StrictStr = "Tatooine"
    arrival: StrictStr = "Endor"
    routes_db: Path = Path("placeholder.db")


class Route(BaseModel):
    origin: StrictStr
    destination: StrictStr
    travel_time: PositiveInt

    @classmethod
    def from_list(cls, tpl: Sequence):
        return cls(**{k: v for k, v in zip(cls.model_fields.keys(), tpl, strict=False)})


class BountyHunter(BaseModel):
    planet: StrictStr
    day: PositiveInt


class Communication(BaseModel):
    countdown: PositiveInt
    bounty_hunters: list[BountyHunter]
