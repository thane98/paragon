from paragon.ui.controllers.main_window import MainWindow
from paragon.ui.states.state import State


class UIMainState(State):
    def __init__(self):
        super().__init__()
        self.window = None

    def run(self, **kwargs):
        ms = kwargs["main_state"]
        gs = kwargs["game_state"]

        self.window = MainWindow(ms, gs)
        self.window.show()

    def on_exit(self):
        self.window = None

    def get_name(self) -> str:
        return "UIMain"
