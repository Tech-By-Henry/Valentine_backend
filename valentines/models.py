# valentines/models.py
from django.db import models
import uuid

class Valentine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_name = models.CharField(max_length=120)
    recipient_name = models.CharField(max_length=120)
    recipient_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_name} → {self.recipient_email}"
