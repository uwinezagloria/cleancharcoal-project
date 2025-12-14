from rest_framework import serializers
from .models import Sensor, SensorData


class SensorReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ["id", "kiln", "sensor_type", "serial_number", "is_active", "installed_at"]
        read_only_fields = fields


class SensorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ["id", "kiln", "sensor_type", "serial_number", "is_active"]
        read_only_fields = ["id"]

    def validate_serial_number(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("serial_number is required.")
        return v


class SensorDataIngestSerializer(serializers.Serializer):
    serial_number = serializers.CharField()
    api_key = serializers.CharField()
    value = serializers.FloatField()
    unit = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        sn = attrs["serial_number"].strip()
        key = attrs["api_key"].strip()
        try:
            sensor = Sensor.objects.select_related("kiln").get(serial_number=sn, api_key=key, is_active=True)
        except Sensor.DoesNotExist:
            raise serializers.ValidationError("Invalid sensor credentials or sensor inactive.")

        # climate gate: only accept readings if kiln approved
        if not sensor.kiln.approved_for_burning:
            raise serializers.ValidationError("Kiln not approved_for_burning. Readings blocked by policy.")

        attrs["sensor"] = sensor
        return attrs


class SensorDataReadSerializer(serializers.ModelSerializer):
    sensor_type = serializers.CharField(source="sensor.sensor_type", read_only=True)
    serial_number = serializers.CharField(source="sensor.serial_number", read_only=True)

    class Meta:
        model = SensorData
        fields = ["id", "sensor", "serial_number", "sensor_type", "value", "unit", "recorded_at"]
        read_only_fields = fields
