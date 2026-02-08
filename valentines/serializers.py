# valentines/serializers.py
from rest_framework import serializers
from .models import Valentine

# valentines/serializers.py (excerpt)
from rest_framework import serializers
from .models import Valentine

class ValentineCreateSerializer(serializers.ModelSerializer):
    recipient_email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = Valentine
        fields = ("id", "sender_name", "recipient_name", "recipient_email")
        read_only_fields = ("id",)

    def create(self, validated_data):
        # Ensure there's a value for recipient_email if the model requires it
        if "recipient_email" not in validated_data:
            validated_data["recipient_email"] = ""
        return super().create(validated_data)



class ValentineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valentine
        fields = ("id", "sender_name", "recipient_name", "created_at")
