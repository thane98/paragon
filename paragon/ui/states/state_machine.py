import logging
from typing import Dict, Optional
from paragon.ui.states.state import State


class StateMachine:
    def __init__(self):
        self._states: Dict[str, State] = {}
        self._current_state: Optional[State] = None

    def clear(self):
        self._states.clear()
        self._current_state = None

    def add_state(self, state: State):
        self._states[state.get_name()] = state

    def transition(self, new_state: str, **kwargs):
        logging.debug(f"Entering state {new_state}.")
        try:
            old_state = self._current_state
            self._current_state = self._states[new_state]
            if old_state:
                old_state.on_exit()
            self._current_state.run(**kwargs)
        except:
            logging.exception(f"Failed during transition to state {new_state}.")
            raise
