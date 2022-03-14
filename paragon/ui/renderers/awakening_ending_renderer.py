from typing import Dict

from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QColor, QTextBlockFormat, QTextCursor, QTransform
from PySide2.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsItem

from paragon.core.services.endings import Endings
from paragon.model.ending import Ending


class AwakeningEndingRenderer:
    def __init__(self):
        self.block_format = QTextBlockFormat()
        self.block_format.setLineHeight(20, QTextBlockFormat.FixedHeight)

    def render(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service: Endings,
        ending: Ending,
        text_callback
    ):
        scene.addPixmap(textures["Main"])
        if ending.char2 is not None:
            scene.addPixmap(textures["Double"])

        font = service.font()
        ending_text = scene.addText(ending.value, font)
        ending_text.setTextInteractionFlags(QtGui.Qt.TextEditorInteraction)
        ending_text.setDefaultTextColor(QColor.fromRgba(0xFF440400))
        ending_text.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        ending_text.setPos(130, 98)
        ending_text.document().contentsChanged.connect(lambda: text_callback(ending_text.toPlainText()))

        cursor = ending_text.textCursor()
        cursor.clearSelection()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(self.block_format)

        portraits = service.get_portraits_for_ending(ending)
        if len(portraits) == 1:
            pixmap = portraits[0].crop(78, 10, 100, 204).to_qpixmap()
            item = scene.addPixmap(pixmap.transformed(QTransform().scale(-1, 1)))
            item.setPos(18, 18)
        elif len(portraits) == 2:
            crop_start_x = portraits[0].width // 2 - 50
            pixmap1 = portraits[0].crop(crop_start_x, 0, 100, 95).to_qpixmap().transformed(QTransform().scale(-1, 1))
            item = scene.addPixmap(pixmap1)
            item.setPos(10, 18)
            pixmap2 = portraits[1].crop(crop_start_x, 0, 100, 95).to_qpixmap().transformed(QTransform().scale(-1, 1))
            item = scene.addPixmap(pixmap2)
            item.setPos(10, 128)
