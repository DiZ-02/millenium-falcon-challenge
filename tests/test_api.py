import json
from collections import defaultdict
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from falcon.adapter import PathStats
from falcon.api import HOME_RESPONSE_FMT, app
from falcon.models import SafePath
from falcon.store import MemoryStore, get_store
from tests import FIXTURES_DIR


def test_lifespan() -> None:
    with pytest.raises(ValueError, match="Set store before accessing it."):
        get_store()
    with TestClient(app):
        store = get_store()
        assert store is not None
        assert store.job is not None
        assert store.nodes is not None
        assert store.weights is not None
        assert store.costs == defaultdict(set)
    with pytest.raises(ValueError, match="Set store before accessing it."):
        get_store()


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
