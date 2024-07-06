from PySide6.QtWidgets import QPushButton

from paragon.ui.controllers.dialogue_editor import DialogueEditor


class FE14SupportDialogueEditor(DialogueEditor):
    def __init__(
        self, data, service, sprite_animation_svc, game, support_service, info
    ):
        super().__init__(data, service, sprite_animation_svc, game)

        self.support_service = support_service
        self.info = info

        # Hide unused buttons.
        self.new_button.setVisible(False)
        self.delete_button.setVisible(False)
        self.rename_button.setVisible(False)

        # Insert "Add S support" button.
        self.add_s_support_button = QPushButton("Add S Support")
        self.generic_layout.insertWidget(1, self.add_s_support_button)

        self.add_s_support_button.clicked.connect(self._on_add_s_support)

    def set_archive(self, path, localized):
        super().set_archive(path, localized)
        self.add_s_support_button.setEnabled(self.keys_box.count() < 4)

    def _on_add_s_support(self):
        key = self.support_service.create_s_support(self.info)
        self.keys_box.addItem(key)
        self.keys_box.setCurrentIndex(self.keys_box.count() - 1)
        self.add_s_support_button.setEnabled(False)
