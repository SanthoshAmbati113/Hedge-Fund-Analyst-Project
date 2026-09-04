"""Central Logfire configuration for the hedge fund analyst application."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import logfire

_configured = False


def is_logfire_enabled() -> bool:
    """Return True when telemetry should be emitted."""
    value = os.getenv("LOGFIRE_ENABLED", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def _scrub_sensitive_values(match: logfire.ScrubMatch) -> Any:
    """Redact API keys that appear in URLs or attribute values."""
    if isinstance(match.value, str):
        lowered = match.value.lower()
        if "apikey=" in lowered or "api_key=" in lowered:
            return _redact_url_query(match.value)
    return None


def _redact_url_query(url: str) -> str:
    """Remove sensitive query parameters from a URL."""
    parsed = urlparse(url)
    safe_params = [
        (key, "[REDACTED]" if key.lower() in {"apikey", "api_key", "token"} else value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
    ]
    return urlunparse(parsed._replace(query=urlencode(safe_params)))


def _resolve_send_to_logfire() -> bool | str:
    """Map environment configuration to Logfire's send_to_logfire setting."""
    value = os.getenv("LOGFIRE_SEND_TO_LOGFIRE", "if-token-present").strip().lower()

    if value in {"0", "false", "no", "off"}:
        return False
    if value in {"1", "true", "yes", "on", "always"}:
        return True
    if value == "if-token-present":
        return "if-token-present"
    return "if-token-present"


def configure_logfire(*, service_name: str = "hedge-fund-analyst") -> None:
    """Initialize Logfire once for the current process."""
    global _configured

    if _configured or not is_logfire_enabled():
        return

    send_to_logfire = _resolve_send_to_logfire()
    token = os.getenv("LOGFIRE_TOKEN")

    try:
        configure_kwargs: dict[str, Any] = {
            "service_name": service_name,
            "send_to_logfire": send_to_logfire,
            "scrubbing": logfire.ScrubbingOptions(
                callback=_scrub_sensitive_values,
                extra_patterns=[
                    r"api[_-]?key",
                    r"groq[_-]?api[_-]?key",
                    r"alpha[_-]?vantage[_-]?api[_-]?key",
                ],
            ),
        }
        if token:
            configure_kwargs["token"] = token

        logfire.configure(**configure_kwargs)
        _configured = True
        logfire.info(
            "logfire configured",
            service=service_name,
            send_to_logfire=send_to_logfire,
        )
    except Exception as exc:
        # Telemetry must never prevent the application from running.
        print(f"[observability] Logfire setup skipped: {exc}")


def instrument_fastapi_app(app: Any) -> None:
    """Attach FastAPI instrumentation to an application instance."""
    if not is_logfire_enabled():
        return

    configure_logfire()

    try:
        logfire.instrument_fastapi(
            app,
            capture_headers=False,
        )
    except Exception as exc:
        print(f"[observability] FastAPI instrumentation skipped: {exc}")
