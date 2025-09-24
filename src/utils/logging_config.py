"""Structured logging setup."""
from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    if logging.getLogger().handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(extra)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logging.basicConfig(level=level, handlers=[handler])

    # Inject extra dict if missing
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):  # type: ignore[override]
        record = old_factory(*args, **kwargs)
        if not hasattr(record, "extra"):
            record.extra = {}
        return record

    logging.setLogRecordFactory(record_factory)
