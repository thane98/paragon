import json
import logging
import os
from typing import List, Optional, Literal

import pydantic
from pydantic import BaseModel

from paragon.model.fe13_avatar_config import FE13AvatarConfig
from paragon.model.fe14_avatar_config import FE14AvatarConfig
from paragon.model.project import Project


class Configuration(BaseModel):
    projects: List[Project] = []
    remember_project: bool = True
    current_project: Optional[str] = None
    theme: Optional[str] = "Fusion Dark"
    backup: Literal["Smart", "Full", "None"] = "Smart"
    show_animations: bool = False
    log_level: int = logging.INFO
    font: Optional[str] = None
    map_editor_zoom: int = 1
    sync_coordinate_changes: bool = True
    fe13_avatar: FE13AvatarConfig = pydantic.Field(default_factory=FE13AvatarConfig)
    fe14_avatar: FE14AvatarConfig = pydantic.Field(default_factory=FE14AvatarConfig)

    def set_current_project(self, project: Project):
        self.current_project = project.get_id()

    @staticmethod
    def load(path) -> "Configuration":
        logging.info("Loading configuration...")
        path = os.path.abspath(path)
        if not os.path.exists(path):
            logging.warn(
                f'paragon.json was not found at path "{path}". Using default configuration...'
            )
            return Configuration()
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_config = json.load(f)
                return Configuration(**raw_config)
        except:
            logging.exception(f"Failed to load config {path}.")
            return Configuration()

    def save(self, path):
        logging.info("Saving configuration...")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.dict(), f, indent=2, ensure_ascii=False)
        except:
            logging.exception(f"Failed to save config {path}.")
            raise

    @staticmethod
    def available_themes() -> List[str]:
        return ["Native", "Fusion", "Fusion Dark"]
