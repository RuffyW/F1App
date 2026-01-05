"""Simple licensing helpers for local execution."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Tuple


TRIAL_LENGTH_DAYS = 7


def is_valid_key(key: Optional[str]) -> bool:
    """Validate a license key. Current implementation accepts non-empty keys."""
    return bool(key and key.strip())


def trial_status(trial_start: Optional[str]) -> Tuple[bool, int]:
    """Return whether the trial is valid and remaining days."""
    if not trial_start:
        return True, TRIAL_LENGTH_DAYS

    try:
        started = datetime.fromisoformat(trial_start)
    except ValueError:
        return True, TRIAL_LENGTH_DAYS

    remaining = TRIAL_LENGTH_DAYS - (datetime.utcnow() - started).days
    return remaining > 0, max(0, remaining)
