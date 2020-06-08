import logging
import os

from PySide2.QtWidgets import QWidget, QFileDialog

from services.abstract_editor_service import AbstractEditorService
from services.service_locator import locator
from ui.error_dialog import ErrorDialog
from ui.fe14_conversation_editor import FE14ConversationEditor


class GenericConversationService(AbstractEditorService):
    def __init__(self):
        self.error_dialog = ErrorDialog("Failed to open message archive.")
        self.editors = {}

    def get_editor(self) -> QWidget:
        file_name, ok = QFileDialog.getOpenFileName()
        if not ok:
            return None
        if file_name in self.editors:
            return self.editors[file_name]
        base_name = os.path.basename(file_name).replace(".bin.lz", "")
        try:
            open_files_service = locator.get_scoped("OpenFilesService")
            real_path = open_files_service.to_valid_path_in_filesystem(file_name)
            if not real_path:
                raise ValueError("Invalid path: " + file_name)
            message_archive = open_files_service.open_message_archive(real_path, localized=False)
            editor = FE14ConversationEditor(message_archive, title=base_name, owner=self)
            self.editors[real_path] = editor
            return editor
        except:
            logging.exception("Failed to open message archive.")
            return self.error_dialog

    def delete_conversation_editor(self, editor: FE14ConversationEditor):
        for key, value in self.editors.items():
            if value == editor:
                del self.editors[key]
                break

    def get_display_name(self) -> str:
        return "Generic Conversation"

    def save(self):
        pass
