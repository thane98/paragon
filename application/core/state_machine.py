from abc import ABC, abstractmethod
from typing import Optional, Dict


class NameInUseException(Exception):
    pass


class State(ABC):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def get_name(self):
        return self.name

    @abstractmethod
    def act(self):
        pass


class Transition(ABC):
    def __init__(self, starting_state_name: str, ending_state_name: str):
        self.starting_state_name = starting_state_name
        self.ending_state_name = ending_state_name

    def get_starting_state(self) -> str:
        return self.starting_state_name

    def get_ending_state(self) -> str:
        return self.ending_state_name

    def get_name(self) -> str:
        return "(%s, %s)" % (self.starting_state_name, self.ending_state_name)

    @abstractmethod
    def apply(self, starting_state: State, ending_state: State):
        pass


class StateMachine:
    def __init__(self):
        self.states: Dict[str, State] = {}
        self.transitions: Dict[str, Transition] = {}
        self.current_state: Optional[State] = None

    def add_state(self, state: State):
        if state.get_name() in self.states:
            raise NameInUseException
        self.states[state.get_name()] = state

    def add_transition(self, transition: Transition):
        if transition.get_name() in self.transitions:
            raise NameInUseException
        self.transitions[transition.get_name()] = transition

    def get_current_state(self) -> Optional[State]:
        return self.current_state

    def transition(self, new_state_name: str):
        if new_state_name not in self.states:
            raise KeyError
        else:
            target_state = self.states[new_state_name]
        if self.current_state:
            target_transition_name = "(%s, %s)" % (self.current_state.get_name(), target_state.get_name())
            if target_transition_name in self.transitions:
                target_transition = self.transitions[target_transition_name]
                target_transition.apply(self.current_state, target_state)
        self.current_state = target_state
        self.current_state.act()
