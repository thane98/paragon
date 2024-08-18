from PySide6.QtWidgets import QComboBox

from paragon.model.configuration import Configuration
from paragon.model.fe10_state import FE10State
from paragon.model.fe9_state import FE9State
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class GcnJobIconComboBox(AbstractAutoWidget, QComboBox):
    def __init__(self, state):
        AbstractAutoWidget.__init__(self, state)
        QComboBox.__init__(self)
        if model := self.gs.icons.model("item"):
            self.setModel(model)
        self.setStyleSheet("combobox-popup: 0;")
        self.rid = None

        config: Configuration = state.main_state.config
        game_state = state.game_state
        if isinstance(game_state, FE9State):
            self.icon_mapping = config.fe9_job_icons
        elif isinstance(game_state, FE10State):
            self.icon_mapping = config.fe10_job_icons
        else:
            raise NotImplementedError

        self.currentIndexChanged.connect(self._on_edit)

    def set_target(self, rid):
        if not self.model():
            return

        self.rid = rid
        if rid:
            job_key = self.data.key(self.rid)
            index = self.icon_mapping.get(job_key)
            if index is not None:
                self.setCurrentIndex(index)
            else:
                self.setCurrentIndex(-1)
        else:
            self.setCurrentIndex(-1)
        self.setEnabled(self.rid is not None)

    def _on_edit(self):
        if self.rid and self.model():
            job_key = self.data.key(self.rid)
            if job_key and self.currentIndex() != -1:
                self.icon_mapping[job_key] = self.currentIndex()
