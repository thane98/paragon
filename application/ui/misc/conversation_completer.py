from PySide2.QtWidgets import QCompleter, QToolTip
from PySide2 import QtCore

class ParagonConversationCompleter(QCompleter):            
    def __init__(self, parent=None):
        super(ParagonConversationCompleter, self).__init__(parent)

        self.highlighted.connect(self._tool_tip)

    def set_command_hints(self, hints):
        self._command_hints = dict()
        self._command_hints = hints


    @QtCore.Slot(str)
    def _tool_tip(self, command):
        popup = self.popup()
        point = QtCore.QPoint(popup.pos().x() + popup.width(), popup.pos().y() - 16)
        for item in self._command_hints:
            if item['Command'] == command:
                QToolTip.showText(point, item['Hint'])
                break
            else:
                QToolTip.hideText()
