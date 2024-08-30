from logging import getLogger

from falcon.models import Communication, Route

logger = getLogger(__name__)


class PathService:
    COMMON_WEIGHT = 1

    def __init__(self):
        self.graph = {}
        self.max_total_weight, self.weights = 0, {}

    def add_graph(self, routes: list[Route]) -> dict:
        self.graph.clear()
        for route in routes:
            self.graph.setdefault(route.origin, {})[route.destination] = route.travel_time
            self.graph.setdefault(route.destination, {})[route.origin] = route.travel_time
        logger.info(f"{len(routes)} edges added.")
        return self.graph

    def add_weights(self, communication: Communication) -> dict:
        self.max_total_weight = communication.countdown
        self.weights.clear()
        for hunter in communication.bounty_hunters:
            self.weights.setdefault(hunter.planet, {})[hunter.day] = self.COMMON_WEIGHT
        logger.info(f"{len(communication.bounty_hunters)} weights added.")
        return self.weights


def get_service() -> PathService:
    global service  # noqa: PLW0603
    if not service:
        service = PathService()
    return service


service: PathService | None = None
