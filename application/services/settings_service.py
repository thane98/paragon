import json
from model.project import Project


class SettingsService:
    def __init__(self):
        try:
            with open("fefeditor2.json", "r") as f:
                js = json.load(f)
                self.cached_project = self._read_cached_project_from_json(js)
        except (IOError, KeyError, json.JSONDecodeError):
            self.cached_project = None

    def save_settings(self):
        settings_dict = {
            "cached_project": self._created_cached_project_entry()
        }
        try:
            with open("fefeditor2.json", "w") as f:
                json.dump(settings_dict, f)
        except IOError:
            pass  # TODO: Logging

    def _created_cached_project_entry(self):
        if self.cached_project:
            return self.cached_project.to_dict()
        return None

    @staticmethod
    def _read_cached_project_from_json(js):
        try:
            return Project.from_json(js["cached_project"])
        except (FileNotFoundError, KeyError):
            return None
