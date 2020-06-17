from PySide2.QtWidgets import QScrollArea, QWidget, QFormLayout, QLabel, QLineEdit

from model.fe14.chapter_data import CHAPTER_DIALOGUES


class FE14ChapterTextDataWidget(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chapter_data = None
        self.message_data_form = QFormLayout()
        self.message_data_editors = []
        self.message_data_scroll_content = QWidget()
        self.message_data_scroll_content.setLayout(self.message_data_form)
        self.setWidget(self.message_data_scroll_content)
        self.setWidgetResizable(True)
        for dialogue in CHAPTER_DIALOGUES:
            label = QLabel(dialogue.name)
            editor = QLineEdit()
            index = len(self.message_data_editors)
            editor.editingFinished.connect(lambda i=index, e=editor: self._on_dialogue_editor_text_changed(i, e.text()))
            self.message_data_editors.append(editor)
            self.message_data_form.addRow(label, editor)

    def update_chapter_data(self, chapter_data):
        self.chapter_data = chapter_data
        message_data = chapter_data.message_data if chapter_data else None
        if not message_data:
            for editor in self.message_data_editors:
                editor.setText("")
        else:
            for i in range(0, len(self.message_data_editors)):
                editor = self.message_data_editors[i]
                new_value = self.chapter_data.message_data[i]
                editor.setText(new_value)
        self.setEnabled(message_data is not None)

    def _on_dialogue_editor_text_changed(self, index: int, new_value: str):
        if self.chapter_data and self.chapter_data.message_data:
            self.chapter_data.message_data[index] = new_value
