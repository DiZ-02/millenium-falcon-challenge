import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse

from falcon import frontend
from falcon.config import init
from falcon.core import PathService
from falcon.models import Communication, SafePath
from falcon.store import MemoryStore, del_store, get_store, set_store

# Use level passed to uvicorn command as base level...
logging.basicConfig(level=getLogger("uvicorn").level)
# ...but keep uvicorn above debug because too verbose
getLogger("uvicorn").setLevel(max(logging.INFO, getLogger("uvicorn").level))
logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    job, nodes, weights, costs = init(
        os.environ.get("MILLENIUM_FALCON_CHALLENGE__JSON_CFG_PATH", "placeholder"),
    )
    set_store(MemoryStore(job, nodes, weights, costs))
    yield
    del_store()


app = FastAPI(lifespan=lifespan)
frontend.init(app)


HOME_RESPONSE_FMT = """<!doctype html>
<html lang="en">
  <div>Click <a href="{0}/docs">here</a> for API docs.</div>
  <div>Click <a href="{0}/gui">here</a> for user interface.</div>
</html>"""


@app.get("/", status_code=200)
def read_root(request: Request) -> HTMLResponse:
    domain = str(request.base_url).rstrip("/")
    return HTMLResponse(HOME_RESPONSE_FMT.format(domain))


@app.post("/communication", status_code=201)
def upload_communication(communication: Communication) -> Communication:
    store = get_store()
    store.costs = store.job.add_constraints(communication)
    return communication


# TODO: split /job/start and /job/status with BackgroundTask
@app.post("/compute_odds", status_code=200)
async def compute_odds() -> SafePath:
    store = get_store()
    service = PathService(store.job, store.nodes, store.weights, store.costs)
    store.job.result = service.search_path()
    return store.job.get_odds()
