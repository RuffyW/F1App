from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SessionSummary(BaseModel):
    id: str
    name: str
    type: str
    status: str = Field(default="scheduled")
    start: datetime
    end: datetime
    local_start: Optional[str] = None
    local_end: Optional[str] = None


class Event(BaseModel):
    id: str
    season: int
    name: str
    circuit: str
    country: str
    start: datetime
    end: datetime
    timezone: str
    sessions: List[SessionSummary] = Field(default_factory=list)


class SessionResult(BaseModel):
    position: int
    driver: str
    team: str
    time: Optional[str] = None
    tyre: Optional[str] = None


class StandingEntry(BaseModel):
    position: int
    name: str
    team: Optional[str] = None
    points: float


class StandingPayload(BaseModel):
    round: int
    last_updated: datetime
    entries: List[StandingEntry]


class ProfilePayload(BaseModel):
    id: str
    name: str
    team: Optional[str] = None
    nationality: Optional[str] = None
    stats: dict
    recent_results: List[SessionResult] = Field(default_factory=list)
