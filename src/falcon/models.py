from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, PositiveInt, StrictStr


def search_file(filepath: Path, folders: list[Path]) -> Path:
    """Search for a file at a given Path, then in folder list in order."""
    if not filepath.exists():
        for folder in folders:
            folder = Path(folder)
            if not folder.is_dir():
                continue
            if folder.joinpath(filepath).exists():
                filepath = folder.joinpath(filepath)
                break

    if filepath.is_file():
        return filepath
    raise FileNotFoundError


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
        return cls(**{k: v for k, v in zip(cls.__fields__.keys(), tpl, strict=False)})
