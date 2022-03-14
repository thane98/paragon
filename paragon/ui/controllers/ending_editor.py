from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel
from PySide2.QtWidgets import QCompleter

from paragon.core.services.endings import Endings
from paragon.model.game import Game
from paragon.ui.controllers.simple_new_ending_dialog import SimpleNewEndingDialog
from paragon.ui.models import Models
from paragon.ui.renderers.awakening_ending_renderer import AwakeningEndingRenderer
from paragon.ui.views.ui_ending_editor import Ui_EndingEditor


class EndingEditor(Ui_EndingEditor):
    def __init__(self, gd, models: Models, service: Endings, game: Game):
        super().__init__()

        # TODO: Undo/redo

        rid, field_id = gd.table("characters")
        self.characters_model = models.get(rid, field_id)
        self.gd = gd
        self.service = service
        self.assets = self.service.assets()
        self.new_ending_dialog = None

        if game == Game.FE13:
            self.renderer = AwakeningEndingRenderer()
        else:
            raise NotImplementedError

        self.model = service.model()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.search_completer = QCompleter()
        self.search_completer.setModel(self.proxy_model)
        self.search_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.search_completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.search_completer.setCompletionRole(QtCore.Qt.DisplayRole)
        self.search_completer.setFilterMode(QtCore.Qt.MatchContains)
        self.keys_box.setCompleter(self.search_completer)
        self.keys_box.setModel(self.proxy_model)

        self.keys_box.currentIndexChanged.connect(self._on_selection_changed)
        self.new_button.clicked.connect(self._on_new)
        self.delete_button.clicked.connect(self._on_delete)

        self._on_selection_changed()

    def _on_new(self):
        self.new_ending_dialog = SimpleNewEndingDialog(
            self.gd,
            self.service,
            self.characters_model,
            self.model,
            self._on_ending_created,
        )
        self.new_ending_dialog.show()

    def _on_selection_changed(self):
        self._render_scene()
        ending = self.keys_box.currentData(QtCore.Qt.UserRole)
        if not ending:
            return
        if ending.is_single():
            self.ending_info_widget.setText(f"Single Ending - {ending.char1_name}")
        else:
            self.ending_info_widget.setText(
                f"Paired Ending - {ending.char1_name} / {ending.char2_name}"
            )

    def _on_text_changed(self, text):
        ending = self.keys_box.currentData(QtCore.Qt.UserRole)
        if not ending:
            return
        ending.value = text
        self.service.update_ending(ending.key, text)

    def _on_ending_created(self, index):
        self.keys_box.setCurrentIndex(index)
        self._on_selection_changed()

    def _on_delete(self):
        if self.keys_box.currentData(QtCore.Qt.UserRole):
            self.model.removeRow(self.keys_box.currentIndex())

    def _render_scene(self):
        self.scene.clear()
        ending = self.keys_box.currentData(QtCore.Qt.UserRole)
        if not ending:
            return
        self.renderer.render(
            self.scene, self.assets, self.service, ending, self._on_text_changed
        )
