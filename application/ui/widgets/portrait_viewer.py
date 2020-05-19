from typing import Optional, List, Tuple

from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGraphicsScene

from model.texture import Texture
from module.properties.property_container import PropertyContainer
from services.service_locator import locator
from ui.views.ui_portrait_viewer import Ui_PortraitViewer


class PortraitViewer(Ui_PortraitViewer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._target: Optional[PropertyContainer] = None
        self._portraits: Optional[List[Tuple[str, Texture]]] = None
        self._current_index = -1

        self.show_st_button.clicked.connect(self._on_show_st_pressed)
        self.show_bu_button.clicked.connect(self._on_show_bu_pressed)
        self.back_button.clicked.connect(self._on_back_button_pressed)
        self.forward_button.clicked.connect(self._on_forward_button_pressed)

        self._clear()

    def update_target(self, target: PropertyContainer):
        if not target:
            self._clear()
        else:
            self.setEnabled(True)
            self._target = target
            self._current_index = 0
            self._update_portraits("st")

    def _update_portraits(self, mode: str):
        if not self._target:
            return
        portrait_service = locator.get_scoped("PortraitService")
        self._portraits = portrait_service.get_sorted_portraits_for_character(self._target, mode)
        if not self._portraits:
            self._clear()
            return
        self._set_portrait_from_current_index()

    def _set_portrait_from_current_index(self):
        portrait_name, texture = self._portraits[self._current_index]
        self.portrait_name_label.setText(portrait_name)
        self.current_image_label.setText("%d / %d" % (self._current_index + 1, len(self._portraits)))

        scene = QGraphicsScene()
        scene.addPixmap(QPixmap.fromImage(texture.image()))
        scene.setSceneRect(0.0, 0.0, 128.0, 128.0)
        self.display.setScene(scene)
        self.display.setSceneRect(0.0, 0.0, float(texture.width()), float(texture.height()))

    def _clear(self):
        self.setEnabled(False)
        self.display.setScene(None)
        self.portrait_name_label.setText("(None)")
        self.current_image_label.setText("0 / 0")
        self._target = None
        self._portraits = None
        self._current_index = -1

    def _on_show_st_pressed(self):
        self._update_portraits("st")

    def _on_show_bu_pressed(self):
        self._update_portraits("bu")

    def _on_back_button_pressed(self):
        self._current_index -= 1
        if self._current_index < 0:
            self._current_index = len(self._portraits) - 1
        self._set_portrait_from_current_index()

    def _on_forward_button_pressed(self):
        self._current_index += 1
        if self._current_index >= len(self._portraits):
            self._current_index = 0
        self._set_portrait_from_current_index()
