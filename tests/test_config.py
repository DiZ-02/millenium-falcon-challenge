from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import Json, ValidationError

from falcon import DB_PLACEHOLDER
from falcon.config import M, init, init_config, parse_file, search_file
from falcon.models import BountyHunter, Communication, Falcon, Route, SafePath
from tests import FIXTURES_DIR, TMP_DIR


@pytest.mark.parametrize(
    ("model", "model_dump"),
    [
        (Falcon, {}),
        (Route, {"origin": "a", "destination": "b", "travel_time": 1}),
        (BountyHunter, {"planet": "a", "day": 0}),
        (Communication, {}),
        (SafePath, {"odds": 0}),
    ],
)
def test_parse_models(model: type[M], model_dump: Json) -> None:
    assert model.model_validate(model_dump) == model(**model_dump)
    model_dump["extra"] = "forbid"
    with pytest.raises(ValidationError):
        model.model_validate_json(model_dump)


def test_search_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        search_file(Path("file_not_found.txt"))


def test_search_file_direct_path() -> None:
    path = FIXTURES_DIR / "empire.json"
    assert search_file(path) == path


def test_search_file_in_folders() -> None:
    file = "empire.json"

    with pytest.raises(FileNotFoundError):
        search_file(Path(file), [TMP_DIR])

    assert search_file(Path(file), [FIXTURES_DIR]) == FIXTURES_DIR / file
    assert search_file(Path(file), [TMP_DIR, FIXTURES_DIR]) == FIXTURES_DIR / file


@pytest.mark.parametrize(
    "filepath",
    [Path("file_not_found.txt"), Path(__file__), FIXTURES_DIR / "empire.json"],
    ids=["file_not_found", "not_json", "wrong_model"],
)
def test_parse_file_with_error_on_file(filepath: Path) -> None:
    assert parse_file(filepath, Falcon) is None


def test_parse_file() -> None:
    filepath = FIXTURES_DIR / "empire.json"
    expected = Communication(countdown=0, bounty_hunters=[BountyHunter(planet="Tatooine", day=0)])

    assert parse_file(filepath, Communication) == expected


@pytest.mark.parametrize(
    ("file", "expected_routes_db", "expected_autonomy"),
    [
        ("file_not_found.txt", DB_PLACEHOLDER, 1),
        ("config-no_db.json", DB_PLACEHOLDER, 6),
        ("config.json", FIXTURES_DIR / "universe.db", 6),
    ],
    ids=["file_not_found", "db_not_found", "existing_db"],
)
def test_init_config(file: str, expected_routes_db: Path, expected_autonomy: int) -> None:
    filepath = FIXTURES_DIR / file
    cfg = init_config(filepath)
    assert cfg.autonomy == expected_autonomy
    assert cfg.departure == "Tatooine"
    assert cfg.arrival == "Endor"
    assert cfg.routes_db == expected_routes_db


@pytest.mark.parametrize(
    "filepath",
    [Path("file_not_found.txt"), Path(__file__), FIXTURES_DIR / "config.json"],
    ids=["no_file", "file_not_found", "wrong_file"],
)
@patch("falcon.config.Job")
def test_init_input_file_ko(mock_job: Mock, filepath: Path) -> None:
    job = mock_job.from_config.return_value
    job.generate_graph.return_value = (None, None)

    init(FIXTURES_DIR / "config.json", filepath)

    job.generate_graph.assert_called_once()
    job.add_constraints.assert_not_called()


@patch("falcon.config.Job")
def test_init_with_input_file(mock_job: Mock) -> None:
    job = mock_job.from_config.return_value
    job.generate_graph.return_value = (None, None)
    argument = Communication(countdown=0, bounty_hunters=[BountyHunter(planet="Tatooine", day=0)])

    init(FIXTURES_DIR / "config.json", FIXTURES_DIR / "empire.json")

    job.generate_graph.assert_called_once()
    job.add_constraints.assert_called_once_with(argument)
