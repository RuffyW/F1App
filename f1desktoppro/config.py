"""Configuration helpers for F1 Desktop Pro."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """Holds basic application settings."""

    license_key: str = ""
    trial_start: Optional[str] = None
    cache_dir: Optional[str] = None
    last_year: Optional[int] = None
    last_event: Optional[str] = None
    last_session: Optional[str] = None
    theme: str = "dark"


def get_app_data_dir() -> Path:
    """Return the platform-agnostic app data directory and ensure it exists."""
    base = Path.home() / ".f1desktoppro"
    base.mkdir(parents=True, exist_ok=True)
    return base


def load_config() -> AppConfig:
    """Load configuration from disk or return defaults."""
    config_path = get_app_data_dir() / "config.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return AppConfig(**data)
        except Exception:
            # Fall back to defaults on any parse error
            return AppConfig()
    return AppConfig()


def save_config(config: AppConfig) -> None:
    """Persist configuration to disk."""
    config_path = get_app_data_dir() / "config.json"
    config_path.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
