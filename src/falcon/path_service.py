from dataclasses import dataclass, replace
from functools import total_ordering
from logging import getLogger
from math import inf
from typing import Self

from falcon.models import Communication, Falcon, Route, SafePath

logger = getLogger(__name__)


@total_ordering
@dataclass(order=False)
class PathStats:
    cost: float = inf
    available_weight: float = 0
    total_weight: float = inf

    def __lt__(self: Self, other: Self) -> bool:
        if self.cost != other.cost:
            return self.cost < other.cost
        if self.total_weight != other.total_weight:
            return self.total_weight < other.total_weight
        # /!\ Reverse order here: keep the record maximizing the available weight for next move
        return other.available_weight < self.available_weight


class PathService:
    COMMON_WEIGHT = 1
    FAIL_CHANCE = 0.1  # Taken from documentation
    SUCCESS_CHANCE = 1 - FAIL_CHANCE

    MAX_AUTONOMY = 4096
    MAX_NB_NODES = 2048

    def __init__(self):
        self.is_running = False
        self.max_total_weight, self.max_available_weight = 0, 0
        self.origin, self.destination = None, None
        self.nodes, self.graph, self.costs = set(), {}, {}

    # Adapters
    # TODO: extract adapter into its own Job class
    def add_params(self, config: Falcon) -> None:
        """
        Add parameters for path search.

        max_available_weight: Maximum weight available to travel on one edge.
        origin: Departure of the path.
        destination: Arrival of the path.
        """
        if config.autonomy >= self.MAX_AUTONOMY:
            raise ValueError(f"{config.autonomy=} must be less then {self.MAX_AUTONOMY}.")

        self.max_available_weight = config.autonomy
        self.origin = config.departure
        self.destination = config.arrival
        logger.info(f"Parameters loaded: {self.origin=}, {self.destination=}, {self.max_available_weight=}")

    def add_graph(self, routes: list[Route]) -> dict:
        self.nodes.clear()
        self.graph.clear()

        # Add edges from a node to another node
        for route in routes:
            self.nodes |= {route.origin, route.destination}
            # TODO: filter out edges with travel time > autonomy?
            self.graph.setdefault(route.origin, {})[route.destination] = route.travel_time
            self.graph.setdefault(route.destination, {})[route.origin] = route.travel_time

        number_of_nodes = len(self.nodes)
        if number_of_nodes >= self.MAX_NB_NODES:
            raise ValueError(f"{number_of_nodes=} must be less than {self.MAX_NB_NODES}.")

        # Add an edge from a node to itself to handle waiting action
        for node in self.nodes:
            self.graph.setdefault(node, {})[node] = 1

        logger.info(f"{len(routes)} edges and {len(self.nodes)} nodes / self edges added.")
        return self.graph

    def add_constraints(self, communication: Communication) -> dict:
        self.max_total_weight = communication.countdown
        self.costs.clear()
        for hunter in communication.bounty_hunters:
            self.costs.setdefault(hunter.planet, {})[hunter.day] = self.COMMON_WEIGHT
        logger.info(f"{len(communication.bounty_hunters)} weights added.")
        return self.costs

    def get_probability(self, wrong_events: float) -> SafePath:
        """Returns the probability of success for a given number of wrong events.

        Success probability for a whole path is the product of the success probabilities for each edge:
        - 1 for a clear edge
        - 1-FAIL_CHANCE for an edge with a wrong event as wrong events share the same probability.
        Thus, the global probability of success for a given path is determined by the number of occurring events.
        """
        return SafePath(odds=self.SUCCESS_CHANCE**wrong_events)

    # Core logic

    def _validate_graph(self) -> None:
        if not self.graph:
            raise ValueError("A graph is required to search for a path.")
        if self.origin not in self.graph:
            raise ValueError(f"{self.origin=} if not is the given graph.")
        if self.destination not in self.graph:
            raise ValueError(f"{self.destination=} if not is the given graph.")

    def search_path(self) -> SafePath:
        """
        Search for a path with the following criteria:
        - minimizing total cost,
        - with a total weight under max_total_weight,
        - with max_available_weight depleting while moving - recovering totally if not.

        Return the number of bad events encountered.
        """

        # TODO: Wrap this function into a class, extract subfunctions, move nonlocal variables to instance level
        def get_cost_to_reach(destination: str, at: int) -> PathStats | None:
            best_stats = PathStats()
            for origin, weight in self.graph.get(destination, {}).items():
                if at - weight >= 0 and origin in least_expensive_destinations[at - weight]:
                    stats = least_expensive_destinations[at - weight][origin]
                    if origin == destination:  # Waiting action
                        stats = replace(stats, available_weight=self.max_available_weight)
                    if stats.available_weight >= weight:
                        new_stats = PathStats(
                            cost=stats.cost + int(at in self.costs.get(destination, {})),
                            available_weight=stats.available_weight - weight,
                            total_weight=stats.total_weight + weight,
                        )
                        best_stats = min(best_stats, new_stats)
            # Return only if reaching this destination with given weight is possible
            # Prune if leading to a worse solution
            return best_stats if best_stats.cost < inf and best_stats < least_expensive_travel else None

        self.is_running = True
        self._validate_graph()
        least_expensive_travel = PathStats()
        # For each day, it stores the destinations reachable on this day and the associated stats.
        least_expensive_destinations: list[dict[str, PathStats]] = [
            {
                self.origin: PathStats(
                    cost=int(0 in self.costs.get(self.origin, {})),
                    available_weight=self.max_available_weight,
                    total_weight=0,
                ),
            },
        ]
        for day in range(1, self.max_total_weight + 1):
            destinations = {}
            for node in self.nodes:
                if cost := get_cost_to_reach(node, day):
                    destinations[node] = cost
            least_expensive_destinations.append(destinations)
            if self.destination in destinations:
                least_expensive_travel = min(least_expensive_travel, destinations[self.destination])
        self.is_running = False
        return self.get_probability(least_expensive_travel.cost)


def get_service() -> PathService:
    global service  # noqa: PLW0603
    if not service:
        service = PathService()
    return service


service: PathService | None = None
