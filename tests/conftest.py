"""Configuration for the pytest test suite."""

from pathlib import Path

import pytest
from _pytest.fixtures import SubRequest
from fastapi.testclient import TestClient

from tests import EXAMPLES_DIR


@pytest.fixture
def client() -> TestClient:
    from falcon.api import app

    return TestClient(app)


@pytest.fixture(params=["example1", "example2", "example3", "example4"])
def examples(request: SubRequest) -> tuple[Path, Path, Path]:
    folder_dir = EXAMPLES_DIR / request.param
    return (
        folder_dir / "millennium-falcon.json",
        folder_dir / "empire.json",
        folder_dir / "answer.json",
    )
