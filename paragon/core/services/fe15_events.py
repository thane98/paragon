import logging
import os
from typing import List

import lark
import yaml

from yaml import Loader

from paragon.core.misc.fe15_event_script_transformer import FE15EventScriptTransformer
from paragon.model.fe15_event_command import FE15EventCommand
from paragon.model.fe15_event_sequence import FE15EventSequence
from paragon.model.fe15_event_symbols import FE15EventSymbols


_ARG_ID_MAPPING = [
    ("argument_1", "string"),
    ("argument_2", "int"),
    ("argument_3", "int"),
    ("argument_4", "string"),
    ("argument_5", "string"),
    ("argument_6", "string"),
]


_DEFAULT_ARGS = [0, 1, 2, 3, 4, 5]


class FE15Events:
    def __init__(self, gd):
        self.gd = gd

        symbols_path = os.path.join("resources", "FE15", "EventSymbols.yml")
        try:
            with open(symbols_path, "r", encoding="utf-8") as f:
                raw_yaml = yaml.load(f, Loader=Loader)
            self.symbols = FE15EventSymbols(**raw_yaml)

            self.inverted_translations = {}
            for k, v in self.symbols.translations.items():
                self.inverted_translations[v] = k
        except:
            logging.exception("Failed to load event script symbols.")
            self.symbols = FE15EventSymbols(translations={}, args={})

        grammar_path = os.path.join("resources", "FE15", "EventGrammar.lark")
        try:
            with open(grammar_path, "r", encoding="utf-8") as f:
                grammar = f.read()
            self.parser = lark.Lark(
                grammar,
                parser="lalr",
                transformer=FE15EventScriptTransformer(self.symbols.args),
            )
        except:
            logging.exception("Failed to load grammar for event scripts.")
            self.parser = None

    def convert_to_paragon_event_script(self, events):
        items = self.gd.items(events, "events")
        sequences = []
        global_sequence_commands = []
        i = 0
        while i < len(items):
            item = items[i]
            i += 1
            if self._is_sequence(item):
                sequence_name = self._translate_to_english(
                    self.gd.string(item, "sequence")
                )
                commands = []
                while i < len(items) and not self._is_sequence(items[i]):
                    item = items[i]
                    i += 1
                    commands.append(self._read_command(item))
                sequences.append(FE15EventSequence(sequence_name, commands))
            else:
                global_sequence_commands.append(self._read_command(item))
        if global_sequence_commands:
            sequences = [
                FE15EventSequence("global", global_sequence_commands)
            ] + sequences
        return "\n\n".join(map(lambda s: s.to_paragon_format(), sequences))

    def _read_command(self, rid):
        name = self._translate_to_english(self.gd.string(rid, "command"))
        args = self._get_command_args(name, rid)
        return FE15EventCommand(
            name=self._translate_to_english(self.gd.string(rid, "command")),
            condition_1=self._translate_to_english(self.gd.string(rid, "condition_1")),
            condition_2=self._translate_to_english(self.gd.string(rid, "condition_2")),
            args=args,
        )

    def _get_command_args(self, name, rid):
        ids = (
            _DEFAULT_ARGS if name not in self.symbols.args else self.symbols.args[name]
        )
        args = []
        for i in ids:
            field_id, field_type = _ARG_ID_MAPPING[i]
            args.append(
                self.gd.string(rid, field_id)
                if field_type == "string"
                else self.gd.int(rid, field_id)
            )
        for i in range(len(args) - 1, -1, -1):
            arg_id = ids[i]
            arg_value = args[i]
            default_value = 0 if type(arg_value) is int else None
            if arg_value == default_value:
                del args[i]
            else:
                break
        return args

    def _is_sequence(self, rid):
        return bool(self.gd.string(rid, "sequence"))

    def convert_to_game_events(self, script: str, rid: int):
        sequences = self.parser.parse(script)
        new_items = self._convert_to_records(sequences)
        old_items = self.gd.items(rid, "events")
        for old_rid in old_items:
            self.gd.delete_instance(old_rid)
        self.gd.set_items(rid, "events", new_items)

    def _convert_to_records(self, sequences: List[FE15EventSequence]) -> List[int]:
        items = []
        global_sequence = self._get_global_sequence(sequences)
        if global_sequence:
            sequences.remove(global_sequence)
            items.extend(self._convert_sequence_to_records(global_sequence))
        for sequence in sequences:
            items.extend(self._convert_sequence_to_records(sequence))
        return items

    def _convert_sequence_to_records(self, sequence: FE15EventSequence) -> List[int]:
        records = []
        sequence_rid = self.gd.new_instance("Event")
        self.gd.set_string(
            sequence_rid, "sequence", self._translate_to_japanese(sequence.name)
        )
        records.append(sequence_rid)
        for command in sequence.commands:
            command_rid = self.gd.new_instance("Event")
            self.gd.set_string(
                command_rid, "command", self._translate_to_japanese(command.name)
            )
            self.gd.set_string(
                command_rid,
                "condition_1",
                self._translate_to_japanese(command.condition_1),
            )
            self.gd.set_string(
                command_rid,
                "condition_2",
                self._translate_to_japanese(command.condition_2),
            )
            symbol = self.symbols.args[command.name]
            for i in range(0, len(command.args)):
                arg_value = command.args[i]
                field_id, field_type = _ARG_ID_MAPPING[symbol[i]]
                if field_type == "string":
                    self.gd.set_string(command_rid, field_id, arg_value)
                else:
                    self.gd.set_int(command_rid, field_id, arg_value)
            records.append(command_rid)
        return records

    @staticmethod
    def _get_global_sequence(sequences: List[FE15EventSequence]):
        return next(filter(lambda s: s.name == "global", sequences), None)

    def _translate_to_english(self, text):
        return self.symbols.translations.get(text, text)

    def _translate_to_japanese(self, text):
        return self.inverted_translations.get(text, text)
