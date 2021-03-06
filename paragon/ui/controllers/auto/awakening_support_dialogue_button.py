from PySide2.QtWidgets import QPushButton, QMessageBox

from paragon.model.game import Game
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.dialogue_editor import DialogueEditor

_PLACEHOLDER_MESSAGE = (
    "$t1$Wmアンナ|3$w0|$Wsアンナ|$E通常,|This message was generated\\nby Paragon.$k"
)


class AwakeningSupportDialogueButton(AbstractAutoWidget, QPushButton):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QPushButton.__init__(self, "Edit Dialogue")
        self.field_id = spec.field_id
        self.rid = None
        self.dialogue_editor = None
        self.current_dialog_pair = None

        self.clicked.connect(self._on_click)

    def set_target(self, rid):
        self.rid = rid
        self.setEnabled(self.rid is not None)

    def _on_click(self):
        pid = self.data.key(self.rid)
        other_rid = self.data.rid(self.rid, self.field_id)
        other_pid = self.data.key(other_rid) if other_rid else None
        if not pid or not other_pid or len(pid) < 5 or len(other_pid) < 5:
            dialog = QMessageBox()
            dialog.setText(
                "Please enter a valid PID for the character and the support to edit dialogue."
            )
            dialog.exec_()
            return
        else:
            part_1 = pid[4:]
            part_2 = other_pid[4:]
            if self._is_current_editor(part_1, part_2):
                self.dialogue_editor.show()
            else:
                path = self._get_archive(part_1, part_2)
                self.dialogue_editor = DialogueEditor(
                    self.data, self.gs.dialogue, self.gs.sprite_animation, Game.FE13
                )
                self.dialogue_editor.set_archive(path, True)
                self.dialogue_editor.show()
            self.current_dialog_pair = (part_1, part_2)

    def _get_archive(self, part_1, part_2) -> str:
        v1 = f"m/{part_1}_{part_2}.bin.lz"
        v2 = f"m/{part_2}_{part_1}.bin.lz"
        v3 = f"m/{part_1}_{part_2}_親子.bin.lz"
        v4 = f"m/{part_2}_{part_1}_親子.bin.lz"
        for path in [v1, v2, v3, v4]:
            try:
                self.data.open_text_data(path, True)
                return path
            except:
                pass  # That didn't work... try a different path.
        self.data.new_text_data(v1, True)
        c_key = f"MID_支援_{part_1}_{part_2}_Ｃ"
        b_key = f"MID_支援_{part_1}_{part_2}_Ｂ"
        a_key = f"MID_支援_{part_1}_{part_2}_Ａ"
        s_key = f"MID_支援_{part_1}_{part_2}_Ｓ"
        self.data.set_message(v1, True, c_key, _PLACEHOLDER_MESSAGE)
        self.data.set_message(v1, True, b_key, _PLACEHOLDER_MESSAGE)
        self.data.set_message(v1, True, a_key, _PLACEHOLDER_MESSAGE)
        self.data.set_message(v1, True, s_key, _PLACEHOLDER_MESSAGE)
        return v1

    def _is_current_editor(self, part_1, part_2):
        return (part_1, part_2) == self.current_dialog_pair or (
            part_2,
            part_1,
        ) == self.current_dialog_pair
