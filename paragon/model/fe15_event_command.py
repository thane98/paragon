import dataclasses
from typing import Optional, List, Union


@dataclasses.dataclass
class FE15EventCommand:
    name: str
    condition_1: Optional[str] = None
    condition_2: Optional[str] = None
    args: List[Union[str, int]] = dataclasses.field(default_factory=list)

    def to_paragon_format(self) -> str:
        command = (
            self.name
            + "("
            + ", ".join([self._convert_arg_to_string(a) for a in self.args])
            + ");"
        )
        condition = self._format_condition()
        return condition + "\n        " + command if condition else command

    @staticmethod
    def _convert_arg_to_string(arg):
        if type(arg) is str:
            return '"' + arg + '"'
        elif arg is None:
            return "null"
        else:
            return str(arg)

    def _format_condition(self) -> str:
        if self.condition_1 and self.condition_2:
            return f'if("{self.condition_1}" == "{self.condition_2}")'
        elif self.condition_1 or self.condition_2:
            condition_1 = f'"{self.condition_1}"' if self.condition_1 else "null"
            condition_2 = f'"{self.condition_2}"' if self.condition_2 else "null"
            return f"if({condition_1} == {condition_2})"
        else:
            return ""
