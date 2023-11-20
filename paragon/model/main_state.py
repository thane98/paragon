import dataclasses

from PySide6.QtWidgets import QApplication

from paragon.ui.states.state_machine import StateMachine
from paragon.model.configuration import Configuration


@dataclasses.dataclass
class MainState:
    app: QApplication
    config: Configuration
    sm: StateMachine
