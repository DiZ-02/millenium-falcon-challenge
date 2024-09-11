from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from falcon import DB_PLACEHOLDER
from falcon.config import init, init_config, parse_file, search_file
from falcon.models import Communication, Falcon
from tests import FIXTURES_DIR, TMP_DIR


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
def test_parse_file_with_error(filepath: Path) -> None:
    assert parse_file(filepath, Falcon) is None
    default = Falcon()
    assert parse_file(filepath, Falcon, default) == default


def test_parse_file() -> None:
    filepath = FIXTURES_DIR / "empire.json"
    expected = Communication(countdown=0, bounty_hunters=[])

    assert parse_file(filepath, Communication) == expected
    default = Communication()
    assert parse_file(filepath, Communication, default) == expected


@pytest.mark.parametrize(
    ("file", "expected_routes_db"),
    [("config-no_db.json", DB_PLACEHOLDER), ("config.json", FIXTURES_DIR / "universe.db")],
    ids=["db_not_found", "existing_db"],
)
def test_init_config(file: str, expected_routes_db: Path) -> None:
    filepath = FIXTURES_DIR / file
    cfg = init_config(filepath)
    assert cfg.autonomy == 6
    assert cfg.departure == "Tatooine"
    assert cfg.arrival == "Endor"
    assert cfg.routes_db == expected_routes_db


@patch("falcon.config.get_service")
def test_init_config_without_input_file(mock_get_service: Mock) -> None:
    mock_get_service.return_value = mock_service = Mock()
    _ = init(FIXTURES_DIR / "config.json")
    mock_service.add_params.assert_called_once()
    mock_service.add_graph.assert_called_once()
    mock_service.add_constraints.assert_not_called()


@patch("falcon.config.get_service")
def test_init_config_with_input_file_not_found(mock_get_service: Mock) -> None:
    mock_get_service.return_value = mock_service = Mock()
    _ = init(FIXTURES_DIR / "config.json", Path("file_not_found.txt"))
    mock_service.add_params.assert_called_once()
    mock_service.add_graph.assert_called_once()
    mock_service.add_constraints.assert_not_called()


@patch("falcon.config.get_service")
def test_init_config_with_wrong_input_file(mock_get_service: Mock) -> None:
    mock_get_service.return_value = mock_service = Mock()
    _ = init(FIXTURES_DIR / "config.json", FIXTURES_DIR / "config.json")
    mock_service.add_params.assert_called_once()
    mock_service.add_graph.assert_called_once()
    mock_service.add_constraints.assert_not_called()


@patch("falcon.config.get_service")
def test_init_config_with_input_file(mock_get_service: Mock) -> None:
    mock_get_service.return_value = mock_service = Mock()
    _ = init(FIXTURES_DIR / "config.json", FIXTURES_DIR / "empire.json")
    mock_service.add_params.assert_called_once()
    mock_service.add_graph.assert_called_once()
    mock_service.add_constraints.assert_called_once()
