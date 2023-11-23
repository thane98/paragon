from PySide6.QtWidgets import QGroupBox, QFormLayout


class Ui_UnionWidget(QGroupBox):
    def __init__(self):
        super().__init__()

        self.setTitle("Variants")

        layout = QFormLayout()
        self.setLayout(layout)
