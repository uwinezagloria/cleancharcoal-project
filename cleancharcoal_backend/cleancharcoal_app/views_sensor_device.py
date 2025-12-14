from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SensorData
from .serializers_sensor import SensorDataIngestSerializer


class SensorDataIngestAPIView(APIView):
    """
    Embedded device sends:
    { serial_number, api_key, value, unit? }
    """
    authentication_classes = []  # device auth handled by serializer (api_key)
    permission_classes = []

    def post(self, request):
        s = SensorDataIngestSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        sensor = s.validated_data["sensor"]
        value = s.validated_data["value"]
        unit = s.validated_data.get("unit") or None

        reading = SensorData.objects.create(sensor=sensor, value=value, unit=unit)

        # ✅ RULE-BASED "AI" NOW (you can replace later with ML)
        # Example thresholds (edit them)
        alerts = []
        if sensor.sensor_type in ["smoke", "pm25"] and value > 150:
            alerts.append(("critical", f"High {sensor.sensor_type} detected: {value}"))
        if sensor.sensor_type == "co2" and value > 1500:
            alerts.append(("warning", f"High CO2 detected: {value}"))

        # If alerts exist, create AIInsight + notifications (optional)
        if alerts:
            from .models import AIInsight, Notification, PermissionRequest

            perm = sensor.kiln.approved_permission  # optional link
            for severity, msg in alerts:
                insight = AIInsight.objects.create(
                    kiln=sensor.kiln,
                    permission=perm,
                    created_by="system",
                    title="Emission threshold exceeded",
                    message=msg,
                    severity=severity,
                    data={"sensor_type": sensor.sensor_type, "value": value, "unit": unit},
                )

                # notify burner
                Notification.objects.create(
                    recipient=sensor.kiln.owner,
                    notif_type="insight",
                    title="Kiln emission alert",
                    message=msg,
                    kiln=sensor.kiln,
                    permission=perm,
                    insight=insight,
                )

                # notify leader if exists on permission
                if perm and perm.leader:
                    Notification.objects.create(
                        recipient=perm.leader,
                        notif_type="insight",
                        title="Kiln emission alert (leader)",
                        message=msg,
                        kiln=sensor.kiln,
                        permission=perm,
                        insight=insight,
                    )

        return Response({"message": "Reading saved.", "reading_id": reading.id}, status=201)
