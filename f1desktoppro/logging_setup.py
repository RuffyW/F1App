"""Basic logging configuration for the application."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(app_data_dir: Path) -> logging.Logger:
    """Configure a rotating file logger."""
    logs_dir = app_data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("f1desktoppro")
