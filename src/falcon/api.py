import logging
import os
from logging import getLogger

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse

from falcon import frontend
from falcon.config import init
from falcon.models import Communication, SafePath
from falcon.path_service import get_service

logging.basicConfig(level=getLogger("uvicorn").level)
logger = getLogger(__name__)

app = FastAPI()
config = init(os.environ.get("JSON_CFG_PATH", "placeholder"))
frontend.init(app)


HOME_RESPONSE_FMT = """<html>
Go to <a>{0}/docs</a> for API docs.
Go to <a>{0}/gui</a> for user interface.
</html>"""


@app.get("/", status_code=200)
def read_root(request: Request) -> HTMLResponse:
    domain = str(request.base_url).rstrip("/")
    return HTMLResponse(HOME_RESPONSE_FMT.format(domain))


@app.post("/communication", status_code=201)
def upload_communication(communication: Communication) -> Communication:
    get_service().add_constraints(communication)
    return communication


# TODO: split /job/start and /job/status with BackgroundTask
@app.post("/compute_odds", status_code=200)
async def compute_odds() -> SafePath:
    return get_service().search_path()
