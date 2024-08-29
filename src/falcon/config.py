from logging import getLogger
from pathlib import Path

from falcon import DB_DIR
from falcon.models import Falcon, search_file

logger = getLogger(__name__)


def init_config(cfg_path: str | Path) -> Falcon:
    cfg_path = Path(cfg_path)
    try:
        with cfg_path.open() as cfg_file:
            cfg = Falcon.model_validate_json(cfg_file.read())
    except Exception as error:
        cfg = Falcon()
        logger.warning(
            f"Didn't manage to read given file: {cfg_path}.\nUnexpected {error=}\nLoading empty config...",
        )

    cfg.routes_db = search_file(cfg.routes_db, [cfg_path.parent, DB_DIR])
    logger.info(f"Configuration loaded: {cfg.dict()}")
    return cfg
