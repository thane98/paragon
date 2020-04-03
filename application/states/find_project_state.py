import logging

from core.state_machine import State
from services.service_locator import locator


class FindProjectState(State):
    def __init__(self):
        super().__init__("FindProject")

    def act(self):
        logging.info("Entered FindProject state.")
        settings_service = locator.get_static("SettingsService")
        if settings_service.has_cached_project():
            locator.get_static("StateMachine").transition("Loading")
        else:
            locator.get_static("StateMachine").transition("CreateProject")
