import logging
import os
from typing import List

from model.module import Module, create_module_from_path
from model.module_model import ModuleModel
from model.project import Game
from services.open_files_service import OpenFilesService
from services.service_locator import locator


class ModuleService:
    def __init__(self, game: Game):
        self._modules = {}
        self._common_module_templates = {}

        modules = self._open_modules_in_dir(self._get_module_dir_from_game(game))
        for module in modules:
            if module.unique:
                self._modules[module.name] = module
            else:
                self._common_module_templates[module.name] = module
        self._modules = {k: self._modules[k] for k in sorted(self._modules)}
        modules = sorted(modules, key=lambda mod: mod.name)
        self._module_model = ModuleModel(modules)

    @staticmethod
    def _get_module_dir_from_game(game: Game):
        if game == Game.FE13.value:
            return "Modules/FE13/"
        elif game == Game.FE14.value:
            return "Modules/FE14/"
        else:
            return "Modules/FE15/"

    def _open_modules_in_dir(self, dir_path: str) -> List[Module]:
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

    def attach_to_files(self):
        open_files_service: OpenFilesService = locator.get_scoped("OpenFilesService")
        archive = None
        for module in self._modules.values():
            if module.file:
                try:
                    logging.info("Attaching module %s to archive %s" % (module.name, module.file))
                    archive = open_files_service.open(module.file)
                    module.attach_to(archive)
                except:
                    logging.exception("Failed to attach module %s to file %s" % (module.name, module.file))
                    open_files_service.close_archive(archive)

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
        open_files_service: OpenFilesService = locator.get_scoped("OpenFilesService")
        for module in self._modules.values():
            if module.archive and open_files_service.is_archive_in_use(module.archive):
                logging.info("Committing changes from " + module.name + ".")
                module.commit_changes()  # TODO: Wrap this in a try
            else:
                logging.info("Never used " + module.name + ". Nothing to commit.")
