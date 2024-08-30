#!/usr/bin/env python3
import logging
import os
from logging import getLogger

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse

from falcon import frontend
from falcon.config import init
from falcon.models import Communication
from falcon.path_service import get_service

logging.basicConfig(level=getLogger("uvicorn").level)
logger = getLogger(__name__)

app, service = FastAPI(), get_service()
config = init(os.environ.get("JSON_CFG_PATH", "placeholder"))
frontend.init(app)


@app.get("/", status_code=200)
def read_root(request: Request):
    domain = request.base_url
    return HTMLResponse(
        f"""<html>
        Go to <a>{domain}/docs</a> for API docs.
        Go to <a>{domain}/gui</a> for user interface.
        </html>""",
    )


@app.post("/communication", status_code=201)
def upload_communication(communication: Communication):
    service.add_weights(communication)
    return communication


if __name__ == "__main__":
    print("Please use `pdm run [dev|prod]` to run the API.")
