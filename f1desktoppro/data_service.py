"""Data service wrapper around FastF1."""

from __future__ import annotations

import fastf1


class F1DataService:
    """Lightweight facade for FastF1 calls."""

    def get_event_schedule(self, year: int):
        """Return the event schedule for a given year."""
        return fastf1.get_event_schedule(year)

    def get_session(self, year: int, event_name: str, session_code: str):
        """Return a FastF1 session instance."""
        return fastf1.get_session(year, event_name, session_code)
