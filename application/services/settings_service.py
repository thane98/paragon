import json
import logging
from typing import Optional, List
from model.project import Project
from model.qt.project_model import ProjectModel


class SettingsService:
    def __init__(self):
        logging.info("Loading settings from disk.")
        try:
            with open("paragon.json", "r", encoding="utf-8") as f:
                js = json.load(f)
                self._remember_last_project = js.get("remember_last_project", True)
                self._cached_project = js.get("cached_project", None)
                self._project_model = ProjectModel(self._read_known_projects(js))
                self._theme = js.get("theme")
                self._remember_exports = js.get("remember_exports", True)
            logging.info("Successfully loaded settings from disk.")
        except:
            logging.exception("Unable to load settings. Using defaults.")
            self._cached_project = None
            self._project_model = ProjectModel([])
            self._remember_last_project = True
            self._remember_exports = True
            self._theme = None

    def save_settings(self):
        logging.info("Saving settings.")

        settings_dict = {
            "remember_last_project": self._remember_last_project,
            "cached_project": self._cached_project,
            "theme": self._theme,
            "remember_exports": self._remember_exports,
            "projects": self._create_projects_entry()
        }

        logging.info("Serialized settings. Writing to disk...")
        try:
            with open("paragon.json", "w", encoding="utf-8") as f:
                json.dump(settings_dict, f, indent=4, ensure_ascii=False)
            logging.info("Successfully wrote settings to disk.")
        except IOError:
            logging.exception("Unable to write settings to disk.")

    def save(self, project):
        self._cached_project = self._project_model.projects.index(project)
        self.save_settings()

    def _create_projects_entry(self):
        result = []
        for project in self._project_model.projects:
            result.append(project.to_dict())
        return result

    def get_cached_project(self) -> Optional[Project]:
        if not self.has_cached_project():
            return None
        projects = self._project_model.projects
        return projects[self._cached_project]

    def has_cached_project(self) -> bool:
        if not self._remember_last_project:
            return False
        return self._cached_project is not None and self._cached_project in range(0, self._project_model.rowCount())

    def get_theme(self) -> Optional[str]:
        return self._theme

    def set_theme(self, theme: Optional[str]):
        self._theme = theme

    def get_project_model(self) -> ProjectModel:
        return self._project_model

    def should_remember_last_project(self) -> bool:
        return self._remember_last_project

    def set_remember_last_project(self, remember_last_project: bool):
        self._remember_last_project = remember_last_project

    def get_remember_exports(self) -> bool:
        return self._remember_exports

    def set_remember_exports(self, new_value: bool):
        self._remember_exports = new_value

    def _read_known_projects(self, js) -> List[Project]:
        projects = js.get("projects", [])
        result = []
        for project_json in projects:
            project = self._read_project_from_json(project_json)
            if project:
                result.append(project)
        return result

    @staticmethod
    def _read_project_from_json(js):
        try:
            return Project.from_json(js)
        except:
            logging.exception("Could not read project.")
            return None
