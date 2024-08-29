import sqlite3
from pathlib import Path

from falcon.models import Route


class PathService:
    def __init__(self, routes_db: Path):
        with sqlite3.connect(routes_db) as db:
            self.routes = [Route.from_list(row) for row in db.cursor().execute("SELECT * FROM routes").fetchall()]
