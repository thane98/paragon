from typing import List, Union, Tuple

from PySide6.QtWidgets import QLayout, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout


def wrap_layout(layout: QLayout, parent=None) -> QWidget:
    widget = QWidget(parent)
    widget.setLayout(layout)
    return widget


def make_vbox(
    widgets: List[Union[QLayout, QWidget]], spacing=10, margins=True, parent=None
) -> QVBoxLayout:
    vbox = QVBoxLayout(parent)
    if not margins:
        vbox.setContentsMargins(0, 0, 0, 0)
    vbox.setSpacing(spacing)
    for widget in widgets:
        if isinstance(widget, QLayout):
            vbox.addWidget(wrap_layout(widget))
        else:
            vbox.addWidget(widget)
    return vbox


def make_hbox(
    widgets: List[Union[QLayout, QWidget]], spacing=10, margins=True, parent=None
) -> QHBoxLayout:
    hbox = QHBoxLayout(parent)
    if not margins:
        hbox.setContentsMargins(0, 0, 0, 0)
    hbox.setSpacing(spacing)
    for widget in widgets:
        if isinstance(widget, QLayout):
            hbox.addWidget(wrap_layout(widget))
        else:
            hbox.addWidget(widget)
    return hbox


def make_form(
    widgets: List[Tuple[str, Union[QLayout, QWidget]]],
    spacing=10,
    margins=True,
    parent=None,
) -> QFormLayout:
    form = QFormLayout(parent)
    if not margins:
        form.setContentsMargins(0, 0, 0, 0)
    form.setSpacing(spacing)
    for label, widget in widgets:
        if isinstance(widget, QLayout):
            form.addRow(label, wrap_layout(widget))
        else:
            form.addRow(label, widget)
    return form
