import typing

from core.state_machine import Transition, State
from services.service_locator import locator
from states.loading_state import LoadingState
from states.main_state import MainState


class ReloadProjectTransition(Transition):
    def apply(self, start_state: State, ending_state: State):
        start_state = typing.cast(MainState, start_state)
        loading_state = typing.cast(LoadingState, ending_state)
        start_state.window = None
        driver = locator.get_scoped("Driver")
        loading_state.project = driver.get_project()
