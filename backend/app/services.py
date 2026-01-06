from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import fastf1

from .schemas import Event, SessionResult, SessionSummary, StandingPayload, StandingEntry
from .timezone import localize_sessions, to_local_time


def enable_fastf1_cache(cache_dir: str) -> None:
    """Enable FastF1 on-disk cache."""
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)


def _mock_event(event_id: str, offset_days: int = 0) -> Event:
    now = datetime.now(timezone.utc) + timedelta(days=offset_days)
    sessions = [
        SessionSummary(
            id=f"{event_id}-fp1",
            name="Free Practice 1",
            type="fp1",
            start=now + timedelta(hours=2),
            end=now + timedelta(hours=3, minutes=30),
        ),
        SessionSummary(
            id=f"{event_id}-qualifying",
            name="Qualifying",
            type="qualifying",
            start=now + timedelta(days=1),
            end=now + timedelta(days=1, hours=1, minutes=30),
        ),
        SessionSummary(
            id=f"{event_id}-race",
            name="Race",
            type="race",
            start=now + timedelta(days=2),
            end=now + timedelta(days=2, hours=2),
        ),
    ]
    event = Event(
        id=event_id,
        season=2024,
        name="Grand Prix",
        circuit="Sample Circuit",
        country="Exampleland",
        timezone="Europe/Paris",
        start=now,
        end=now + timedelta(days=3),
        sessions=sessions,
    )
    enriched_sessions: List[SessionSummary] = []
    for base_session in event.sessions:
        enriched_sessions.append(
            SessionSummary(
                **base_session.model_dump(exclude={"local_start", "local_end"}),
                local_start=to_local_time(base_session.start, event.timezone),
                local_end=to_local_time(base_session.end, event.timezone),
            )
        )
    event.sessions = enriched_sessions
    return event


def get_calendar(status: str = "all") -> List[Event]:
    """Return a normalized calendar. Uses mock data for scaffolding."""
    events = [
        _mock_event("round-1", offset_days=7),
        _mock_event("round-2", offset_days=21),
        _mock_event("round-0", offset_days=-14),
    ]

    if status == "upcoming":
        return [event for event in events if event.start > datetime.now(timezone.utc)]
    if status == "completed":
        return [event for event in events if event.end < datetime.now(timezone.utc)]
    return events


def get_event(event_id: str) -> Event:
    for event in get_calendar():
        if event.id == event_id:
            return event
    return _mock_event(event_id)


def get_session_results(session_id: str) -> Dict[str, List[SessionResult]]:
    base = [
        SessionResult(position=1, driver="DRV1", team="TEAM1", time="1:30.000"),
        SessionResult(position=2, driver="DRV2", team="TEAM2", time="1:30.500"),
    ]
    return {
        "classification": base,
        "stints": base,
        "tyres": base,
        "pitstops": base,
    }


def get_standings(kind: str) -> StandingPayload:
    entries = [
        StandingEntry(position=1, name="Driver One", team="Team A", points=102.0),
        StandingEntry(position=2, name="Driver Two", team="Team B", points=94.0),
    ]
    return StandingPayload(round=6, last_updated=datetime.now(timezone.utc), entries=entries)


def get_profile(entity_id: str, kind: str = "driver") -> Dict:
    profile = {
        "id": entity_id,
        "name": f"{kind.title()} {entity_id}",
        "team": "Team A",
        "nationality": "N/A",
        "stats": {"starts": 10, "wins": 2},
        "recent_results": [
            SessionResult(position=3, driver="DRV3", team="TEAM3", time="1:32.000").model_dump()
        ],
    }
    return profile


def get_telemetry(session_id: str, drivers: List[str]) -> Dict:
    now = datetime.now(timezone.utc)
    return {
        "session_id": session_id,
        "drivers": drivers,
        "points": [
            {"timestamp": now.isoformat(), "speed": 320, "delta": 0.0},
            {"timestamp": (now + timedelta(seconds=30)).isoformat(), "speed": 315, "delta": 0.2},
        ],
    }
