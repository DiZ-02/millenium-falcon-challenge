import sqlite3
from collections.abc import Generator
from logging import getLogger
from pathlib import Path

from falcon.models import Route

logger = getLogger(__name__)


class DbService:
    def __init__(self, routes_db: Path):
        self.connection = sqlite3.connect(routes_db)

    def get_nodes(self) -> set[str]:
        with self.connection as conn:
            # Note: UNION operator removes duplicates.
            cur = conn.execute("""
                select origin from routes
                UNION
                select destination from routes
                ORDER BY 1
            """)
            cur.row_factory = lambda cursor, row: row[0]
            nodes = set(cur.fetchall())
        logger.info(f"{len(nodes)} nodes fetched from database.")
        return nodes

    def get_edges(self) -> Generator[Route, None, None]:
        with self.connection as conn:
            cur = conn.execute("select origin, destination, travel_time from routes")
            fields = [column[0] for column in cur.description]
            cur.row_factory = lambda cursor, row: Route(**dict(zip(fields, row, strict=False)))
            yield from cur
