"""Configuration for the pytest test suite."""
from collections.abc import Generator
from pathlib import Path

import pytest
from _pytest.fixtures import SubRequest
from fastapi.testclient import TestClient

from falcon.config import init
from falcon.store import MemoryStore, del_store, set_store
from tests import EXAMPLES_DIR, FIXTURES_DIR


@pytest.fixture
def store() -> MemoryStore:
    job, nodes, weights, costs = init(FIXTURES_DIR / "config.json")
    return MemoryStore(job, nodes, weights, costs)


@pytest.fixture
def client(store: MemoryStore) -> Generator[TestClient]:
    from falcon.api import app

    set_store(store)
    yield TestClient(app)
    del_store()


@pytest.fixture(params=["example1", "example2", "example3", "example4"])
def examples(request: SubRequest) -> tuple[Path, Path, Path]:
    folder_dir = EXAMPLES_DIR / request.param
    return (
        folder_dir / "millennium-falcon.json",
        folder_dir / "empire.json",
        folder_dir / "answer.json",
    )
