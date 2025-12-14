from rest_framework import serializers
from .models import AIInsight


class AIInsightReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = "__all__"
        read_only_fields = fields
