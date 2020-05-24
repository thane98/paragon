from operator import methodcaller

from core.conversation.game_script_scanner import GameScriptScanner, List
from core.conversation.paragon_script_parser import ParagonScriptParser
from model.conversation.command import PrintCommand, GenderDependentMessageCommand, PrintAvatarNameCommand, Command


def game_to_paragon(game_script: str):
    scanner = GameScriptScanner()
    commands = scanner.scan(game_script)
    return commands_to_paragon(commands)


def commands_to_paragon(commands: List[Command]):
    current_text = []
    result = []
    for command in commands:
        command_text = command.to_paragon_script()
        if not command_text:
            continue
        if not isinstance(command, PrintCommand):
            command_text = "$" + command_text
        if isinstance(command, (PrintCommand, PrintAvatarNameCommand, GenderDependentMessageCommand)):
            current_text.append(command_text)
        elif command.is_pause():
            result.append("".join(current_text))
            result.append(command_text)
            result.append("")
            current_text.clear()
        else:
            result.append(command_text)
    return "\n".join(result)


def paragon_to_game(paragon_script: str) -> str:
    commands = paragon_to_commands(paragon_script)
    result = "".join(map(methodcaller("to_game_script"), commands))
    return result


def commands_to_game(commands: List[Command]) -> str:
    return "".join(map(methodcaller("to_game_script"), commands))


def paragon_to_commands(paragon_script: str) -> List[Command]:
    parser = ParagonScriptParser()
    return parser.parse(paragon_script)
