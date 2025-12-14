from rest_framework import serializers
from .models import Notification


class NotificationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = fields


class NotificationMarkReadSerializer(serializers.Serializer):
    is_read = serializers.BooleanField()
