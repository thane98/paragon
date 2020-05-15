import logging
from abc import abstractmethod, ABC
from copy import copy
from typing import List, Tuple

from core.export_capabilities import ExportCapabilities
from module.location import location_strategy_from_json
from module.properties.property_container import PropertyContainer


class Module(ABC):
    def __init__(self, js):
        self.name = js["name"]
        self.unique = js.get("unique", False)
        if self.unique:
            self.file = js["file"]
        else:
            self.file = None
        self.type = js["type"]
        self.location_strategy = location_strategy_from_json(js["location"])
        self.archive = None
        self.element_template = PropertyContainer.from_json(js["properties"])
        self.display_property = self.element_template.display_property_name
        self.fallback_display_property = self.element_template.fallback_display_property_name
        self.id_property = self.element_template.id_property_name
        self.parent_path_from_base = None

        from module.extensions import extension_factory
        extension_name = js.get("extension")
        self.extension = extension_factory.get_extension_from_string(extension_name)

    def duplicate(self) -> "Module":
        result = copy(self)
        result._update_post_shallow_copy_fields()
        return result

    @abstractmethod
    def find_base_address_for_element(self, element):
        raise NotImplementedError

    @abstractmethod
    def attach_to(self, archive):
        raise NotImplementedError

    @abstractmethod
    def commit_changes(self):
        raise NotImplementedError

    @abstractmethod
    def children(self) -> List[Tuple[PropertyContainer, str]]:
        pass

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        return ExportCapabilities([])

    @abstractmethod
    def import_values_from_dict(self, values: dict):
        pass

    @abstractmethod
    def _update_post_shallow_copy_fields(self):
        raise NotImplementedError

    def try_commit_changes(self) -> bool:
        try:
            self.commit_changes()
            return True
        except:
            logging.exception("Failed to commit changes to module %s." % self.name)
            return False
