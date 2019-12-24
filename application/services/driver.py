import os
import traceback
from copy import copy
from typing import List
from model.module import Module, create_module_from_path
from model.module_model import ModuleModel
from model.project import Project, Game
from services.module_data_service import ModuleDataService
from services.open_files_service import OpenFilesService
from services.settings_service import SettingsService


class Driver:
    def __init__(self, settings_service: SettingsService, project: Project):
        self.project = project
        self.settings_service = settings_service
        self.open_files_service = OpenFilesService(project.filesystem)
        self.module_data_service = ModuleDataService()
        self.modules = {}
        self.common_module_cache = {}
        self.module_model = self._create_module_model(project)

        # Load every file the current project targets.
        self._attach_to_files()

        self.settings_service.cached_project = project  # We know the project works now, so let's cache it.

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
            raise NotImplementedError

        for module in modules:
            if module.unique:
                self.modules[module.name] = module
        return ModuleModel(modules)

    def _open_modules_in_dir(self, dir_path) -> List[Module]:
        modules = []
        files = os.walk(dir_path)
        for dir_path, _, file_names in files:
            for file in file_names:
                if file.endswith(".json"):
                    module = self._try_open_module(os.path.join(dir_path, file))
                    if module:
                        modules.append(module)
        return modules

    def _try_open_module(self, module_path):
        try:
            return create_module_from_path(self, module_path)
        except Exception:
            print(traceback.format_exc())

    def save(self):
        for module in self.modules.values():
            if module.archive and self.open_files_service.is_archive_in_use(module.archive):
                module.commit_changes()
        for module in self.common_module_cache.values():
            if self.open_files_service.is_archive_in_use(module.archive):
                module.commit_changes()
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
