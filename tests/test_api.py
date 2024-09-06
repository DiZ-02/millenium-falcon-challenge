import json
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from falcon.api import HOME_RESPONSE_FMT
from falcon.models import Communication, SafePath
from tests import FIXTURES_DIR


def test_read_root(client: TestClient) -> None:
    endpoint = "/"
    domain = "http://test"
    body = HOME_RESPONSE_FMT.format(domain)
    assert client.get(domain + endpoint).text == body


@patch("falcon.api.get_service")
def test_upload_communication(mock_get_service: Mock, client: TestClient) -> None:
    mock_get_service.return_value = mock_service = Mock()
    argument = Communication(countdown=1, bounty_hunters=[])
    with (FIXTURES_DIR / "empire.json").open() as input_file:
        json_input = json.loads(input_file.read())

    response = client.post("/communication", json=json_input)
    assert response.json() == json_input
    mock_service.add_constraints.assert_called_once_with(argument)


@patch("falcon.api.get_service")
def test_compute_odds(mock_get_service: Mock, client: TestClient) -> None:
    mock_get_service.return_value = mock_service = Mock()
    mock_service.search_path.return_value = SafePath(odds=1.0)

    response = client.post("/compute_odds")
    assert response.status_code == 200
    assert response.json().get("odds") == 1.0
    mock_service.search_path.assert_called_once()
