from typing import Dict, List

from pydantic import BaseModel


class FE15EventSymbols(BaseModel):
    translations: Dict[str, str]
    args: Dict[str, List[int]]
