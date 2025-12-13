from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsAdminProfile
from .models import Profile
from .serializers_leaders import LeaderCreateSerializer, LeaderUpdateSerializer
from .serializers import ProfileReadSerializer


class AdminLeaderListCreateAPIView(APIView):
    permission_classes = [IsAdminProfile]

    def get(self, request):
        leaders = Profile.objects.filter(role="leader").select_related("user").order_by("-id")
        return Response(ProfileReadSerializer(leaders, many=True).data, status=200)

    def post(self, request):
        s = LeaderCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        email = data["email"].strip().lower()

        if User.objects.filter(username=email).exists():
            return Response({"error": "Leader with this email already exists."}, status=400)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        Profile.objects.create(
            user=user,
            role="leader",
            phone="000000000",
            country="Rwanda",
            province="Unknown",
            district="Unknown",
            sector="Unknown",
            leader_district=data["leader_district"],
            leader_sector=data["leader_sector"],
            otp_verified=True,  # leader is trusted; no OTP flow
        )

        return Response({"message": "Leader created."}, status=201)


class AdminLeaderDetailAPIView(APIView):
    permission_classes = [IsAdminProfile]

    def patch(self, request, leader_user_id):
        s = LeaderUpdateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        try:
            user = User.objects.get(id=leader_user_id)
        except User.DoesNotExist:
            return Response({"error": "Leader not found."}, status=404)

        if not hasattr(user, "profile") or user.profile.role != "leader":
            return Response({"error": "This user is not a leader."}, status=400)

        # update User fields
        if "first_name" in data: user.first_name = data["first_name"]
        if "last_name" in data: user.last_name = data["last_name"]
        if "password" in data: user.set_password(data["password"])
        user.save()

        # update jurisdiction
        p = user.profile
        if "leader_district" in data: p.leader_district = data["leader_district"]
        if "leader_sector" in data: p.leader_sector = data["leader_sector"]
        p.save()

        return Response({"message": "Leader updated."}, status=200)

    def delete(self, request, leader_user_id):
        try:
            user = User.objects.get(id=leader_user_id)
        except User.DoesNotExist:
            return Response({"error": "Leader not found."}, status=404)

        if not hasattr(user, "profile") or user.profile.role != "leader":
            return Response({"error": "This user is not a leader."}, status=400)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
