from collections import defaultdict
from dataclasses import dataclass
from functools import total_ordering
from logging import getLogger
from math import inf
from pathlib import Path as FilePath
from typing import ClassVar, Self

from pydantic import BaseModel

from falcon.db import DbService
from falcon.models import Communication, Falcon, SafePath

logger = getLogger(__name__)

Nodes = set[str]
Weights = defaultdict[str, dict[str, int]]
Costs = defaultdict[str, set[int]]


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


class Job(BaseModel):
    # Fixed parameters for path finding service
    WAITING_ACTION_WEIGHT: ClassVar[int] = 1
    FAIL_CHANCE: ClassVar[float] = 0.1  # Taken from documentation
    SUCCESS_CHANCE: ClassVar[float] = 1 - FAIL_CHANCE

    # Performance upper bounds
    MAX_AUTONOMY: ClassVar[int] = 4096
    MAX_NB_NODES: ClassVar[int] = 2048

    max_available_weight: int
    max_total_weight: int = 0

    origin: str
    destination: str

    routes_db: FilePath
    result: PathStats | None = None

    # TODO: Add ID and status for API and GUI

    @classmethod
    def from_config(cls, config: Falcon) -> Self:
        """
        Add parameters from configuration file.

        autonomy: Maximum weight available to travel on one edge.
        departure: origin of the path.
        arrival: destination of the path.
        routes_db: Path to the DB file.
        """
        if config.autonomy >= cls.MAX_AUTONOMY:
            raise ValueError(f"{config.autonomy=} must be less then {cls.MAX_AUTONOMY}.")

        logger.info(f"Parameters loaded: {config}")

        return cls(
            origin=config.departure,
            destination=config.arrival,
            max_available_weight=config.autonomy,
            routes_db=config.routes_db,
        )

    def generate_graph(self) -> tuple[Nodes, Weights]:
        db_service = DbService(self.routes_db)

        nodes = db_service.get_nodes()

        number_of_nodes = len(nodes)
        if number_of_nodes >= self.MAX_NB_NODES:
            raise ValueError(f"{number_of_nodes=} must be less than {self.MAX_NB_NODES}.")

        number_of_edges = 0
        edges: Weights = defaultdict(dict)

        # Add an edge from a node to itself to handle waiting action
        for node in nodes:
            edges[node][node] = self.WAITING_ACTION_WEIGHT

        # Add edges from a node to another node
        for route in db_service.get_edges():
            number_of_edges += 1
            # TODO: filter out edges with travel time > autonomy?
            edges[route.origin][route.destination] = route.travel_time
            edges[route.destination][route.origin] = route.travel_time

        logger.info(f"Fetched {number_of_nodes} nodes and {number_of_edges} edges from db.")
        return nodes, edges

    def add_constraints(self, communication: Communication) -> Costs:
        self.max_total_weight = communication.countdown

        costs = defaultdict(set)
        for hunter in communication.bounty_hunters:
            costs[hunter.planet].add(hunter.day)
        logger.info(f"{len(communication.bounty_hunters)} weights added.")
        return costs

    def get_odds(self) -> SafePath:
        """return the odds of success for a given path cost - aka. the number of wrong events.

        Success probability for a whole path is the product of the success probabilities for each edge:
        - 1 for a clear edge
        - 1-FAIL_CHANCE for an edge with a wrong event as wrong events share the same probability.
        Thus, the global probability of success for a given path is determined by the number of wrong events occured.
        """
        if self.result is None:
            raise ValueError("Result is null, please run path search.")
        return SafePath(odds=self.SUCCESS_CHANCE**self.result.cost)
