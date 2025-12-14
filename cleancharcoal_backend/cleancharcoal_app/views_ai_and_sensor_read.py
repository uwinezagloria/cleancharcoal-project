from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import Sensor, SensorData, AIInsight
from .serializers_sensor import SensorReadSerializer, SensorDataReadSerializer
from .serializers_ai import AIInsightReadSerializer


def require_any_role(request, roles):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required."}, status=401)
    if not hasattr(request.user, "profile"):
        return Response({"error": "Profile missing."}, status=400)
    if request.user.profile.role not in roles:
        return Response({"error": f"Only {roles} allowed."}, status=403)
    return None


class KilnSensorsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, kiln_id):
        err = require_any_role(request, ["burner", "leader", "admin"])
        if err: return err

        # burner can see only own kiln
        if request.user.profile.role == "burner":
            qs = Sensor.objects.filter(kiln_id=kiln_id, kiln__owner=request.user)
        else:
            qs = Sensor.objects.filter(kiln_id=kiln_id)

        return Response(SensorReadSerializer(qs, many=True).data, status=200)


class KilnSensorReadingsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, kiln_id):
        err = require_any_role(request, ["burner", "leader", "admin"])
        if err: return err

        if request.user.profile.role == "burner":
            qs = SensorData.objects.filter(sensor__kiln_id=kiln_id, sensor__kiln__owner=request.user).order_by("-id")[:200]
        else:
            qs = SensorData.objects.filter(sensor__kiln_id=kiln_id).order_by("-id")[:200]

        return Response(SensorDataReadSerializer(qs, many=True).data, status=200)


class KilnAIInsightsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, kiln_id):
        err = require_any_role(request, ["burner", "leader", "admin"])
        if err: return err

        if request.user.profile.role == "burner":
            qs = AIInsight.objects.filter(kiln_id=kiln_id, kiln__owner=request.user).order_by("-id")[:200]
        else:
            qs = AIInsight.objects.filter(kiln_id=kiln_id).order_by("-id")[:200]

        return Response(AIInsightReadSerializer(qs, many=True).data, status=200)
