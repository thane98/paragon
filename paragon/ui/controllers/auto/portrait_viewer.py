from typing import Optional, List, Tuple

from PySide2.QtWidgets import QGraphicsScene
from paragon.model.auto_ui import PortraitViewerSpec

from paragon.model.auto_generator_state import AutoGeneratorState

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.core.textures.texture import Texture
from paragon.ui.views.ui_portrait_viewer import Ui_PortraitViewer


class PortraitViewer(AbstractAutoWidget, Ui_PortraitViewer):
    @staticmethod
    def new(ms, gs, retrieve_mode):
        dummy_state = AutoGeneratorState(
            main_state=ms,
            game_state=gs,
            generator=None,
            type_metadata={},
            field_metadata={},
            typename="",
        )
        spec = PortraitViewerSpec(
            type="portrait_viewer",
            retrieve_mode=retrieve_mode
        )
        return PortraitViewer(dummy_state, spec)

    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        Ui_PortraitViewer.__init__(self)
        self.service = self.gs.portraits
        self.rid = None
        self.retrieve_mode = spec.retrieve_mode
        self.portraits: Optional[List[Tuple[str, Texture]]] = None
        self.current_index = -1

        modes = self.service.modes()
        default_mode = self.service.default_mode()
        for mode in modes:
            self.mode_combo_box.addItem(mode)
        self.mode_combo_box.setCurrentIndex(modes.index(default_mode))

        if self.retrieve_mode == "face_data":
            self.mode_combo_box.setVisible(False)

        self.mode_combo_box.currentIndexChanged.connect(self._on_mode_changed)
        self.back_button.clicked.connect(self._on_back_button_pressed)
        self.forward_button.clicked.connect(self._on_forward_button_pressed)
        self._clear()

    def _on_mode_changed(self):
        self.current_index = 0
        self._update_portraits(self.mode_combo_box.currentText())

    def set_target(self, rid):
        self.rid = rid
        if not rid:
            self._clear()
        else:
            self.current_index = 0
            self._update_portraits(self.mode_combo_box.currentText())
        self.setEnabled(self.rid is not None)

    def _retrieve(self, mode: str):
        if not self.rid:
            return None
        if self.retrieve_mode == "character":
            return self.service.from_character(self.rid, mode)
        elif self.retrieve_mode == "class":
            return self.service.from_job(self.rid, mode)
        elif self.retrieve_mode == "face_data":
            return self.service.from_face_data(self.rid)
        else:
            return None

    def _update_portraits(self, mode: str):
        portraits = self._retrieve(mode)
        self.back_button.setEnabled(portraits is not None)
        self.forward_button.setEnabled(portraits is not None)
        if not portraits:
            self._clear_display()
            return
        self.portraits = list(portraits.items())
        self._set_portrait_from_current_index()

    def _set_portrait_from_current_index(self):
        if not self.portraits:
            return
        key, texture = self.portraits[self.current_index]
        self.portrait_name_label.setText(key)
        self.current_image_label.setText(
            "%d / %d" % (self.current_index + 1, len(self.portraits))
        )
        scene = QGraphicsScene()
        scene.addPixmap(texture.to_qpixmap())
        scene.setSceneRect(0.0, 0.0, 128.0, 128.0)
        self.display.setScene(scene)
        self.display.setSceneRect(0.0, 0.0, float(texture.width), float(texture.height))

    def _clear(self):
        self._clear_display()
        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)
        self.target = None
        self.portraits = None
        self.current_index = -1

    def _clear_display(self):
        self.display.setScene(None)
        self.portrait_name_label.setText("(None)")
        self.current_image_label.setText("0 / 0")

    def _on_back_button_pressed(self):
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.portraits) - 1
        self._set_portrait_from_current_index()

    def _on_forward_button_pressed(self):
        self.current_index += 1
        if self.current_index >= len(self.portraits):
            self.current_index = 0
        self._set_portrait_from_current_index()
