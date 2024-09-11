"""Millenium Falcon Challenge package.

Developer Technical Test @ Dataiku
"""

from __future__ import annotations

from pathlib import Path

SOURCE_DIR = Path(__file__).parent
PROJECT_DIR = SOURCE_DIR.parent.parent
DB_DIR = PROJECT_DIR / "dbs"
DB_PLACEHOLDER = DB_DIR / "placeholder.db"
