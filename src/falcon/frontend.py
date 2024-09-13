import json
from collections import defaultdict
from enum import StrEnum
from logging import getLogger

import pydantic
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from nicegui import app, events, ui
from nicegui.events import ClickEventArguments

from falcon.adapter import Job
from falcon.core import PathService
from falcon.models import Communication
from falcon.store import get_store

logger = getLogger(__name__)


class FilePickerStatus(StrEnum):
    info = "Upload the intercepted communication."
    positive = "Communication uploaded with success."
    warning = "The communication is not correct. Please review the uploaded file."
    negative = "Error during upload. Please try again."


class FilePicker:
    def __init__(self):
        self.status = None
        self.upload_element = (
            ui.upload(
                # TODO: use run_io_bound to keep GUI responsive
                on_upload=self.upload_handler,
                max_files=1,
                multiple=False,
            )
            .props("accept=.json")
            .classes("w-full h-full col-span-2 lg:col-span-1")
            .on("removed", lambda e: self.reset())
            .on("failed", lambda e: self.set_status(FilePickerStatus.negative))
        )
        with ui.column().classes("size-full col-span-2 lg:col-span-1"):
            self.label_element = ui.label()
            self.file_preview = ui.code(language="json").classes("w-full col-span-2 lg:col-span-1")
        self.set_status(FilePickerStatus.info)

    def set_status(self, status: FilePickerStatus) -> None:
        self.status = status
        self.label_element.classes(replace=f"text-{status.name}")
        self.label_element.set_text(status.value)
        self.file_preview.set_visibility(status in (FilePickerStatus.warning, FilePickerStatus.positive))

    def reset(self) -> None:
        self.set_status(FilePickerStatus.info)
        self.upload_element.reset()
        self.file_preview.set_content("")

    def upload_handler(self, event: events.UploadEventArguments) -> None:
        text = event.content.read().decode("utf-8", errors="replace")
        try:
            communication = Communication.model_validate_json(text)
            formatted = json.dumps(communication.model_dump(), indent=4)
            self.file_preview.set_content(formatted)
            self.set_status(FilePickerStatus.positive)

            store = get_store()
            user_job = store.job.copy()
            app.storage.user["costs"] = jsonable_encoder(user_job.add_constraints(communication))
            app.storage.user["job"] = jsonable_encoder(user_job.model_dump())
        except (json.decoder.JSONDecodeError, pydantic.ValidationError):
            logger.warning("Didn't manage to parse given file")
            self.file_preview.set_content(text)
            self.set_status(FilePickerStatus.warning)


def header() -> None:
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


def init(fastapi_app: FastAPI) -> None:
    @ui.page("/")
    def show() -> None:
        header()

        with ui.grid(columns=2).classes("w-full grid-flow-row"):
            file_picker = FilePicker()

            with ui.row().classes("w-full col-span-2 lg:col-span-2 place-content-evenly"):

                def start_on_click(_: ClickEventArguments) -> None:
                    start_button.set_visibility(False)
                    result_element.set_visibility(True)
                    store = get_store()
                    job = Job.model_validate(app.storage.user["job"])
                    costs = defaultdict(set, app.storage.user["costs"])
                    service = PathService(job, store.nodes, store.weights, costs)
                    # TODO: Use run_cpu_bound for asynchronous processing
                    job.result = service.search_path()
                    result_label.set_text(f"{job.get_odds().odds:.1%}")
                    app.storage.user["job"] = jsonable_encoder(job.model_dump())

                start_button = ui.button("Start").props('size="xl" padding="xl" glossy')
                start_button.bind_enabled_from(
                    file_picker,
                    "status",
                    backward=lambda status: status == FilePickerStatus.positive,
                ).on_click(start_on_click)

                def reset_on_click(_: ClickEventArguments) -> None:
                    file_picker.reset()
                    # TODO: bind visibility on PathService.is_running without calling get_service for performance
                    result_element.set_visibility(False)
                    start_button.set_visibility(True)

                with ui.column().classes("items-center") as result_element:
                    ui.label("Your chance to reach destination safely is:")
                    result_label = ui.label("--.-%").props('size="xl"')
                    ui.button("Reset").on_click(reset_on_click)
                    result_element.set_visibility(False)

    ui.run_with(
        fastapi_app,
        mount_path="/gui",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
        storage_secret="pick your private secret here",  # noqa: S106
        # NOTE setting a secret is optional but allows for persistent storage per user
    )


# TODO: Add unit tests for frontend
