from lark import Transformer

from paragon.model.fe15_event_command import FE15EventCommand
from paragon.model.fe15_event_sequence import FE15EventSequence


class FE15EventScriptTransformer(Transformer):
    def __init__(self, arg_symbols):
        super().__init__()
        self.symbols = arg_symbols

    def start(self, value):
        return value

    def sequence(self, value):
        return FE15EventSequence(value[0], value[1:])

    def any_command(self, value):
        return value[0]

    def conditional_command(self, value):
        command = value[-1]
        return FE15EventCommand(
            command.name,
            condition_1=value[0],
            condition_2=value[1],
            args=command.args,
        )

    def command(self, value):
        identifier, arglist = value[0], value[1] if len(value) > 1 else []
        if identifier not in self.symbols:
            raise Exception(f"Unknown command: {identifier}")
        else:
            # TODO: Signature validation and default arguments
            return FE15EventCommand(identifier, args=arglist)

    def arglist(self, value):
        return value

    def argument(self, value):
        return value[0] if value else None

    def condition(self, value):
        if value:
            (s,) = value
            return s[1:-1]
        else:
            return None

    def number(self, value):
        return int(value[0])

    def string(self, value):
        (s,) = value
        return s[1:-1]

    def identifier(self, value):
        return value[0].value
