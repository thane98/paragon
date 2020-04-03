import typing

from core.state_machine import Transition, State
from services.service_locator import locator
from services.settings_service import SettingsService
from states.loading_state import LoadingState


class FindProjectToLoadingTransition(Transition):
    def apply(self, _: State, ending_state: State):
        loading_state = typing.cast(LoadingState, ending_state)
        settings_service: SettingsService = locator.get_static("SettingsService")
        loading_state.project = settings_service.get_cached_project()
