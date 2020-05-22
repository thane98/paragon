from abc import ABC, abstractmethod
from typing import List

from model.conversation.conversation_controller import ConversationController


class Command(ABC):
    @abstractmethod
    def run(self, controller: ConversationController):
        pass

    @abstractmethod
    def to_game_script(self) -> str:
        pass

    def is_pause(self) -> bool:
        return False


class PlayerMentionedCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$a"


class SetConversationTypeCommand(Command):
    def __init__(self, new_type: int):
        self.new_type = new_type

    def run(self, controller: ConversationController):
        pass  # TODO

    def to_game_script(self) -> str:
        return "$t" + str(self.new_type)


class LoadPortraitsCommand(Command):
    def __init__(self, portrait_name: str):
        self.portrait_name = portrait_name

    def run(self, controller: ConversationController):
        controller.create_speaker(self.portrait_name)

    def to_game_script(self) -> str:
        return "$Wm" + self.portrait_name


class SetCursorPositionCommand(Command):
    def __init__(self, new_position: int):
        self.new_position = new_position

    def run(self, controller: ConversationController):
        controller.set_cursor_position(self.new_position)

    def to_game_script(self) -> str:
        return str(self.new_position)


class GetActiveSpeakerCommand(Command):
    def run(self, controller: ConversationController):
        controller.apply_to_active_speaker()

    def to_game_script(self) -> str:
        return "$w0"


class SetSpeakerCommand(Command):
    def __init__(self, new_speaker: str):
        self.new_speaker = new_speaker

    def run(self, controller: ConversationController):
        controller.set_active_speaker(self.new_speaker)

    def to_game_script(self) -> str:
        return "$Ws" + self.new_speaker


class BeginMessageCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Wa"


class SetEmotionCommand(Command):
    def __init__(self, new_emotions: List[str]):
        self.new_emotions = new_emotions

    def run(self, controller: ConversationController):
        controller.set_emotions(self.new_emotions)

    def to_game_script(self) -> str:
        return "$E%s," % ",".join(self.new_emotions)


class PlayVoiceCommand(Command):
    def __init__(self, voice_line: str):
        self.voice_line = voice_line

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Svp" + self.voice_line


class GenderDependentMessageCommand(Command):
    def __init__(self, message_1, message_2):
        self.message_1 = message_1
        self.message_2 = message_2

    def run(self, controller: ConversationController):
        pass  # TODO

    def to_game_script(self) -> str:
        return "$G%s,%s" % (self.message_1, self.message_2)


class PrintCommand(Command):
    def __init__(self, message: str):
        self.message = message

    def run(self, controller: ConversationController):
        controller.push_message(self.message)

    def to_game_script(self) -> str:
        return self.message


class PrintAvatarNameCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Nu"


class PlayMessageCommand(Command):
    def run(self, controller: ConversationController):
        controller.dump()

    def to_game_script(self) -> str:
        return ""


class PauseCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$k"

    def is_pause(self) -> bool:
        return True


class PauseNewlineCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return r"$k\n"

    def is_pause(self) -> bool:
        return True


class ClearMessageCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$p"


class DeleteSpeakerCommand(Command):
    def run(self, controller: ConversationController):
        controller.set_delete_flag()

    def to_game_script(self) -> str:
        return "$Wd"
