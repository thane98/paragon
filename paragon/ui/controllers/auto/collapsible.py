from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.views.ui_collapsible import Ui_Collapsible


class Collapsible(AbstractAutoWidget, Ui_Collapsible):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        Ui_Collapsible.__init__(self)
        self.inner = state.generator.generate_top_level(state, spec.inner)
        self.inner.setVisible(False)
        self.layout().addWidget(self.inner)

        self.toggle.clicked.connect(self._toggle)

    def _toggle(self):
        self.inner.setVisible(not self.inner.isVisible())

    def set_target(self, rid):
        self.inner.set_target(rid)
