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

# valentines/views.py (excerpt)
import os
import logging
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Valentine
from .serializers import ValentineCreateSerializer, ValentineSerializer

logger = logging.getLogger(__name__)


class CreateValentineAPIView(APIView):
    """
    POST /valentine/
    Expects JSON:
    {
      "sender_name": "...",
      "recipient_name": "..."
    }

    Returns:
    {
      "id": "...",
      "link": "https://.../valentine/<id>",
      "share_text": "Short loving message with the link"
    }
    """
    def post(self, request):
        serializer = ValentineCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valentine = serializer.save()

        frontend_base = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip('/')
        link = f"{frontend_base}/valentine/{valentine.id}"

        # Short, friendly share text (keeps it compact and copy-ready)
        share_text = (
            f"Hey {valentine.recipient_name},\n\n"
            f"{valentine.sender_name} sent you a little message 💌\n\n"
            f"Open it here: {link}\n\n"
            "— Sent with a small smile"
        )

        return Response(
            {"id": str(valentine.id), "link": link, "share_text": share_text},
            status=status.HTTP_201_CREATED,
        )


class ValentineDetailAPIView(APIView):
    def get(self, request, id):
        valentine = get_object_or_404(Valentine, id=id)
        serializer = ValentineSerializer(valentine)
        return Response(serializer.data)



class ValentineDetailAPIView(APIView):
    """
    GET /valentine/<uuid:id>/
    """
    def get(self, request, id):
        valentine = get_object_or_404(Valentine, id=id)
        serializer = ValentineSerializer(valentine)
        return Response(serializer.data)

from django.http import HttpResponse

def ping(request):
    return HttpResponse("ok", content_type="text/plain")


