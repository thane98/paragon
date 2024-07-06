from PySide6 import QtGui
from PySide6.QtWidgets import QTableWidgetItem

from paragon.ui.views.ui_dialogue_emotions_dialog import Ui_DialogueEmotionsDialog


class DialogueEmotionsDialog(Ui_DialogueEmotionsDialog):
    def __init__(self, service):
        super().__init__()

        self.service = service
        self._refresh()

    def _refresh(self):
        emotion_translations = sorted(
            self.service.emotion_translations().items(), key=lambda k: k[0].lower()
        )
        self.table.clear()
        self.table.setColumnCount(2)
        self.table.setRowCount(len(emotion_translations))
        self.table.setHorizontalHeaderLabels(["Name in Paragon", "Name in Game"])
        self.table.verticalHeader().hide()
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 200)
        for i in range(0, len(emotion_translations)):
            name_in_paragon, name_in_game = emotion_translations[i]
            paragon_item = QTableWidgetItem(name_in_paragon)
            paragon_item.setFlags(paragon_item.flags() & ~QtGui.Qt.ItemIsEditable)
            game_item = QTableWidgetItem(name_in_game)
            game_item.setFlags(game_item.flags() & ~QtGui.Qt.ItemIsEditable)
            self.table.setItem(i, 0, paragon_item)
            self.table.setItem(i, 1, game_item)
