from paragon.ui.views.ui_fe10_main_widget import Ui_FE10MainWidget


class FE10MainWidget(Ui_FE10MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window

    def on_close(self):
        pass
