from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
from zoneinfo import ZoneInfo


def to_local_time(dt: datetime, tz_name: str) -> str:
    """Convert a timezone-aware datetime to a local string representation."""
    zone = ZoneInfo(tz_name)
    source = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return source.astimezone(zone).isoformat()


def localize_sessions(
    sessions: Iterable[dict], tz_name: str, fields: Iterable[str] = ("start", "end")
) -> list[dict]:
    """Return sessions with converted time fields."""
    localized = []
    for session in sessions:
        session_copy = {**session}
        for field in fields:
            if session_copy.get(field):
                session_copy[field] = to_local_time(session_copy[field], tz_name)
        localized.append(session_copy)
    return localized
