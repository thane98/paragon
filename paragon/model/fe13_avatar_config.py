from typing import Literal, Optional

from pydantic.main import BaseModel


class FE13AvatarConfig(BaseModel):
    name: str = "Robin"
    gender: Literal["Male", "Female"] = "Female"
    portraits: Optional[str] = "FID_マイユニ_少女_顔立ちA"
    accessory: Optional[str] = None
