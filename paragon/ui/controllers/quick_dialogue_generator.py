from paragon.core.dialogue import convert
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

        self._update_buttons()

        self.character1_box.currentIndexChanged.connect(self._update_buttons)
        self.character2_box.currentIndexChanged.connect(self._update_buttons)
        self.dialogue_editor.textChanged.connect(self._update_buttons)
        self.convert_button.clicked.connect(self._convert)

    def _update_buttons(self):
        self.convert_button.setEnabled(self._inputs_are_valid())

    def _inputs_are_valid(self):
        return bool(self.character1_box.currentData()
                    and self.character2_box.currentData()
                    and self.dialogue_editor.toPlainText())

    def _convert(self):
        character1 = self.character1_box.currentData()
        character2 = self.character2_box.currentData()
        text = self.dialogue_editor.toPlainText()
        try:
            text = convert.quick_to_pretty(text, self.gd.display(character1), 3, self.gd.display(character2), 7)
            self.result_display.setPlainText(text)
        except:
            utils.error(self)
