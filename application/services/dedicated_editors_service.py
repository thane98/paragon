import logging

from model.project import Game
from model.qt.services_model import ServicesModel
from services.fe14.chapter_service import ChapterService
from services.fe14.dialogue_service import DialogueService
from services.fe14.supports_service import SupportsService
from services.service_locator import locator

FE14_SERVICES = {
    "SupportsService": SupportsService,
    "DialogueService": DialogueService,
    "ChapterService": ChapterService
}


class DedicatedEditorsService:
    def __init__(self, game: Game):
        (self._services, self._services_model) = self._create_services_model_for_game(game)

    @staticmethod
    def _create_services_model_for_game(game):
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
        for service in self._services.values():
            logging.info("Committing changes from service " + service.get_display_name())
            service.save()
        logging.info("Done saving changes from dedicated editors.")

    def get_editor_service(self, service_name):
        return self._services[service_name]

    def get_dedicated_editors_model(self):
        return self._services_model
