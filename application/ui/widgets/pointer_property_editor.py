from PySide2.QtWidgets import QFormLayout, QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from ui.widgets.property_widget import PropertyWidget


class PointerPropertyEditor (QGroupBox, PropertyWidget):
    def __init__(self, target_property_name, template):
        QGroupBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)

        main_layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.make_unique_button = QPushButton("Make Unique")
        self.toggle_button = QPushButton("Toggle Editor")
        button_layout.addWidget(self.make_unique_button)
        button_layout.addWidget(self.toggle_button)
        main_layout.addLayout(button_layout)

        form_layout = QFormLayout()
        self.form_widget = QWidget()
        self.editors = []
        for (key, value) in template.items():
            label = QLabel(key)
            editor = value.create_editor()
            self.editors.append(editor)
            form_layout.addRow(label, editor)
        form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_widget.setLayout(form_layout)
        main_layout.addWidget(self.form_widget)
        self.setLayout(main_layout)

        self.make_unique_button.clicked.connect(self._on_make_unique_clicked)
        self.toggle_button.clicked.connect(lambda: self.form_widget.setVisible(not self.form_widget.isVisible()))

    def _on_make_unique_clicked(self):
        if self.target:
            self.target[self.target_property_name].make_unique(self.target)
            self._on_target_changed()  # Pointer value changes here.

    def _on_target_changed(self):
        if self.target:
            target_for_children = self.target[self.target_property_name].value
            for editor in self.editors:
                editor.update_target(target_for_children)
        else:
            for editor in self.editors:
                editor.update_target(None)
