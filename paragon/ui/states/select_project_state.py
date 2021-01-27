from paragon.ui.controllers.project_select import ProjectSelect
from paragon.ui.states.state import State


class SelectProjectState(State):
    def __init__(self):
        self.view = None

    def run(self, **kwargs):
        ms = kwargs["main_state"]
        self.view = ProjectSelect(ms)
        self.view.show()

    def on_exit(self):
        self.view = None

    def get_name(self) -> str:
        return "SelectProject"
