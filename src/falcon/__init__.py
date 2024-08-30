"""Millenium Falcon Challenge package.

Developer Technical Test @ Dataiku
"""

from __future__ import annotations

from pathlib import Path

__all__: list[str] = []

SOURCE_DIR = Path(__file__).parent.parent
PROJECT_DIR = SOURCE_DIR.parent
DB_DIR = PROJECT_DIR / "dbs"
DB_PLACEHOLDER = DB_DIR / "placeholder.db"
