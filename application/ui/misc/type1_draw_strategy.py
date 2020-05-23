from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QColor, QTextBlockFormat, QTextCursor
from PySide2.QtWidgets import QGraphicsItemGroup, QGraphicsScene, QGraphicsTextItem

from utils import text_utils

_BG_WIDTH = 400
_BG_HEIGHT = 240
_TALK_WINDOW_MODE_0_X = 8
_TALK_WINDOW_Y = 184
_NAME_PLATE_LEFT_X = 6
_NAME_PLATE_RIGHT_X = 282
_NAME_PLATE_Y = 168


class Type1DrawStrategy:
    def __init__(self, view):
        self.view = view
        self.scene: QGraphicsScene = view.scene

    def draw_message(self, text: str, name: str, window_type="standard", mode=0, left=True) -> QGraphicsItemGroup:
        # Create the message box
        talk_window: QPixmap = self.view.talk_windows[window_type][mode]
        message_box = self.scene.addPixmap(talk_window)
        talk_window_x = _TALK_WINDOW_MODE_0_X if not mode else -3
        talk_window_y = _TALK_WINDOW_Y if not mode else _TALK_WINDOW_Y - 5
        message_box.setPos(talk_window_x, talk_window_y)

        # Create the name plate
        name_plate_texture: QPixmap = self.view.talk_windows["name_plate"]["plate"]
        name_plate = self.scene.addPixmap(name_plate_texture)
        name_plate_x = _NAME_PLATE_LEFT_X if left else _NAME_PLATE_RIGHT_X
        name_plate.setPos(name_plate_x, _NAME_PLATE_Y)

        # Create the name plate text
        name_plate_text = QGraphicsTextItem()
        name_plate_text.setPlainText(name)
        name_plate_text.setDefaultTextColor(QColor.fromRgba(0xFFFFFFB3))
        name_plate_text.setFont(self.view.name_plate_font)
        name_plate_text.setTextWidth(name_plate_texture.width())
        name_plate_text.setPos(name_plate_x, _NAME_PLATE_Y)

        # Center the name plate text
        block_format = QTextBlockFormat()
        block_format.setAlignment(QtGui.Qt.AlignCenter)
        cursor = name_plate_text.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_format)
        cursor.clearSelection()
        name_plate_text.setTextCursor(cursor)
        self.scene.addItem(name_plate_text)

        # Create the message box text. Draw two lines if required.
        # Truncate lines with width > 312
        split_text = text.split(r"\n")
        message_box_text = QGraphicsTextItem()
        message_box_text_2 = QGraphicsTextItem()
        if split_text and split_text[0]:
            text_utils.draw_message_text(
                message_box_text,
                self.view.name_plate_font,
                split_text[0],
                _TALK_WINDOW_MODE_0_X + 20,
                _TALK_WINDOW_Y + 5,
                312
            )
        if len(split_text) > 1 and split_text[1]:
            text_utils.draw_message_text(
                message_box_text_2,
                self.view.name_plate_font,
                split_text[1],
                _TALK_WINDOW_MODE_0_X + 20,
                _TALK_WINDOW_Y + 21,
                312
            )

        group = self.scene.createItemGroup([
            message_box,
            message_box_text,
            message_box_text_2,
            name_plate,
            name_plate_text
        ])
        group.setZValue(2.0)
        return group
