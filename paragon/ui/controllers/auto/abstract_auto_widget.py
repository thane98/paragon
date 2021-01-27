class AbstractAutoWidget:
    def __init__(self, state):
        self.ms = state.main_state
        self.gs = state.game_state
        self.data = self.gs.data

    def set_target(self, rid):
        raise NotImplementedError
