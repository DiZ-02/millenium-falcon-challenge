from dataclasses import dataclass

from falcon.adapter import Costs, Job, Nodes, Weights


@dataclass
class MemoryStore:
    # TODO: Could switch to memoryview or redis on bigger environment
    job: Job
    nodes: Nodes
    weights: Weights
    costs: Costs


_store: MemoryStore | None = None


def set_store(store: MemoryStore) -> None:
    global _store  # noqa: PLW0603
    _store = store


def get_store() -> MemoryStore:
    if _store is None:
        raise ValueError("Set store before accessing it.")
    return _store


def del_store() -> None:
    global _store  # noqa: PLW0603
    del _store
    _store = None
