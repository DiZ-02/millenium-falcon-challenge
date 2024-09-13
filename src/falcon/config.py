from collections import defaultdict
from collections.abc import Sequence
from logging import getLogger
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from falcon import DB_DIR, DB_PLACEHOLDER, PROJECT_DIR
from falcon.adapter import Costs, Job, Nodes, Weights
from falcon.models import Communication, Falcon

logger = getLogger(__name__)


def search_file(filepath: Path, folders: Sequence[Path] = ()) -> Path:
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


M = TypeVar("M", bound=BaseModel)


def parse_file(filepath: Path, model: type[M]) -> M | None:
    inst = None
    try:
        with filepath.open() as file:
            inst = model.model_validate_json(file.read(), context={"extra": "forbid"})
    except (FileNotFoundError, ValidationError) as error:
        logger.warning(f"Didn't manage to read given file: {filepath}.\nUnexpected error: {error}")
    return inst


def init_config(cfg_path: str | Path) -> Falcon:
    cfg_path = Path(cfg_path)
    try:
        cfg_path = search_file(cfg_path, [PROJECT_DIR])
        cfg: Falcon = parse_file(cfg_path, Falcon)  # type: ignore[assignment]
    except FileNotFoundError:
        logger.warning(
            f"Config file not found: {cfg_path}.\nUsing default config...",
        )
        cfg = Falcon()

    try:
        cfg.routes_db = search_file(cfg.routes_db, [cfg_path.parent, DB_DIR])
    except FileNotFoundError:
        cfg.routes_db = DB_PLACEHOLDER
        logger.warning(
            f"DB file not found: {cfg.routes_db}.\nUsing empty database...",
        )
    logger.info(f"Configuration loaded:\n{cfg.model_dump()}")
    return cfg


def init(cfg_path: str | Path, input_file: str | Path | None = None) -> tuple[Job, Nodes, Weights, Costs]:
    cfg_path = Path(cfg_path)
    config = init_config(cfg_path)

    job = Job.from_config(config)
    nodes, edges = job.generate_graph()
    costs: Costs = defaultdict(set)

    if input_file:
        try:
            input_file = Path(input_file)
            input_file = search_file(input_file, [cfg_path.parent, DB_DIR])
            if input_ := parse_file(input_file, Communication):
                costs = job.add_constraints(input_)
        except FileNotFoundError:
            # TODO: Add placeholder for input file to demo the app?
            logger.warning(f"Input file not found: {input_file}.")

    return job, nodes, edges, costs
