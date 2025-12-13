from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class LeaderCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    leader_district = serializers.CharField()
    leader_sector = serializers.CharField()

class LeaderUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    leader_district = serializers.CharField(required=False)
    leader_sector = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)  # optional reset
