from PySide6.QtWidgets import QWidget, QVBoxLayout
from paragon.ui.auto_widget_generator import AutoWidgetGenerator


class FE9MapEditorSidePanel(QWidget):
    def __init__(self, ms, gs):
        super().__init__()

        gen = AutoWidgetGenerator(ms, gs)
        self.spawn_ui = gen.generate_for_type("Spawn")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spawn_ui)
        self.setLayout(layout)

    def toggle_mode(self):
        self.spawn_ui.setVisible(False)

    def clear_forms(self):
        self.set_spawn_target(None)

    def set_spawn_target(self, spawn):
        self.spawn_ui.set_target(spawn)

    def get_spawn_widgets(self):
        return self.spawn_ui.gen_widgets
