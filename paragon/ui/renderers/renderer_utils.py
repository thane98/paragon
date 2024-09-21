from PySide6.QtGui import QFontMetrics


def trim_to_width(text, font, width):
    font_metrics = QFontMetrics(font)
    cur_width = font_metrics.horizontalAdvance(text, len(text))
    cur_end = len(text) - 1
    while cur_width > width:
        cur_width -= font_metrics.horizontalAdvance(text, cur_end)
        cur_end -= 1
    return text[: cur_end + 1]
