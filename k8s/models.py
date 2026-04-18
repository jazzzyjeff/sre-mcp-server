from pydantic import BaseModel
from typing import Optional


class Pod(BaseModel):
    name: str
    namespace: str
    status: str
    node: Optional[str] = None
    restart_count: int


class Deployment(BaseModel):
    name: str
    namespace: str
    desired: int
    ready: int
    available: int
    image: str


class Event(BaseModel):
    namespace: str
    name: str
    reason: str
    message: str
    count: int
    first_time: Optional[str] = None
    last_time: Optional[str] = None
