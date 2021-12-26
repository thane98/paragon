from paragon.ui import utils
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.misc.fe15_event_script_syntax_highlighter import (
    FE15EventScriptHighlighter,
)
from paragon.ui.views.ui_fe15_event_script_editor import Ui_FE15EventScriptEditor


class FE15EventScriptEditor(AbstractAutoWidget, Ui_FE15EventScriptEditor):
    def __init__(self, state):
        AbstractAutoWidget.__init__(self, state)
        Ui_FE15EventScriptEditor.__init__(self)

        self.highlighter = FE15EventScriptHighlighter(self.editor.document())

        self.service = self.gs.events

        self.rid = None

        self.editor.editing_finished.connect(self._on_editing_finished)
        self.editor.cursorPositionChanged.connect(self._on_cursor_position_changed)

    def set_target(self, rid):
        self.rid = rid
        if not rid:
            self.clear()
        else:
            self._update_editor_for_new_rid()

    def clear(self):
        self.editor.clear()
        self.editor.setEnabled(False)

    def _update_editor_for_new_rid(self):
        try:
            self.editor.setPlainText(
                self.gs.events.convert_to_paragon_event_script(self.rid)
            )
            self.editor.setEnabled(True)
        except:
            utils.error(self)

    def _on_editing_finished(self):
        if not self.rid:
            return
        try:
            self.service.convert_to_game_events(self.editor.toPlainText(), self.rid)
            self.status_bar.showMessage("Successfully compiled events!", 5000)
        except:
            utils.error(self)

    def _on_cursor_position_changed(self):
        block = self.editor.textCursor().blockNumber() + 1
        pos = self.editor.textCursor().positionInBlock() + 1
        self.cursor_position_label.setText(f"{block} : {pos}")
