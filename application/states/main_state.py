import logging

from core.state_machine import State
from ui.main_window import MainWindow


class MainState(State):
    def __init__(self):
        super().__init__("Main")
        self.window = None

    def act(self):
        logging.info("Entered Main state.")
        self.window = MainWindow()
        self.window.show()
