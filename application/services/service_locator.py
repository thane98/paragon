import logging


class ServiceLocator:
    def __init__(self):
        self.static_services = {}
        self.scoped_services = {}

    def clear_scoped_services(self):
        self.scoped_services.clear()
        logging.info("Cleared scoped services.")

    def register_static(self, name, service):
        self.static_services[name] = service
        logging.info("Registered static service " + name)

    def register_scoped(self, name, service):
        self.scoped_services[name] = service
        logging.info("Registered scoped service " + name)

    def get_static(self, name):
        return self.static_services[name]

    def get_scoped(self, name):
        return self.scoped_services[name]


locator = ServiceLocator()
