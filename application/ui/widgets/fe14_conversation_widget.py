from typing import Optional, List

from PySide2 import QtGui
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem

from services.service_locator import locator
from ui.misc.type1_draw_strategy import Type1DrawStrategy
from ui.widgets.conversation_bust import ConversationBust

_BG_WIDTH = 400
_BG_HEIGHT = 240
_DEFAULT_EMOTION = "通常"
_FONT_NAME = "FOT-Chiaro Std B"


class FE14ConversationWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0.0, 0.0, _BG_WIDTH, _BG_HEIGHT)
        self.setFixedSize(400, 240)
        self.setHorizontalScrollBarPolicy(QtGui.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtGui.Qt.ScrollBarAlwaysOff)

        self.background = self.scene.addPixmap(locator.get_scoped("ConversationService").background())
        self._busts = self._create_busts()
        self._message_view: Optional[QGraphicsItem] = None

        self.talk_windows = locator.get_scoped("ConversationService").talk_windows()
        self.name_plate_font = QFont(_FONT_NAME)
        self.name_plate_font.setPixelSize(15)
        self.message_draw_strategy = Type1DrawStrategy(self)

    def _create_busts(self) -> List[ConversationBust]:
        position_0_bust = ConversationBust(left=True)
        position_3_bust = ConversationBust(left=True)
        position_6_bust = ConversationBust()
        position_7_bust = ConversationBust()
        self.scene.addItem(position_0_bust)
        self.scene.addItem(position_3_bust)
        self.scene.addItem(position_6_bust)
        self.scene.addItem(position_7_bust)
        position_0_bust.setPos(-30, 0.0)
        position_3_bust.setPos(-30, 0.0)
        position_6_bust.setPos(_BG_WIDTH - 256 + 30, 0.0)
        position_7_bust.setPos(_BG_WIDTH - 256 + 30, 0.0)
        return [position_0_bust, None, None, position_3_bust, None, None, position_6_bust, position_7_bust]

    @staticmethod
    def is_position_valid(position: int, mode: int):
        if mode == 1:
            return position == 3 or position == 7
        else:
            return position == 0 or position == 6

    def set_portraits(self, fid: str, position: int):
        if not self._busts[position]:
            raise ValueError
        self._busts[position].set_portraits(fid)

    def set_emotions(self, emotions: List[str], position: int):
        if not self._busts[position]:
            raise ValueError
        if not emotions:
            emotions = [_DEFAULT_EMOTION]
        self._busts[position].set_emotions(emotions)
        self._busts[position].show_normal()

    def clear_at(self, position: int):
        if not self._busts[position]:
            raise ValueError
        self._busts[position].clear()

    def message(self, text: str, name: str, speaker_position: int, window_type="standard", mode=0):
        self.clear_message()
        left = speaker_position == 3
        self._message_view = self.message_draw_strategy.draw_message(
            text,
            name,
            window_type,
            mode,
            left
        )
        for i, bust in enumerate(self._busts):
            if i == speaker_position:
                bust.show_normal()
            elif bust:
                bust.show_faded()

    def clear_message(self):
        if self._message_view:
            self.scene.removeItem(self._message_view)

    def clear(self):
        self.clear_message()
        for bust in self._busts:
            if bust:
                bust.clear()
