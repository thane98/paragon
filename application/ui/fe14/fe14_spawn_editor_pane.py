from typing import Optional

from PySide2.QtWidgets import QScrollArea, QWidget

from model.fe14.dispo import get_spawn_template
from module.properties.property_container import PropertyContainer
from ui.property_form import PropertyForm


class FE14SpawnEditorPane(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contents = QWidget()
        self.form = PropertyForm(get_spawn_template())
        self.contents.setLayout(self.form)
        self.setWidgetResizable(True)
        self.setWidget(self.contents)

    def update_target(self, new_target: Optional[PropertyContainer]):
        self.form.update_target(new_target)

    def update_coordinate_of_target(self, coordinate_key: str, updated_spawn):
        self.form.editors[coordinate_key].update_target(updated_spawn)
