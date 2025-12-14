from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import Notification
from .serializers_notifications import NotificationReadSerializer, NotificationMarkReadSerializer


class MyNotificationsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user).order_by("-id")[:200]
        return Response(NotificationReadSerializer(qs, many=True).data, status=200)


class NotificationMarkReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, notif_id):
        try:
            n = Notification.objects.get(id=notif_id, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found."}, status=404)

        s = NotificationMarkReadSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        n.is_read = s.validated_data["is_read"]
        n.save(update_fields=["is_read"])
        return Response({"message": "Updated."}, status=200)
