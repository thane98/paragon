from module.extensions.fe14_character_module_extension import FE14CharacterModuleExtension
from module.module import Module
from module.properties.property_container import PropertyContainer


class FE14PersonModuleExtension(FE14CharacterModuleExtension):
    def get_display_name(self, module: Module, entry: PropertyContainer):
        display_name = super().get_display_name(module, entry)
        if display_name and display_name.startswith("PID_"):
            return display_name
        return "%s [%s]" % (entry.get_display_name(), entry.get_key())
