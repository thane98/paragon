from PySide6 import QtGui
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsScene
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.scene_graphics_view import ImageGraphicsView


class MiniPortraitBox(AbstractAutoWidget, ImageGraphicsView):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        ImageGraphicsView.__init__(self)

        self.spec = spec
        self.service = self.gs.portraits
        self.rid = None

        if self.spec.box_height:
            self.setFixedHeight(self.spec.box_height)
        else:
            self.setFixedHeight(self.spec.box_dim)
        self.setFixedWidth(self.spec.box_dim)

    def _retrieve(self, rid):
        if not rid:
            return None
        elif self.spec.retrieve_mode == "character":
            return self.service.from_character(rid, self.spec.mode)
        elif self.spec.retrieve_mode == "class":
            return self.service.from_job(rid, self.spec.mode)
        elif (
            self.spec.retrieve_mode == "reference"
            and self.spec.reference_type == "character"
        ):
            rid = self.data.rid(rid, self.spec.reference_field)
            return self.service.from_character(rid, self.spec.mode) if rid else None
        elif (
            self.spec.retrieve_mode == "reference"
            and self.spec.reference_type == "class"
        ):
            rid = self.data.rid(rid, self.spec.reference_field)
            return self.service.from_job(rid, self.spec.mode) if rid else None
        else:
            raise NotImplementedError

    def set_target(self, rid):
        portraits = self._retrieve(rid)
        if not portraits:
            self.setScene(QGraphicsScene())
        else:
            texture = portraits[next(iter(portraits))]
            self.set_to_pixmap(texture.to_qpixmap())

    def set_to_pixmap(self, pixmap: QPixmap):
        if self.spec.mode == "HR":
            pixmap = pixmap.scaled(
                self.spec.image_dim,
                (
                    self.spec.image_height
                    if self.spec.image_height
                    else self.spec.image_dim
                ),
                mode=QtGui.Qt.SmoothTransformation,
            )
        self.setEnabled(True)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        scene.setSceneRect(
            self.spec.x_transform,
            self.spec.y_transform,
            self.spec.image_dim,
            self.spec.image_height if self.spec.image_height else self.spec.image_dim,
        )
        self.setScene(scene)
