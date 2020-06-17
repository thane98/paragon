import logging
import os

from PySide2.QtWidgets import QWidget, QFileDialog

from services.abstract_editor_service import AbstractEditorService
from services.service_locator import locator
from ui.error_dialog import ErrorDialog
from ui.fe14.fe14_field_editor import FE14FieldEditor


class FieldService(AbstractEditorService):
    def __init__(self):
        self.error_dialog = ErrorDialog("Failed to open field data.")
        self.editors = {}

    def get_editor(self) -> QWidget:
        file_name, ok = QFileDialog.getOpenFileName()
        if not ok:
            return None
        if file_name in self.editors:
            return self.editors[file_name]
        base_name = os.path.basename(file_name).replace(".lz", "")
        gamedata_field_path = "/GameData/Field/" + base_name
        try:
            common_module_service = locator.get_scoped("CommonModuleService")
            module_service = locator.get_scoped("ModuleService")
            parts_template = module_service.get_common_module_template("Field Parts")
            refer_template = module_service.get_common_module_template("Field Refer")
            files_template = module_service.get_common_module_template("Field Files")
            gamedata_field_template = module_service.get_common_module_template("Field")

            parts_module = common_module_service.open_common_module(parts_template, file_name)
            refer_module = common_module_service.open_common_module(refer_template, file_name)
            files_module = common_module_service.open_common_module(files_template, file_name)
            gamedata_field_module = common_module_service.open_common_module(gamedata_field_template,
                                                                             gamedata_field_path)

            module_service.set_module_in_use(parts_module)
            module_service.set_module_in_use(refer_module)
            module_service.set_module_in_use(files_module)
            module_service.set_module_in_use(gamedata_field_module)
            self.editors[file_name] = FE14FieldEditor(
                [parts_module, refer_module, files_module, gamedata_field_module], base_name)
            return self.editors[file_name]
        except:
            logging.exception("Failed to open field data.")
            return self.error_dialog

    def get_display_name(self) -> str:
        return "Field / Map Appearance"

    def save(self):
        pass
