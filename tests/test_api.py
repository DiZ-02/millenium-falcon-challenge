import json
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from falcon.adapter import PathStats
from falcon.api import HOME_RESPONSE_FMT
from falcon.models import SafePath
from falcon.store import MemoryStore
from tests import FIXTURES_DIR


def test_read_root(client: TestClient) -> None:
    endpoint = "/"
    domain = "http://test"
    body = HOME_RESPONSE_FMT.format(domain)
    assert client.get(domain + endpoint).text == body


def test_upload_communication(store: MemoryStore, client: TestClient) -> None:
    with (FIXTURES_DIR / "empire.json").open() as input_file:
        json_input = json.loads(input_file.read())

    response = client.post("/communication", json=json_input)
    assert store.costs is not None
    assert response.json() == json_input


@patch("falcon.api.PathService")
def test_compute_odds(mock_path_service: Mock, client: TestClient) -> None:
    mock_path_service.return_value.search_path.return_value = PathStats(cost=1, total_weight=0, available_weight=0)

    response = client.post("/compute_odds")
    mock_path_service.return_value.search_path.assert_called_once()
    assert response.status_code == 200
    assert response.json() == SafePath(odds=0.9).model_dump()
