import dataclasses
import random
from collections import defaultdict
from typing import Any

import pytest

from falcon.adapter import Job, PathStats
from falcon.core import PathService
from falcon.models import Falcon


def test_path_stats_order() -> None:
    stats = [
        PathStats(cost, total_weight, available_weight)
        for cost, total_weight, available_weight in [
            (0, 1, 1),
            (0, 1, 10),
            (0, 3, 1),
            (0, 3, 10),
            (1, 1, 1),
            (1, 1, 10),
            (1, 3, 1),
            (1, 3, 10),
        ]
    ]
    random.shuffle(stats)
    stats.sort()
    assert [dataclasses.astuple(stat) for stat in stats] == [
        (0, 1, 10),
        (0, 1, 1),
        (0, 3, 10),
        (0, 3, 1),
        (1, 1, 10),
        (1, 1, 1),
        (1, 3, 10),
        (1, 3, 1),
    ]


@pytest.mark.parametrize(
    ("overrides_job", "match"),
    [
        ({"departure": "foo"}, r"self.job.origin=.+ if not is the given graph."),
        ({"arrival": "bar"}, r"self.job.destination=.+ if not is the given graph."),
    ],
    ids=["origin", "destination"],
)
def test_validate_graph(overrides_job: dict[str, Any], match: str) -> None:
    job = Job.from_config(Falcon.model_validate({"departure": "a", "arrival": "b"} | overrides_job))
    service = PathService(job, {"a", "b"}, defaultdict(dict), defaultdict(set))
    with pytest.raises(ValueError, match=match):
        service.search_path()
