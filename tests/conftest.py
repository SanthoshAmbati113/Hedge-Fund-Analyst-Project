"""Pytest bootstrap for observability-safe test runs."""

from __future__ import annotations

import os

# Disable remote export during automated tests unless explicitly overridden.
os.environ.setdefault("LOGFIRE_SEND_TO_LOGFIRE", "false")
os.environ.setdefault("LOGFIRE_ENABLED", "true")

import observability  # noqa: F401, E402
from observability import configure_logfire  # noqa: E402

configure_logfire(service_name="hedge-fund-analyst-tests")
