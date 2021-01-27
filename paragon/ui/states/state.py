import abc


class State(abc.ABC):
    @abc.abstractmethod
    def run(self, **kwargs):
        pass

    def on_exit(self):
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        pass
