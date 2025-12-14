from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import PermissionRequest, Kiln, Notification
from .views_admin import require_admin


class AdminProvisionKilnAfterApprovalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, permission_id):
        err = require_admin(request)
        if err: return err

        try:
            perm = PermissionRequest.objects.select_related("burner", "kiln").get(id=permission_id)
        except PermissionRequest.DoesNotExist:
            return Response({"error": "Permission request not found."}, status=404)

        if perm.status != "approved":
            return Response({"error": "Permission must be approved before provisioning kiln monitoring."}, status=400)

        # Ensure kiln is linked and approved_for_burning
        kiln = perm.kiln
        kiln.approved_for_burning = True
        kiln.approved_permission = perm
        kiln.save(update_fields=["approved_for_burning", "approved_permission"])

        Notification.objects.create(
            recipient=perm.burner,
            notif_type="permission",
            title="Kiln approved for burning",
            message="Your kiln is now approved_for_burning and monitoring will start.",
            kiln=kiln,
            permission=perm,
        )

        return Response(
            {"message": "Kiln provisioned. Now assign sensors to this kiln.", "kiln_id": kiln.id},
            status=200
        )
