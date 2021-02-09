from PySide2.QtGui import QClipboard, QMouseEvent, QCursor
from PySide2.QtCore import Qt

from PySide2.QtWidgets import QGraphicsView, QAction, QMenu, QFileDialog


class ImageGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self._setup_menu()

    def _setup_menu(self):
        self._menu = QMenu()

        save_image_action = QAction("Save image", self)
        copy_image_action = QAction("Copy image", self)

        save_image_action.triggered.connect(self._save_image)
        copy_image_action.triggered.connect(self._copy_image)

        self._menu.addAction(save_image_action)
        self._menu.addAction(copy_image_action)

    def scrollContentsBy(self, dx: int, dy: int) -> None:
        pass  # disable scrolling

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(e)
            e.accept()
        else:
            e.ignore()

    def _show_context_menu(self, _):
        self._menu.exec_(QCursor().pos())

    def _save_image(self):
        file_dialog = QFileDialog()

        filename, _ = file_dialog.getSaveFileName(
            self, "Save Image", None, "PNG (*.png)"
        )

        if filename:
            self.grab(self.sceneRect().toRect()).toImage().save(filename)

    def _copy_image(self):
        clipboard = QClipboard()
        clipboard.setImage(self.grab(self.sceneRect().toRect()).toImage())
