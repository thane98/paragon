from typing import Optional

from PySide2 import QtGui
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem

from module.properties.property_container import PropertyContainer
from services.service_locator import locator
from ui.misc.type1_draw_strategy import Type1DrawStrategy
from ui.widgets.conversation_bust import ConversationBust

_BG_WIDTH = 400
_BG_HEIGHT = 240
_DEFAULT_EMOTION = "通常"
# _FONT_NAME = "FOT-Chiaro Std B"
_FONT_NAME = "Merriweather Black"


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
        self._left_character_view = ConversationBust(left=True)
        self._right_character_view = ConversationBust()
        self.scene.addItem(self._left_character_view)
        self.scene.addItem(self._right_character_view)
        self._left_character_view.setPos(-30, 0.0)
        self._right_character_view.setPos(_BG_WIDTH - 256 + 30, 0.0)
        self._message_view: Optional[QGraphicsItem] = None
        self.talk_windows = locator.get_scoped("ConversationService").talk_windows()
        self.name_plate_font = QFont(_FONT_NAME)
        self.name_plate_font.setPixelSize(13)
        self.message_draw_strategy = Type1DrawStrategy(self)

    def enter_left(self, character: PropertyContainer, emotion=_DEFAULT_EMOTION):
        self._left_character_view.set_character(character)
        self._left_character_view.set_emotion(emotion)
        self._left_character_view.show_normal()

    def enter_right(self, character: PropertyContainer, emotion=_DEFAULT_EMOTION):
        self._right_character_view.set_character(character)
        self._right_character_view.set_emotion(emotion)
        self._right_character_view.show_normal()

    def clear_left(self):
        self._left_character_view.clear()

    def clear_right(self):
        self._right_character_view.clear()

    # TODO: Automatically use the character's name if no name is provided.
    # TODO: Support text boxes with no name plate.
    def message_left(self, text: str, name: str, window_type="standard", mode=0):
        self.clear_message()
        self._message_view = self.message_draw_strategy.draw_message(text, name, window_type, mode, left=True)

    def message_right(self, text: str, name: str, window_type="standard", mode=0):
        self.clear_message()
        self._message_view = self.message_draw_strategy.draw_message(text, name, window_type, mode, left=False)

    def clear(self):
        self.clear_left()
        self.clear_right()
        self.clear_message()

    def clear_message(self):
        if self._message_view:
            self.scene.removeItem(self._message_view)

    def fade_left(self):
        self._left_character_view.show_faded()

    def fade_right(self):
        self._right_character_view.show_faded()
