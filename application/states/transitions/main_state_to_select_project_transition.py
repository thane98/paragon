import typing

from core.state_machine import Transition, State
from services.service_locator import locator
from states.main_state import MainState


class MainStateToSelectProjectTransition(Transition):
    def apply(self, start_state: State, _: State):
        start_state = typing.cast(MainState, start_state)
        locator.clear_scoped_services()
        start_state.window = None
