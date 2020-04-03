import logging

from core.state_machine import State
from services.service_locator import locator
from services.settings_service import SettingsService


class InitState(State):
    def __init__(self):
        super().__init__("Init")

    def act(self):
        logging.info("Entered Init state.")
        locator.register_static("SettingsService", SettingsService())
        locator.get_static("StateMachine").transition("FindProject")
