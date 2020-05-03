from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QWidget

from ui.property_form import PropertyForm
from ui.widgets.property_widget import PropertyWidget


class PointerPropertyEditor (QGroupBox, PropertyWidget):
    def __init__(self, target_property_name, template):
        QGroupBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)

        main_layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.make_unique_button = QPushButton("Make Unique")
        self.make_unique_button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                              QtWidgets.QSizePolicy.MinimumExpanding)
        self.clear_button = QPushButton("Clear")
        self.clear_button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                        QtWidgets.QSizePolicy.MinimumExpanding)
        self.toggle_button = QPushButton("Toggle Editor")
        self.toggle_button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                         QtWidgets.QSizePolicy.MinimumExpanding)
        button_layout.addWidget(self.make_unique_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.toggle_button)
        main_layout.addLayout(button_layout)

        self.property_form = PropertyForm(template)
        self.form_widget = QWidget()
        self.property_form.setContentsMargins(0, 0, 0, 0)
        self.form_widget.setLayout(self.property_form)
        main_layout.addWidget(self.form_widget)
        self.setLayout(main_layout)
        self.form_widget.setVisible(False)

        self.make_unique_button.clicked.connect(self._on_make_unique_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        self.toggle_button.clicked.connect(lambda: self.form_widget.setVisible(not self.form_widget.isVisible()))

    def _on_make_unique_clicked(self):
        if self.target:
            self.target[self.target_property_name].make_unique()
            self._on_target_changed()  # Pointer value changes here.

    def _on_clear_clicked(self):
        if self.target:
            self.target[self.target_property_name].clear_value()
            self._on_target_changed()  # Pointer value changes here.

    def _on_target_changed(self):
        if self.target:
            target_for_children = self._get_target_value()
            self.property_form.update_target(target_for_children)
            self.form_widget.setEnabled(target_for_children is not None)
        else:
            self.property_form.update_target(None)
