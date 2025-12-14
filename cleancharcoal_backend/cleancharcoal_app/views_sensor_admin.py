import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import Sensor, Kiln, Profile
from .serializers_sensor import SensorReadSerializer, SensorCreateSerializer


def require_admin(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required."}, status=401)
    if not hasattr(request.user, "profile"):
        return Response({"error": "Profile missing."}, status=400)
    if request.user.profile.role != "admin":
        return Response({"error": "Only admin can access this endpoint."}, status=403)
    return None


class AdminSensorListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_admin(request)
        if err: return err
        qs = Sensor.objects.select_related("kiln").order_by("-id")
        return Response(SensorReadSerializer(qs, many=True).data, status=200)

    def post(self, request):
        err = require_admin(request)
        if err: return err

        s = SensorCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        sensor = s.save()

        # Return api_key ONCE here (admin sees it and programs device)
        return Response(
            {
                "message": "Sensor created. Save api_key now (you won't show it again in normal reads).",
                "sensor_id": sensor.id,
                "serial_number": sensor.serial_number,
                "api_key": sensor.api_key,
            },
            status=201
        )


class AdminSensorRotateKeyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, sensor_id):
        err = require_admin(request)
        if err: return err

        try:
            sensor = Sensor.objects.get(id=sensor_id)
        except Sensor.DoesNotExist:
            return Response({"error": "Sensor not found."}, status=404)

        sensor.api_key = secrets.token_hex(32)
        sensor.save(update_fields=["api_key"])
        return Response(
            {"message": "API key rotated. Update embedded device.", "api_key": sensor.api_key},
            status=200
        )
