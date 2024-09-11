import dataclasses
import random

from falcon.core import PathStats


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
