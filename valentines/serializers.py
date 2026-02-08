# valentines/serializers.py
from rest_framework import serializers
from .models import Valentine

class ValentineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valentine
        fields = ("sender_name", "recipient_name", "recipient_email")

class ValentineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valentine
        fields = ("id", "sender_name", "recipient_name", "created_at")
