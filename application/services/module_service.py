import logging
import os
from typing import List, Tuple

from core.export_capabilities import ExportCapabilities
from model.project import Project
from model.qt.module_model import ModuleModel
from module.module import Module
from module.module_factory import create_module_from_path
from services.open_files_service import OpenFilesService
from services.service_locator import locator


class ModuleService:
    def __init__(self, project: Project):
        self._modules = {}
        self._common_module_templates = {}

        modules = self._open_modules_in_dir(project.get_module_dir())
        for module in modules:
            if module.unique:
                self._modules[module.name] = module
            else:
                self._common_module_templates[module.name] = module
        self._module_model = None

    def _open_modules_in_dir(self, dir_path: str) -> List[Module]:
        logging.info("Reading modules from " + dir_path)
        modules = []
        files = os.walk(dir_path)
        for parent_path, _, file_names in files:
            for file in file_names:
                if file.endswith(".json"):
                    logging.info("Found module " + file + ". Attempting to open.")
                    module = self._try_open_module(os.path.join(parent_path, file))
                    if module:
                        logging.info("Successfully opened " + module.name + ".")
                        module.parent_path_from_base = parent_path.replace(dir_path, "")
                        modules.append(module)
                    else:
                        logging.error("Failed to module at " + file + ".")
        return modules

    @staticmethod
    def _try_open_module(module_path):
        try:
            return create_module_from_path(module_path)
        except:
            logging.exception("Error while opening module.")
            return None

    def load_files_and_generate_model(self):
        successful_modules = self._attach_to_files()
        self._modules = {module.name: self._modules[module.name] for module in successful_modules}
        successful_modules.extend({mod for mod in self._common_module_templates.values()})
        modules = sorted(successful_modules, key=lambda mod: mod.name)
        self._module_model = ModuleModel(modules)

    def _attach_to_files(self) -> List[Module]:
        open_files_service: OpenFilesService = locator.get_scoped("OpenFilesService")
        successful_modules = []
        for module in self._modules.values():
            if module.file:
                try:
                    logging.info("Attaching module %s to archive %s" % (module.name, module.file))
                    archive = open_files_service.open(module.file)
                    module.attach_to(archive)
                    successful_modules.append(module)
                except:
                    logging.exception("Failed to attach module %s to file %s" % (module.name, module.file))
                    # open_files_service.close_archive(archive)
                    # TODO: Use reference counting for archives to prevent bugs
                    #       related to close_archive.
            else:
                successful_modules.append(module)
        return successful_modules

    def get_module(self, module_name: str) -> Module:
        return self._modules[module_name]

    def get_common_module_template(self, module_name: str) -> Module:
        return self._common_module_templates[module_name]

    def get_module_model(self):
        return self._module_model

    @staticmethod
    def set_module_in_use(module):
        if not module.archive:
            raise ValueError
        open_files_service: OpenFilesService = locator.get_scoped("OpenFilesService")
        open_files_service.set_archive_in_use(module.archive)

    def is_archive_used_by_module(self, archive):
        for module in self._modules.values():
            if module.archive == archive:
                return True
        return False

    def save(self):
        logging.info("Committing module changes.")
        success = True
        open_files_service: OpenFilesService = locator.get_scoped("OpenFilesService")
        for module in self._modules.values():
            if module.archive and open_files_service.is_archive_in_use(module.archive):
                logging.info("Committing changes from " + module.name + ".")
                if not module.try_commit_changes():
                    success = False
            else:
                logging.info("Never used " + module.name + ". Nothing to commit.")
        return success

    def children(self) -> List[Tuple[Module, str]]:
        return [(module, module.name) for module in self._modules.values()]

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        return ExportCapabilities([])
