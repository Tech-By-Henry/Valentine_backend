import logging
from typing import Iterable, List, Optional, Union

import resend
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

def _normalize_recipients(to: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(to, str):
        return [to]
    return list(to)

def _ensure_resend_configured():
    api_key = getattr(settings, "RESEND_API_KEY", None)
    from_addr = getattr(settings, "RESEND_EMAIL_FROM", None)
    if not api_key:
        raise ImproperlyConfigured("RESEND_API_KEY environment variable is required.")
    if not from_addr:
        raise ImproperlyConfigured("RESEND_EMAIL_FROM environment variable is required.")
    resend.api_key = api_key
    return from_addr

def send_email(
    to: Union[str, Iterable[str]],
    subject: str,
    html: Optional[str] = None,
    text: Optional[str] = None,
    from_email: Optional[str] = None,
) -> dict:
    if not html and not text:
        raise ValueError("Either html or text must be provided to send_email.")

    from_addr = from_email or _ensure_resend_configured()
    recipients = _normalize_recipients(to)

    payload = {"from": from_addr, "to": recipients, "subject": subject}
    if html: payload["html"] = html
    if text: payload["text"] = text

    logger.debug("Resend: sending email %s -> %s (subject=%s)", from_addr, recipients, subject)
    try:
        response = resend.Emails.send(payload)
        msg_id = response.get("id") if isinstance(response, dict) else None
        logger.info("Resend: queued/sent (subject=%s to=%s). response_id=%s", subject, recipients, msg_id)
        return response
    except Exception as exc:
        logger.exception("Failed to send email via Resend: %s", exc)
        raise
