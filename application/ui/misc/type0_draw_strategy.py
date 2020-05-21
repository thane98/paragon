from PySide2.QtWidgets import QGraphicsItemGroup


class Type0DrawStrategy:
    def __init__(self, view):
        self.view = view
        self.scene = view.scene

    def draw_message(self, text: str, window_type="standard", left=True) -> QGraphicsItemGroup:
        pass
