import logging
from typing import Dict, Optional

from model.texture import Texture


# This can probably be a global service. It -should- work for any game.
class FE14AssetsService:
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def load_arc(self, path: str) -> Optional[Dict[str, Texture]]:
        try:
            raw_textures_map = self.filesystem.open_arc_file(path)

            result = {}
            for key, raw_texture in raw_textures_map.items():
                result[key] = Texture(raw_texture)
            return result
        except:
            logging.debug("Failed to load arc at path %s." % path)
            return None
