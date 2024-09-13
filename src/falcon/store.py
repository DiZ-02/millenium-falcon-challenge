from collections import defaultdict
from dataclasses import dataclass, field

from falcon.adapter import Costs, Job, Nodes, Weights


@dataclass
class MemoryStore:
    # TODO: Could switch to memoryview or redis on bigger environment
    job: Job
    nodes: Nodes
    weights: Weights
    costs: Costs = field(default_factory=lambda: defaultdict(set))


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


# def get_store() -> Generator[MemoryStore]:
#     global _store
#     job, nodes, weights, costs = init(
#         os.environ.get("MILLENIUM_FALCON_CHALLENGE__JSON_CFG_PATH", "placeholder"),
#     )
#     _store = MemoryStore(job, nodes, weights, costs)
#     yield _store
#     del _store
