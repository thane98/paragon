from typing import Optional

from model.conversation.command import *
from model.conversation.source_position import SourcePosition
from model.conversation.transpiler_error import TranspilerError


class GameScriptScanner:
    def __init__(self):
        self._position = 0
        self._tokens: List[Command] = []
        self._input: Optional[str] = None

    def reset(self):
        self._position = 0
        self._tokens = []
        self._input = None

    def scan(self, input) -> List[Command]:
        self.reset()
        self._input = input
        while self._position < len(self._input):
            if self._peek() == "|":
                self._position += 1
            else:
                next_token = self._next_token()
                if not next_token:
                    break
                else:
                    self._tokens.extend(next_token)
        return self._tokens

    def _next_token(self) -> Optional[List[Command]]:
        next_char = self._peek()
        if next_char == "\0":
            return None
        elif next_char == "$":
            return self._scan_command()
        elif next_char.isdigit():
            return [RepositionSpeakerCommand(self._scan_int())]
        else:
            return [PrintCommand(self._scan_string())]

    def _scan_command(self) -> List[Command]:
        # TODO: This could definitely be more performant.
        self._next()  # Consume the dollar sign.
        three_char_command = self._peek() + self._safe_lookahead(1) + self._safe_lookahead(2)
        two_char_command = self._peek() + self._safe_lookahead(1)
        one_char_command = self._peek()
        if three_char_command == "Svp":
            self._position += 3
            return [PlayVoiceCommand(self._scan_string())]
        elif three_char_command == r"k\n":
            self._position += 3
            return [PlayMessageCommand(), PauseNewlineCommand()]
        elif two_char_command == "Wm":
            self._position += 2
            return [LoadPortraitsCommand(self._scan_string())]
        elif two_char_command == "Ws":
            self._position += 2
            return [SetSpeakerCommand(self._scan_string())]
        elif two_char_command == "w0":
            self._position += 2
            return [GetActiveSpeakerCommand()]
        elif two_char_command == "Wa":
            self._position += 2
            return [BeginMessageCommand()]
        elif two_char_command == "Wd":
            self._position += 2
            return [DeleteSpeakerCommand()]
        elif two_char_command == "Nu":
            self._position += 2
            return [PrintAvatarNameCommand()]
        elif one_char_command == "a":
            self._position += 1
            return [PlayerMentionedCommand()]
        elif one_char_command == "t":
            self._position += 1
            return [SetConversationTypeCommand(self._scan_int())]
        elif one_char_command == "E":
            self._position += 1
            return [SetEmotionCommand(self._scan_string().split(","))]
        elif one_char_command == "G":
            self._position += 1
            messages = self._scan_string().split[","]
            if len(messages) < 2:
                raise TranspilerError(self._source_position(), "Invalid $G command.")
            return [GenderDependentMessageCommand(messages[0], messages[1])]
        elif one_char_command == "k":
            self._position += 1
            return [PlayMessageCommand(), PauseCommand()]
        elif one_char_command == "p":
            self._position += 1
            return [ClearMessageCommand()]
        else:
            print(self._input[self._position:])
            raise TranspilerError(self._source_position(), "Unrecognized command " + three_char_command)

    def _scan_int(self) -> int:
        result = ""
        while self._peek().isdigit():
            result += self._next()
        return int(result)

    def _scan_string(self):
        result = ""
        next_char = self._peek()
        while next_char != "|" and next_char != "$" and next_char != "\0":
            result += self._next()
            next_char = self._peek()
        return result

    def _next(self) -> str:
        if self._position >= len(self._input):
            raise TranspilerError(self._source_position(), "Reached EOL while parsing.")
        result = self._peek()
        self._position += 1
        return result

    def _peek(self) -> str:
        if self._position >= len(self._input):
            return "\0"
        return self._input[self._position]

    def _safe_lookahead(self, amount: int) -> str:
        if self._position + amount >= len(self._input):
            return ""
        return self._input[self._position + amount]

    def _source_position(self) -> SourcePosition:
        return SourcePosition(1, self._position)
