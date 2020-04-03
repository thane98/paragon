import typing

from core.state_machine import Transition, State
from states.create_project_state import CreateProjectState
from states.loading_state import LoadingState


class CreateProjectToLoadingTransition(Transition):
    def apply(self, starting_state: State, ending_state: State):
        create_state = typing.cast(CreateProjectState, starting_state)
        loading_state = typing.cast(LoadingState, ending_state)
        loading_state.project = create_state.project
