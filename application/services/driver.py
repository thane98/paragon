import logging
from model.project import Project
from services.common_module_service import CommonModuleService
from services.dedicated_editors_service import DedicatedEditorsService
from services.module_data_service import ModuleDataService
from services.module_service import ModuleService
from services.open_files_service import OpenFilesService
from services.service_locator import locator


class Driver:
    def __init__(self, project: Project):
        logging.info("Initializing driver.")
        self._project = project
        locator.register_scoped("Driver", self)
        locator.register_scoped("OpenFilesService", OpenFilesService(project.filesystem))
        locator.register_scoped("ModuleDataService", ModuleDataService())
        locator.register_scoped("ModuleService", ModuleService(project.game))
        locator.get_scoped("ModuleService").attach_to_files()
        locator.register_scoped("CommonModuleService", CommonModuleService())
        locator.register_scoped("DedicatedEditorsService", DedicatedEditorsService(project.game))

        logging.info("Driver initialized successfully.")
        locator.get_static("SettingsService").cache_project(project)

    @staticmethod
    def save():
        locator.get_scoped("DedicatedEditorsService").save()
        locator.get_scoped("ModuleService").save()
        locator.get_scoped("CommonModuleService").save()
        locator.get_scoped("OpenFilesService").save()

    @staticmethod
    def close_archive(archive):
        locator.get_scoped("OpenFilesService").close_archive(archive)
        locator.get_scoped("CommonModuleService").close_modules_using_archive(archive)

    def get_project(self) -> Project:
        return self._project
