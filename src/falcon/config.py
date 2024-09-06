import sqlite3
from logging import getLogger
from pathlib import Path

from pydantic import BaseModel

from falcon import DB_DIR, DB_PLACEHOLDER
from falcon.models import Communication, Falcon, Route
from falcon.path_service import get_service

logger = getLogger(__name__)


def search_file(filepath: Path, folders: list[Path]) -> Path:
    """Search for a file at a given Path, then in folder list in order."""
    if not filepath.exists():
        for folder in map(Path, folders):
            if not folder.is_dir():
                continue
            if folder.joinpath(filepath).exists():
                filepath = folder.joinpath(filepath)
                break

    if filepath.is_file():
        return filepath
    raise FileNotFoundError


def parse_file[M: BaseModel](  # type: ignore[valid-type]
    filepath: str | Path,
    model: type[M],  # type: ignore[name-defined]
    default: M | None = None,  # type: ignore[name-defined]
) -> M | None:  # type: ignore[name-defined]
    filepath, inst = Path(filepath), default
    try:
        with filepath.open() as file:
            inst = model.model_validate_json(file.read())
    except Exception as error:  # noqa: BLE001
        msg = f"Didn't manage to read given file: {filepath}."
        msg += f"\nUnexpected {error=}"
        if default is not None:
            msg += f"Using default value {default}."
        logger.warning(msg)
    return inst


def init_config(cfg_path: str | Path) -> Falcon:
    cfg_path = Path(cfg_path)
    cfg: Falcon = parse_file(cfg_path, Falcon, Falcon())  # type: ignore[assignment]

    try:
        cfg.routes_db = search_file(cfg.routes_db, [cfg_path.parent, DB_DIR])
    except FileNotFoundError:
        cfg.routes_db = DB_PLACEHOLDER
        logger.warning(
            f"DB file not found: {cfg.routes_db}.\nUsing empty database...",
        )
    logger.info(f"Configuration loaded:\n{cfg.model_dump()}")
    return cfg


def fetch_routes_from_db(routes_db: Path) -> list[Route]:
    # TODO: Extract this into a service
    logger.info(f"Fetching routes from database {routes_db}")
    with sqlite3.connect(routes_db) as db:
        return [Route.from_list(row) for row in db.cursor().execute("SELECT * FROM routes").fetchall()]


def init(cfg_path: str | Path, input_file: str | Path | None = None) -> Falcon:
    cfg_path = Path(cfg_path)
    config = init_config(cfg_path)
    routes = fetch_routes_from_db(config.routes_db)
    service = get_service()
    service.add_params(config)
    service.add_graph(routes)

    if input_file:
        try:
            input_file = Path(input_file)
            input_file = search_file(input_file, [cfg_path.parent, DB_DIR])
            if input_ := parse_file(input_file, Communication):
                service.add_constraints(input_)
        except FileNotFoundError:
            # TODO: Add placeholder for input file to demo the app?
            logger.warning(f"Input file not found: {input_file}.")

    return config
