import logging
from abc import abstractmethod, ABC
from copy import copy

from module.location import location_strategy_from_json
from module.properties.property_container import PropertyContainer
from utils.checked_json import read_key_optional


class Module(ABC):
    def __init__(self, js):
        self.name = js["name"]
        self.unique = read_key_optional(js, "unique", False)
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
    def _update_post_shallow_copy_fields(self):
        raise NotImplementedError

    def try_commit_changes(self):
        try:
            self.commit_changes()
        except:
            logging.exception("Failed to commit changes to module %s." % self.name)
