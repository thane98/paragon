import logging
from typing import List, Tuple, Optional

from core.export_capabilities import ExportCapabilities
from model.project import Game
from model.qt.services_model import ServicesModel
from services.abstract_editor_service import AbstractEditorService
from services.fe14.chapter_service import ChapterService
from services.fe14.dialogue_service import DialogueService
from services.fe14.sound_service import SoundService
from services.fe14.supports_service import SupportsService
from services.service_locator import locator

FE14_SERVICES = {
    "SupportsService": SupportsService,
    "DialogueService": DialogueService,
    "ChapterService": ChapterService,
    "SoundService": SoundService
}


class DedicatedEditorsService:
    def __init__(self, game: Game):
        (self._services, self._services_model) = self._create_services_model_for_game(game)

    @staticmethod
    def _create_services_model_for_game(game: Game):
        if game == Game.FE13.value:
            base = {}
        elif game == Game.FE14.value:
            base = FE14_SERVICES
        else:
            base = {}

        services = {}
        for key, value in base.items():
            service = value()
            services[key] = service
            locator.register_scoped(key, service)
        return services, ServicesModel(services)

    def save(self):
        logging.info("Saving changes from dedicated editors...")
        success = True
        for service in self._services.values():
            logging.info("Committing changes from service " + service.get_display_name())
            try:
                service.save()
            except:
                logging.exception("An error occurred while saving service %s." % service.get_display_name())
                success = False
        logging.info("Done saving changes from dedicated editors.")
        return success

    def get_editor_service(self, service_name: str):
        return self._services[service_name]

    def get_dedicated_editors_model(self) -> ServicesModel:
        return self._services_model

    def children(self):
        return [(service, service.get_display_name(), service.get_display_name())
                for service in self._services.values()]

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        return ExportCapabilities([])

    def import_values_from_json(self, values_json: dict):
        for service_name in values_json:
            service = self._find_service_by_display_name(service_name)
            if not service:
                raise KeyError("Cannot import into non-existent service %s." % service_name)
            else:
                service.import_values_from_json(values_json[service_name])

    def _find_service_by_display_name(self, name: str) -> Optional[AbstractEditorService]:
        for service in self._services.values():
            if service.get_display_name() == name:
                return service
        return None
