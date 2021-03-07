from typing import Literal, Optional

from pydantic.main import BaseModel


class FE14AvatarConfig(BaseModel):
    name: str = "Corrin"
    gender: Literal["Male", "Female"] = "Male"
    portraits: Optional[str] = "FID_マイユニ_男1_顔A"
    accessory: Optional[str] = None
