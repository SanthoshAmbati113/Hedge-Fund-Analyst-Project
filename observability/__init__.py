"""Logfire observability bootstrap.

Import this module before ``langchain`` / ``langgraph`` so LangSmith OpenTelemetry
tracing is routed to Logfire.
"""

from __future__ import annotations

import os

# LangSmith OTel must be enabled before langchain/langgraph are imported.
os.environ.setdefault("LANGSMITH_OTEL_ENABLED", "true")
os.environ.setdefault("LANGSMITH_OTEL_ONLY", "true")
os.environ.setdefault("LANGSMITH_TRACING", "true")

from observability.setup import (
    configure_logfire,
    instrument_fastapi_app,
    is_logfire_enabled,
)

__all__ = [
    "configure_logfire",
    "instrument_fastapi_app",
    "is_logfire_enabled",
]
