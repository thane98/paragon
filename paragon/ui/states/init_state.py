import logging
import os

from PySide6.QtGui import QPalette, QColor, Qt, QFontDatabase, QIcon, QFont
from PySide6.QtWidgets import QMessageBox

from paragon.ui.states.state import State


class InitState(State):
    def run(self, **kwargs):
        ms = kwargs["main_state"]
        logging.getLogger().setLevel(ms.config.log_level)

        self.sanity_check_cwd()

        self.set_theme(ms.app, ms.config.theme)
        self.set_font(ms.app, ms.config.font)
        QFontDatabase.addApplicationFont("resources/misc/FOT-ChiaroStd-B.otf")

        ms.sm.transition("FindProject", main_state=ms)

    def set_font(self, app, font_str):
        if not font_str:
            return
        font = QFont()
        font.fromString(font_str)
        app.setFont(font)

    def set_theme(self, app, theme):
        try:
            if theme == "Fusion Dark":
                app.setStyle("Fusion")
                app.setPalette(self.gen_dark_palette())
            elif theme and theme != "Native":
                app.setStyle(theme)
        except:
            logging.exception(f"Failed to set app theme to {theme}.")

    @staticmethod
    def sanity_check_cwd():
        if not os.path.exists("Data") or not os.path.isdir("Data"):
            message_box = QMessageBox()
            message_box.setText(
                "Cannot find Paragon data files. This probably means that your working directory is incorrect."
            )
            message_box.setWindowTitle("Cannot find data files.")
            message_box.setWindowIcon(QIcon("paragon.ico"))
            message_box.setIcon(QMessageBox.Warning)
            message_box.exec_()

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
