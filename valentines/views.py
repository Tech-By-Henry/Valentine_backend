# valentines/views.py
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os


from .models import Valentine
from .serializers import ValentineCreateSerializer, ValentineSerializer

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
        message = (
            f"Hi {valentine.recipient_name},\n\n"
            f"{valentine.sender_name} sent you a message.\n\n"
            f"Open this link to view it:\n\n{link}\n\n"
            "If you didn't expect this, ignore it."
        )
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER or None)

        # send email (will raise if smtp misconfigured)
        send_mail(subject, message, from_email, [valentine.recipient_email], fail_silently=False)

        return Response({"id": str(valentine.id), "link_sent": True}, status=status.HTTP_201_CREATED)


class ValentineDetailAPIView(APIView):
    """
    GET /valentine/<uuid:id>/
    """
    def get(self, request, id):
        valentine = get_object_or_404(Valentine, id=id)
        serializer = ValentineSerializer(valentine)
        return Response(serializer.data)
