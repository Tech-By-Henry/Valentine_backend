# valentines/views.py
import os
import logging

from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Valentine
from .serializers import ValentineCreateSerializer, ValentineSerializer
from .services.email_service import send_email

logger = logging.getLogger(__name__)


class CreateValentineAPIView(APIView):
    """
    POST /valentine/
    Expects JSON:
    {
      "sender_name": "...",
      "recipient_name": "...",
      "recipient_email": "..."
    }
    """
    def post(self, request):
        serializer = ValentineCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valentine = serializer.save()

        # frontend URL used in the email link — set this in .env if needed
        frontend_base = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip('/')
        link = f"{frontend_base}/valentine/{valentine.id}"

        subject = f"💌 A message from {valentine.sender_name}"
        # prefer HTML if you want prettier emails — fall back to plain text
        html = (
            f"<p>Hi {valentine.recipient_name},</p>"
            f"<p><strong>{valentine.sender_name}</strong> sent you a message.</p>"
            f"<p>Open this link to view it:<br><a href=\"{link}\">{link}</a></p>"
            f"<p>If you didn't expect this, ignore this email.</p>"
        )

        text = (
            f"Hi {valentine.recipient_name},\n\n"
            f"{valentine.sender_name} sent you a message.\n\n"
            f"Open this link to view it:\n\n{link}\n\n"
            "If you didn't expect this, ignore it."
        )

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

        try:
            # call centralized Resend wrapper
            send_email(
                to=valentine.recipient_email,
                subject=subject,
                html=html,
                text=text,
                from_email=from_email,
            )
        except Exception as exc:
            logger.exception("Error sending valentine email for id=%s: %s", valentine.id, exc)
            # If you prefer not to fail the whole creation when email fails, you can
            # return 201 with link_sent=False. For now we return 201 with link_sent False and log.
            return Response({"id": str(valentine.id), "link_sent": False, "error": "Failed to send email"}, status=status.HTTP_201_CREATED)

        return Response({"id": str(valentine.id), "link_sent": True}, status=status.HTTP_201_CREATED)


class ValentineDetailAPIView(APIView):
    """
    GET /valentine/<uuid:id>/
    """
    def get(self, request, id):
        valentine = get_object_or_404(Valentine, id=id)
        serializer = ValentineSerializer(valentine)
        return Response(serializer.data)
