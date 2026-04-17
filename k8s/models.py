from pydantic import BaseModel
from typing import Optional


class Pod(BaseModel):
    name: str
    namespace: str
    status: str
    node: Optional[str] = None
    restart_count: int

