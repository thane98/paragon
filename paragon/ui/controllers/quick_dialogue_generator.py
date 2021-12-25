from PySide2.QtGui import QClipboard

from paragon.core.dialogue import convert
from paragon.core.services.utils import is_avatar_pid
from paragon.ui import utils
from paragon.ui.views.ui_quick_dialogue_generator import Ui_QuickDialogueGenerator


class QuickDialogueGenerator(Ui_QuickDialogueGenerator):
    def __init__(self, gs):
        super().__init__()

        self.gd = gs.data
        self.service = gs.dialogue

        table_rid, table_field_id = self.gd.table("characters")
        models = gs.models
        characters_model = models.get(table_rid, table_field_id)
        self.character1_box.setModel(characters_model)
        self.character2_box.setModel(characters_model)
        self.character1_box.setCurrentIndex(-1)
        self.character2_box.setCurrentIndex(-1)

        self._update_buttons()

        self.character1_box.currentIndexChanged.connect(self._update_buttons)
        self.character2_box.currentIndexChanged.connect(self._update_buttons)
        self.dialogue_editor.textChanged.connect(self._update_buttons)
        self.convert_button.clicked.connect(self._convert)
        self.copy_button.clicked.connect(self._on_copy)

    def _on_copy(self):
        clipboard = QClipboard()
        clipboard.setText(self.result_display.toPlainText())

    def _update_buttons(self):
        self.convert_button.setEnabled(self._inputs_are_valid())

    def _inputs_are_valid(self):
        return bool(
            self.character1_box.currentData()
            and self.character2_box.currentData()
            and self.dialogue_editor.toPlainText()
        )

    def _convert(self):
        character1 = self.character1_box.currentData()
        character2 = self.character2_box.currentData()
        text = self.dialogue_editor.toPlainText()
        try:
            text = convert.quick_to_pretty(
                text,
                self._get_character_quick_script_name(character1),
                3,
                self._get_character_quick_script_name(character2),
                7,
            )
            self.result_display.setPlainText(text)
        except:
            utils.error(self)

    def _get_character_quick_script_name(self, rid):
        pid = self.gd.key(rid)
        if is_avatar_pid(pid):
            return "Corrin"
        else:
            return self.gd.display(rid)
