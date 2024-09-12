from dataclasses import dataclass, replace
from functools import total_ordering
from logging import getLogger
from math import inf
from typing import Self

from falcon.adapter import Costs, Job, Nodes, Weights

logger = getLogger(__name__)


@total_ordering
@dataclass(order=False)
class PathStats:
    cost: float = inf
    total_weight: float = inf
    available_weight: float = 0

    def __lt__(self: Self, other: Self) -> bool:
        if self.cost != other.cost:
            return self.cost < other.cost
        if self.total_weight != other.total_weight:
            return self.total_weight < other.total_weight
        # /!\ Reverse order here: keep the record maximizing the available weight for next move
        return other.available_weight < self.available_weight


class PathService:
    def __init__(self, job: Job, nodes: Nodes, weights: Weights, costs: Costs):
        # TODO: use weakref logic to resolve weights and costs with less impact on memory.
        self.job, self.nodes, self.weights, self.costs = job, nodes, weights, costs

        # Represents the best result for the current search.
        self.least_expensive_travel = PathStats()
        # For each day, stores the destinations reachable and the associated stats.
        self.least_expensive_destinations: list[dict[str, PathStats]] = []

    def _validate_params(self) -> None:
        if self.job.origin not in self.nodes:
            raise ValueError(f"{self.job.origin=} if not is the given graph.")
        if self.job.destination not in self.nodes:
            raise ValueError(f"{self.job.destination=} if not is the given graph.")

    def get_cost_to_reach(self, destination: str, at: int) -> PathStats | None:
        best_stats = PathStats()
        for origin, weight in self.weights[destination].items():
            if at - weight >= 0 and origin in self.least_expensive_destinations[at - weight]:
                stats = self.least_expensive_destinations[at - weight][origin]
                if origin == destination:  # Waiting action
                    stats = replace(stats, available_weight=self.job.max_available_weight)
                if stats.available_weight >= weight:
                    new_stats = PathStats(
                        cost=stats.cost + int(at in self.costs.get(destination, {})),
                        total_weight=stats.total_weight + weight,
                        available_weight=stats.available_weight - weight,
                    )
                    best_stats = min(best_stats, new_stats)
        # Return only if reaching this destination with given weight is possible
        # Prune if leading to a worse solution
        return best_stats if best_stats.cost < inf and best_stats < self.least_expensive_travel else None

    def search_path(self) -> PathStats:
        """
        Search for a path with the following criteria:
        - minimizing total cost,
        - with a total weight under max_total_weight,
        - with max_available_weight depleting while moving - recovering totally if not.

        Return the number of bad events encountered.
        """

        self._validate_params()

        logger.info(f"Searching for path from {self.job.origin} to {self.job.destination}...")

        self.least_expensive_destinations.append(
            {
                self.job.origin: PathStats(
                    cost=int(0 in self.costs[self.job.origin]),
                    total_weight=0,
                    available_weight=self.job.max_available_weight,
                ),
            },
        )
        for day in range(1, self.job.max_total_weight + 1):
            destinations = {}
            for node in self.nodes:
                if cost := self.get_cost_to_reach(node, day):
                    destinations[node] = cost
            self.least_expensive_destinations.append(destinations)
            if self.job.destination in destinations:
                self.least_expensive_travel = min(self.least_expensive_travel, destinations[self.job.destination])
        logger.info(f"Safest solution found: {self.least_expensive_travel}")
        return self.least_expensive_travel
