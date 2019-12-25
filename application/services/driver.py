import logging
import os

from copy import copy
from typing import List
from model.module import Module, create_module_from_path
from model.module_model import ModuleModel
from model.project import Project, Game
from services import service_locator
from services.module_data_service import ModuleDataService
from services.open_files_service import OpenFilesService


class Driver:
    def __init__(self, project: Project):
        logging.info("Initializing driver.")

        self.project = project
        self.settings_service = service_locator.locator.get_static("SettingsService")
        self.open_files_service = OpenFilesService(project.filesystem)
        self.module_data_service = ModuleDataService()
        self.modules = {}
        self.common_module_cache = {}

        # Add services to the service locator.
        service_locator.locator.register_scoped("Driver", self)
        service_locator.locator.register_scoped("OpenFilesService", self.open_files_service)
        service_locator.locator.register_scoped("ModuleDataService", self.module_data_service)

        logging.info("Initialized driver services. Reading modules and files...")

        # Load every file the current project targets.
        self.module_model = self._create_module_model(project)
        self._attach_to_files()

        # We know the project works now, so let's cache it.
        logging.info("Read all modules.")
        self.settings_service.cached_project = project

    def _attach_to_files(self):
        for module in self.modules.values():
            if module.file:
                archive = self.open_files_service.open(module.file)
                module.attach_to(archive)

    def _create_module_model(self, project) -> ModuleModel:
        if project.game == Game.FE13.value:
            modules = self._open_modules_in_dir("Modules/FE13/")
        elif project.game == Game.FE14.value:
            modules = self._open_modules_in_dir("Modules/FE14/")
        elif project.game == Game.FE15.value:
            modules = self._open_modules_in_dir("Modules/FE15/")
        else:
            logging.error("Unrecognized game. Unable to read modules.")
            raise NotImplementedError

        for module in modules:
            if module.unique:
                self.modules[module.name] = module
        return ModuleModel(modules)

    def _open_modules_in_dir(self, dir_path) -> List[Module]:
        logging.info("Reading modules from " + dir_path)
        modules = []
        files = os.walk(dir_path)
        for dir_path, _, file_names in files:
            for file in file_names:
                if file.endswith(".json"):
                    logging.info("Found module " + file + ". Attempting to open.")
                    module = self._try_open_module(os.path.join(dir_path, file))
                    if module:
                        logging.info("Successfully opened " + module.name + ".")
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

    def save(self):
        logging.info("Beginning save. Committing module changes to files...")
        for module in self.modules.values():
            if module.archive and self.open_files_service.is_archive_in_use(module.archive):
                logging.info("Committing changes from " + module.name + ".")
                module.commit_changes()
            else:
                logging.info("Never used " + module.name + ". Nothing to commit.")
        for module in self.common_module_cache.values():
            logging.info("Committing changes from " + module.name + ".")
            module.commit_changes()

        logging.info("Committed all module changes.")
        self.open_files_service.save()

    def handle_open_for_common_module(self, base_module: Module, file_path: str):
        if (base_module, file_path) in self.common_module_cache:
            return self.common_module_cache[(base_module, file_path)]

        # First, convert the path selected by the user to a relative path in the roms.
        valid_path = self.open_files_service.to_valid_path_in_filesystem(file_path)
        if not valid_path:
            raise ValueError

        module = copy(base_module)
        module.update_post_shallow_copy_fields()
        archive = self.open_files_service.open(valid_path)
        module.attach_to(archive)
        self.common_module_cache[(base_module, file_path)] = module
        return module

    def set_module_used(self, module):
        self.open_files_service.set_archive_in_use(module.archive)
