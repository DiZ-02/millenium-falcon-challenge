"""Configuration for the pytest test suite."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    from falcon.api import app

    return TestClient(app)
