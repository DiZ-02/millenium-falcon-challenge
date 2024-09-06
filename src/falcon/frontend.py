import json
from logging import getLogger

import pydantic
from fastapi import FastAPI
from nicegui import app, events, ui
from nicegui.elements.mixins.content_element import ContentElement
from nicegui.events import ClickEventArguments

from falcon.models import Communication
from falcon.path_service import get_service

logger = getLogger(__name__)


def json_file_handler(event: events.UploadEventArguments, element: ContentElement) -> None:
    text = event.content.read().decode("utf-8", errors="replace")
    try:
        communication = Communication.model_validate_json(text)
        formatted = json.dumps(communication.model_dump(), indent=4)
        element.set_content(formatted)
        get_service().add_constraints(communication)
    except (json.decoder.JSONDecodeError, pydantic.ValidationError):
        logger.warning("Didn't manage to parse given file")
        element.set_content(text)
    element.set_visibility(True)


def init(fastapi_app: FastAPI) -> None:
    @ui.page("/")
    def show() -> None:
        with ui.header().classes("items-center justify-between"):
            ui.label("Millenium Falcon Challenge")

            # NOTE dark mode will be persistent for each user across tabs and server restarts
            def toggle_page_mode(e: ClickEventArguments) -> None:  # noqa: ARG001
                app.storage.user["dark_mode"] = not app.storage.user["dark_mode"]

            dark_mode = ui.dark_mode()
            dark_mode.bind_value(app.storage.user, "dark_mode")
            ui.button(on_click=toggle_page_mode).props("round unelevated").bind_icon_from(
                dark_mode,
                "value",
                lambda value: "dark_mode" if value else "light_mode",
            )

        with ui.row().classes("w-full flex flex-nowrap"):
            ui.upload(
                on_upload=lambda event: json_file_handler(event, upload_content),
                max_files=1,
            ).props("accept=.json").classes("w-1/3 flex-initial")
            upload_content = ui.code(language="json").classes("w-2/3 flex-initial")
            upload_content.set_visibility(False)

    ui.run_with(
        fastapi_app,
        mount_path="/gui",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
        storage_secret="pick your private secret here",  # noqa: S106 # NOTE setting a secret is optional but allows for persistent storage per user
    )
