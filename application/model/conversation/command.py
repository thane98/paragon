from abc import ABC, abstractmethod

from model.conversation.conversation_controller import ConversationController


class Command(ABC):
    @abstractmethod
    def run(self, controller: ConversationController):
        pass

    @abstractmethod
    def to_game_script(self) -> str:
        pass


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
        controller.push_portrait(self.portrait_name)

    def to_game_script(self) -> str:
        return "$Wm%s" % self.portrait_name


class SetPortraitPositionCommand(Command):
    def __init__(self, new_position: int):
        self.new_position = new_position

    def run(self, controller: ConversationController):
        controller.set_portrait_position(self.new_position)

    def to_game_script(self) -> str:
        return str(self.new_position) + "$w0"


class SetNameCommand(Command):
    def __init__(self, new_name: str):
        self.new_name = new_name

    def run(self, controller: ConversationController):
        controller.set_name(self.new_name)

    def to_game_script(self) -> str:
        return "$Ws" + self.new_name


class SetEmotionCommand(Command):
    def __init__(self, new_emotion: str):
        self.new_emotion = new_emotion

    def run(self, controller: ConversationController):
        controller.set_emotion(self.new_emotion)

    def to_game_script(self) -> str:
        return "$Wa$E%s," % self.new_emotion


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


class ClearMessageCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$p"
