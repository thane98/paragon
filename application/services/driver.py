import logging
import os

from model.project import Project
from services.service_locator import locator


class Driver:
    def __init__(self, project: Project):
        logging.info("Initializing driver.")
        if not os.path.exists(project.patch_path) or not os.path.exists(project.rom_path):
            logging.error("Project path or ROM path are no longer valid.")
            raise FileNotFoundError
        self._project = project

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

    @staticmethod
    def close_archive(archive):
        locator.get_scoped("OpenFilesService").close_archive(archive)
        locator.get_scoped("CommonModuleService").close_modules_using_archive(archive)

    def get_project(self) -> Project:
        return self._project
