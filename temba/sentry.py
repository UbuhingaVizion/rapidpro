"""Sentry/GlitchTip error reporting.

Configured from the environment, so a deployment without a DSN simply does not
report. Only errors are sent: tracing and log forwarding stay off. Request
bodies, contact identifiers and phone numbers are removed before an event
leaves the process.
"""

import hashlib
import os
import re
import threading
import time

_PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")

_SENSITIVE_HEADERS = {"authorization", "cookie", "x-hub-signature-256", "tiktok-signature"}
_SENSITIVE_KEYS = {
    "body",
    "contact",
    "contact_uuid",
    "from",
    "message",
    "payload",
    "phone",
    "phone_number",
    "text",
    "to",
    "urn",
    "urns",
    "wa_id",
}

_DEDUPE_WINDOW = 300
_seen = {}
_lock = threading.Lock()
_initialised = False


def _scrub(value):
    if not isinstance(value, str):
        return value
    return _PHONE_RE.sub("[phone]", value)


def _deduplicate(event):
    exception = (event.get("exception", {}).get("values") or [{}])[-1]
    signature = "|".join(
        [
            str(event.get("fingerprint") or ""),
            str(exception.get("type")),
            str(exception.get("value"))[:160],
            str(event.get("message"))[:160],
        ]
    )
    key = hashlib.sha256(signature.encode()).hexdigest()
    now = time.monotonic()

    with _lock:
        for existing, seen_at in list(_seen.items()):
            if now - seen_at > _DEDUPE_WINDOW:
                del _seen[existing]

        if key in _seen:
            return None

        _seen[key] = now

    return event


def before_send(event, hint):
    request = event.get("request") or {}
    for field in ("data", "cookies", "query_string"):
        request.pop(field, None)

    headers = request.get("headers")
    if headers:
        for header in list(headers):
            if header.lower() in _SENSITIVE_HEADERS:
                headers.pop(header, None)

    extra = event.get("extra")
    if extra:
        for key in list(extra):
            if key.lower() in _SENSITIVE_KEYS:
                extra.pop(key)
            else:
                extra[key] = _scrub(extra[key])

    for value in event.get("exception", {}).get("values", []):
        if value.get("value"):
            value["value"] = _scrub(value["value"])

    if event.get("message"):
        event["message"] = _scrub(event["message"])

    return _deduplicate(event)


def init_sentry():
    """Initialise reporting. Returns False when no DSN is configured."""
    global _initialised

    if _initialised:
        return True

    dsn = os.environ.get("RAPIDPRO_SENTRY_DSN") or os.environ.get("SENTRY_DSN")
    if not dsn:
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
    except ImportError:
        # the image may still be on a tag without sentry-sdk; a configured DSN must not break startup
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("SENTRY_ENVIRONMENT") or None,
        release=os.environ.get("SENTRY_RELEASE") or None,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
            # handled errors are captured explicitly, so logging should only add breadcrumbs
            LoggingIntegration(event_level=None),
        ],
        send_default_pii=False,
        auto_session_tracking=False,
        traces_sample_rate=0.0,
        attach_stacktrace=True,
        before_send=before_send,
        ignore_errors=[
            "django.http.response.Http404",
            "django.core.exceptions.DisallowedHost",
            "django.core.exceptions.PermissionDenied",
            "django.core.exceptions.SuspiciousOperation",
        ],
    )
    sentry_sdk.set_tag("service", "rapidpro")

    _initialised = True
    return True


def capture_exception(exc):
    """Report a handled exception. No-op when reporting isn't configured."""
    try:
        import sentry_sdk

        sentry_sdk.capture_exception(exc)
    except Exception:  # pragma: no cover - reporting must never break the caller
        pass
