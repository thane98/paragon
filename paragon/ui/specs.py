import os
from pathlib import Path

import yaml
from yaml import Loader

from paragon.model import auto_ui
from paragon.model.auto_ui import UISpec


class Specs:
    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def load(path, language):
        language_dir = os.path.join(path, language.value)
        auto_ui.update_forward_refs()
        specs = Specs._load_specs_from_dir(path)
        if os.path.exists(language_dir):
            specs.update(Specs._load_specs_from_dir(language_dir))
        return Specs(specs)

    @staticmethod
    def _load_specs_from_dir(path):
        specs = {}
        for filename in Path(path).glob("*.yml"):
            with open(filename, "r", encoding="utf-8") as f:
                raw_yaml = yaml.load(f, Loader=Loader)
                spec = UISpec(**raw_yaml)
                specs[spec.typename] = spec
        return specs

    def get_dimensions(self, typename):
        if spec := self.specs.get(typename):
            if spec.width and spec.height:
                return spec.width, spec.height
            else:
                return None
        else:
            return None

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
