import os
from pathlib import Path

import yaml

from paragon.model import auto_ui
from paragon.model.auto_ui import UISpec

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class Specs:
    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def load(path):
        auto_ui.update_forward_refs()
        specs = {}
        for filename in Path(path).glob("*.yml"):
            with open(filename, "r", encoding="utf-8") as f:
                raw_yaml = yaml.load(f, Loader=Loader)
                spec = UISpec(**raw_yaml)
                specs[spec.typename] = spec
        return Specs(specs)

    def get_top_level_spec(self, typename):
        if spec := self.specs.get(typename):
            return spec.top_level
        else:
            return None

    def get_field_spec(self, typename, field):
        if spec := self.specs.get(typename):
            return spec.overrides.get(field)
        else:
            return None