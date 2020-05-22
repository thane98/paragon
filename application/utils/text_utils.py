from PySide2.QtGui import QFont, QFontMetrics, QColor
from PySide2.QtWidgets import QGraphicsTextItem


def draw_message_text(item: QGraphicsTextItem, font: QFont, text: str, x: int, y: int, max_width: int):
    item.setDefaultTextColor(QColor.fromRgba(0xFF440400))
    item.setFont(font)
    item.setPos(x, y)

    # Calculate how many character to trim *without* making copies of the string.
    font_metrics = QFontMetrics(font)
    cur_width = font_metrics.width(text)
    cur_end = len(text) - 1
    while cur_width > max_width:
        cur_width -= font_metrics.charWidth(text, cur_end)
        cur_end -= 1
    item.setPlainText(text[:cur_end + 1])
