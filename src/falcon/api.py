#!/usr/bin/env python3
import logging
import os
from logging import getLogger

from fastapi import FastAPI

from falcon import frontend
from falcon.config import init_config
from falcon.path_service import PathService

logging.basicConfig(level=getLogger("uvicorn").level)
logger = getLogger(__name__)

app = FastAPI()
config = init_config(os.environ.get("JSON_CFG_PATH", "placeholder"))
service = PathService(config.routes_db)
frontend.init(app)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    print("Please use `pdm run [dev|prod]` to run the project.")
