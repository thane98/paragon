from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout
from paragon.ui.controllers.auto.icon_combo_box import IconComboBox

from paragon.model.auto_ui import IconComboBoxSpec

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class IconDisplay(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)

        self.rid = None
        self.field_id = field_id
        self.spec = spec

        combo_box_spec = IconComboBoxSpec(type="icon_combo_box", icons=spec.icons, base_index=spec.base_index)
        self.combo_box = IconComboBox(state, combo_box_spec, field_id)
        self.label = QLabel()
        self.label.setAlignment(QtGui.Qt.AlignCenter)
        self.label.setFixedSize(spec.display_dim, spec.display_dim)

        layout = QVBoxLayout()
        layout.setAlignment(QtGui.Qt.AlignHCenter)
        layout.addWidget(self.label)
        layout.addWidget(self.combo_box)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.combo_box.currentIndexChanged.connect(self._on_icon_changed)

    def set_target(self, rid):
        self.rid = rid
        self.combo_box.set_target(rid)

    def _on_icon_changed(self):
        icon = self.combo_box.currentData(QtCore.Qt.DecorationRole)
        if icon:
            icon = icon.scaled(
                self.spec.display_dim,
                self.spec.display_dim,
            )
        self.label.setPixmap(icon)
