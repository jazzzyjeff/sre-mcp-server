"""Azure DevOps Pydantic models."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Project(BaseModel):
    """Represents a Azure DevOps project."""

    id: str
    name: str
    state: str


class WorkItem(BaseModel):
    """Represents a Azure DevOps workitem."""

    id: int
    title: str
    state: str
    assigned_to: Optional[str] = None
    url: str


class Pipeline(BaseModel):
    """Represents a Azure DevOps pipeline."""

    id: int
    name: str
    path: str


class Build(BaseModel):
    """Represents a Azure DevOps build."""

    id: int
    pipeline: str
    status: str
    result: Optional[str] = None
    requested_by: str
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None


class FailedStep(BaseModel):
    """Represents a Azure DevOps failed step."""

    id: str
    name: str
    type: str
    log_id: Optional[int] = None


class Repository(BaseModel):
    """Represents a Azure DevOps repository."""

    id: str
    name: str
    default_branch: Optional[str] = None


class Environment(BaseModel):
    """Represents a Azure DevOps environment."""

    id: int
    name: str


class Deployment(BaseModel):
    """Represents a Azure DevOps deployment."""

    pipeline: str
    run_id: int
    run_name: str
    result: Optional[str]
