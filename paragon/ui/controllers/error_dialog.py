from paragon.ui.views.ui_error_dialog import Ui_ErrorDialog


class ErrorDialog(Ui_ErrorDialog):
    def __init__(self, traceback):
        super().__init__()
        self.text.setText(traceback)
        self.buttons.accepted.connect(self.accept)
