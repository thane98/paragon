import json
import logging
import os

from model.project import Project, Game
from module.properties.reference_property import ReferenceProperty
from services.fe14.assets_service import FE14AssetsService
from services.fe14.portrait_service import FE14PortraitService
from services.service_locator import locator


class Driver:
    def __init__(self, project: Project):
        logging.info("Initializing driver.")
        if not os.path.exists(project.patch_path) or not os.path.exists(project.rom_path):
            logging.error("Project path or ROM path are no longer valid.")
            raise FileNotFoundError
        self._project = project
        self._register_game_services()

        # This is only here because there isn't a better place to put it right now.
        # Making a service just to host this isn't worth it.
        # We cannot resolve reference property values until after we've imported everything.
        # So, unresolved references register themselves after importing. That way, we can
        # fix them later.
        self._unresolved_references = []

    def _register_game_services(self):
        if self._project.game == Game.FE14.value:
            locator.register_scoped("AssetsService", FE14AssetsService(self._project.filesystem))
            locator.register_scoped("PortraitService", FE14PortraitService())

    @staticmethod
    def save():
        services_to_save = [
            locator.get_scoped("DedicatedEditorsService"),
            locator.get_scoped("ModuleService"),
            locator.get_scoped("CommonModuleService"),
            locator.get_scoped("OpenFilesService")
        ]

        success = True
        for service in services_to_save:
            if not service.save():
                success = False
        return success

    def import_from_json(self, file_name):
        logging.debug("Importing from file %s." % file_name)
        with open(file_name, "r", encoding="utf-8") as f:
            values_json = json.load(f)
        if "Modules" in values_json:
            locator.get_scoped("ModuleService").import_values_from_json(values_json["Modules"])
        if "Common Modules" in values_json:
            locator.get_scoped("CommonModuleService").import_values_from_json(values_json["Common Modules"])
        if "Services" in values_json:
            locator.get_scoped("DedicatedEditorsService").import_values_from_json(values_json["Services"])
        self._resolve_import_references()
        logging.debug("Importing of file %s completed successfully." % file_name)

    def register_unresolved_import_reference(self, reference: ReferenceProperty):
        self._unresolved_references.append(reference)

    def _resolve_import_references(self):
        for reference in self._unresolved_references:
            reference.resolve()
        self._unresolved_references.clear()

    @staticmethod
    def close_archive(archive):
        locator.get_scoped("OpenFilesService").close_archive(archive)
        locator.get_scoped("CommonModuleService").close_modules_using_archive(archive)

    def get_project(self) -> Project:
        return self._project
