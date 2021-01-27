from paragon.ui.states.state import State


class FindProjectState(State):
    def run(self, **kwargs):
        ms = kwargs["main_state"]
        projects = ms.config.projects
        cur = ms.config.current_project
        if project := next((p for p in projects if p.get_id() == cur), None):
            ms.sm.transition("LoadProject", main_state=ms, project=project)
        else:
            ms.sm.transition("SelectProject", main_state=ms)

    def get_name(self) -> str:
        return "FindProject"
