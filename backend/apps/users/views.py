from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.common.audit import build_model_snapshot, log_audit_event
from apps.common.permissions import IsActiveUnblocked, RoleBasedPermission
from apps.common.viewsets import AuditedModelViewSet
from apps.users.models import User
from apps.users.serializers import AuthUserSerializer, InspectionTokenObtainPairSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    serializer_class = InspectionTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        log_audit_event(
                user=user,
                action="logged_in",
                instance=user,
                new_value=build_model_snapshot(user),
            )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AuthMeView(APIView):
    permission_classes = [IsActiveUnblocked]

    def get(self, request):
        return Response(AuthUserSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [IsActiveUnblocked]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        log_audit_event(
            user=request.user,
            action="logged_out",
            instance=request.user,
            new_value=build_model_snapshot(request.user),
        )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class UserViewSet(AuditedModelViewSet):
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin"}
    write_roles = {"Admin"}
    filterset_fields = ("role", "is_active", "is_blocked")
    search_fields = ("email", "full_name", "organization")
