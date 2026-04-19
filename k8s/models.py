"""Kubernetes Pydantic models."""

from typing import Optional
from pydantic import BaseModel


class Pod(BaseModel):
    """Represents a Kubernetes pod."""

    name: str
    namespace: str
    status: str
    node: Optional[str] = None
    restart_count: int


class Deployment(BaseModel):
    """Represents a Kubernetes deployment."""

    name: str
    namespace: str
    desired: int
    ready: int
    available: int
    image: str


class Event(BaseModel):
    """Represents a Kubernetes event."""

    namespace: str
    name: str
    reason: str
    message: str
    count: int
    first_time: Optional[str] = None
    last_time: Optional[str] = None
