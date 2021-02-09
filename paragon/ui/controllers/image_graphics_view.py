from PySide2.QtGui import (
    QClipboard,
    QMouseEvent,
    QCursor
)
from PySide2.QtCore import Qt

from PySide2.QtWidgets import (
    QGraphicsView,
    QAction,
    QMenu,
    QFileDialog
)

from PySide2.QtCore import (
    QRect,
    QPoint
)

class ImageGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self._setup_menu()

        # To be able to export images with a transparent background
        self.setStyleSheet("background-color: transparent")

    def _setup_menu(self):
        self._menu = QMenu()

        save_image_action = QAction("Save image", self)
        copy_image_action = QAction("Copy image", self)

        save_image_action.triggered.connect(self._save_image)
        copy_image_action.triggered.connect(self._copy_image)

        self._menu.addAction(save_image_action)
        self._menu.addAction(copy_image_action)


    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(e)
            e.accept()
        else:
            e.ignore()

    def _show_context_menu(self, e: QMouseEvent):
        self._menu.exec_(QCursor().pos())

    def _save_image(self):
        file_dialog = QFileDialog()

        filename, _ = file_dialog.getSaveFileName(
            self, 
            "Save Image", 
            None, 
            "PNG (*.png)"
        )

        if filename:
            self.grab(
                self._scene_rect()
            ).toImage().save(filename)

    def _copy_image(self):
        clipboard = QClipboard()

        clipboard.setImage(
            self.grab(
                self._scene_rect()
            ).toImage()
        )

    def _scene_rect(self) -> QRect:
        '''
        Returns QRect in the container
        '''
        x = self.mapFromScene(self.sceneRect().toRect()).boundingRect().x()
        y = self.mapFromScene(self.sceneRect().toRect()).boundingRect().y()
        return QRect(QPoint(x, y), self.sceneRect().size().toSize())
