from typing import Literal, Optional

from pydantic.main import BaseModel


class FE15AvatarConfig(BaseModel):
    name: str = "Placeholder"
    gender: Literal["Male", "Female"] = "Female"
