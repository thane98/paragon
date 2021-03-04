from PySide2.QtWidgets import QWidget, QGridLayout, QSizePolicy
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class Grid(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)
        layout = QGridLayout()
        self.widgets = []
        for cell in spec.cells:
            w = state.generator.generate_top_level(state, cell.inner)
            layout.addWidget(w, cell.row, cell.column, cell.row_span, cell.column_span)
            self.widgets.append(w)
            layout.setRowStretch(cell.row, 0 if cell.no_stretch else 1)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer, layout.rowCount(), 0, 1, layout.columnCount())
        self.setLayout(layout)

    def set_target(self, target):
        for widget in self.widgets:
            widget.set_target(target)
