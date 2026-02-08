# valentines/admin.py
from django.contrib import admin
from .models import Valentine

@admin.register(Valentine)
class ValentineAdmin(admin.ModelAdmin):
    list_display = ("id", "sender_name", "recipient_name", "recipient_email", "created_at")
    search_fields = ("sender_name", "recipient_name", "recipient_email")
    ordering = ("-created_at",)
