import json
import logging
from typing import List, Optional
from pydantic import BaseModel
from paragon.model.project import Project


class Configuration(BaseModel):
    projects: List[Project] = []
    remember_project: bool = True
    current_project: Optional[str] = None
    theme: Optional[str] = None

    def set_current_project(self, project: Project):
        self.current_project = project.get_id()

    @staticmethod
    def load(path) -> "Configuration":
        logging.debug("Loading configuration...")
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_config = json.load(f)
                return Configuration(**raw_config)
        except:
            logging.exception(f"Failed to load config {path}.")
            return Configuration()

    def save(self, path):
        logging.debug("Saving configuration...")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.dict(), f, indent=2, ensure_ascii=False)
        except:
            logging.exception(f"Failed to save config {path}.")
            raise
