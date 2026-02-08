# valentines/services/email_service.py
import logging
from typing import Iterable, List, Optional, Union

import resend
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# Ensure API key is configured
RESEND_API_KEY = getattr(settings, "RESEND_API_KEY", None)
if not RESEND_API_KEY:
    raise ImproperlyConfigured("RESEND_API_KEY environment variable is required to send emails via Resend.")

# configure the sdk
resend.api_key = RESEND_API_KEY


def _normalize_recipients(to: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(to, str):
        return [to]
    return list(to)


def send_email(
    to: Union[str, Iterable[str]],
    subject: str,
    html: Optional[str] = None,
    text: Optional[str] = None,
    from_email: Optional[str] = None,
) -> dict:
    """
    Send an email through Resend.

    Args:
        to: single address or iterable of addresses
        subject: subject line
        html: HTML body (preferred)
        text: plain-text body (fallback)
        from_email: optional override for sender (falls back to DEFAULT_FROM_EMAIL)

    Returns:
        The response from resend.Emails.send (dict-like)
    Raises:
        Exception for network / API errors (bubbles up)
    """
    if not html and not text:
        raise ValueError("Either html or text must be provided to send_email.")

    recipients = _normalize_recipients(to)
    from_addr = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if not from_addr:
        raise ImproperlyConfigured("DEFAULT_FROM_EMAIL must be set in settings or pass from_email explicitly.")

    payload = {
        "from": from_addr,
        "to": recipients,
        "subject": subject,
    }

    if html:
        payload["html"] = html
    if text:
        payload["text"] = text

    logger.debug("Sending email via Resend: %s -> %s (subject=%s)", from_addr, recipients, subject)

    # resend.Emails.send returns a dict-like response
    try:
        response = resend.Emails.send(payload)
        logger.info("Resend: email queued/sent (subject=%s to=%s). response_id=%s", subject, recipients, response.get("id"))
        return response
    except Exception as exc:
        # Log and re-raise so calling code can handle/report as needed
        logger.exception("Failed to send email via Resend (subject=%s to=%s): %s", subject, recipients, exc)
        raise
