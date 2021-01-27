import os
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class EnumLoader:
    def __init__(self, path):
        self.path = os.path.join(path)
        self.loaded_enums = {}

    def load(self, enum_name: str):
        if enum_name in self.loaded_enums:
            return self.loaded_enums[enum_name]
        else:
            path = os.path.join(self.path, enum_name + ".yml")
            with open(path, "r", encoding="utf-8") as f:
                enum_mappings = yaml.load(f, Loader=Loader)
            self.loaded_enums[enum_name] = enum_mappings
            return enum_mappings
