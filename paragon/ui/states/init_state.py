import logging

from PySide2.QtGui import QPalette, QColor, Qt, QFontDatabase

from paragon.ui.states.state import State


class InitState(State):
    def run(self, **kwargs):
        ms = kwargs["main_state"]
        self.set_theme(ms.app, ms.config.theme)
        ms.sm.transition("FindProject", main_state=ms)

        QFontDatabase.addApplicationFont("resources/misc/FOT-ChiaroStd-B.otf")

    def set_theme(self, app, theme):
        try:
            if theme == "Fusion Dark":
                app.setStyle("Fusion")
                app.setPalette(self.gen_dark_palette())
            elif theme:
                app.setStyle(theme)
        except:
            logging.exception(f"Failed to set app theme to {theme}.")

    @staticmethod
    def gen_dark_palette() -> QPalette:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
        palette.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
        palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.darkGray)
        palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
        palette.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))
        return palette

    def get_name(self) -> str:
        return "Init"
