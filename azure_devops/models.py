from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Project(BaseModel):
    id: str
    name: str
    state: str


class WorkItem(BaseModel):
    id: int
    title: str
    state: str
    assigned_to: Optional[str] = None
    url: str


class Pipeline(BaseModel):
    id: int
    name: str
    path: str


class Build(BaseModel):
    id: int
    pipeline: str
    status: str
    result: Optional[str] = None
    requested_by: str
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None


class FailedStep(BaseModel):
    id: str
    name: str
    type: str
    log_id: Optional[int] = None


class Repository(BaseModel):
    id: str
    name: str
    default_branch: Optional[str] = None


class Environment(BaseModel):
    id: int
    name: str


class Deployment(BaseModel):
    pipeline: str
    run_id: int
    run_name: str
    result: Optional[str]
