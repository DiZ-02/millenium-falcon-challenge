from collections import defaultdict
from logging import getLogger
from typing import TYPE_CHECKING

from falcon.db import DbService
from falcon.models import Communication, Falcon, SafePath

if TYPE_CHECKING:
    from falcon.core import PathStats

logger = getLogger(__name__)

Nodes = set[str]
Weights = dict[str, dict[str, int]]
Costs = dict[str, set[int]]


class Job:
    # Fixed parameters for path finding service
    WAITING_ACTION_WEIGHT = 1
    FAIL_CHANCE = 0.1  # Taken from documentation
    SUCCESS_CHANCE = 1 - FAIL_CHANCE

    # Performance upper bounds
    MAX_AUTONOMY = 4096
    MAX_NB_NODES = 2048

    def __init__(self, config: Falcon) -> None:
        """
        Add parameters from configuration file.

        max_available_weight: Maximum weight available to travel on one edge.
        origin: Departure of the path.
        destination: Arrival of the path.
        """
        # TODO: Add ID and status for API and GUI
        self.max_total_weight = 0
        self.result: PathStats | None = None

        if config.autonomy >= self.MAX_AUTONOMY:
            raise ValueError(f"{config.autonomy=} must be less then {self.MAX_AUTONOMY}.")

        self.max_available_weight = config.autonomy
        self.origin, self.destination = config.departure, config.arrival
        logger.info(f"Parameters loaded: {self.origin=}, {self.destination=}, {self.max_available_weight=}")

        self.routes_db = config.routes_db

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

        logger.info(f"Fetched {number_of_nodes} nodes and {number_of_edges} from db.")
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
