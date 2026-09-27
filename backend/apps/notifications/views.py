from rest_framework import mixins, viewsets

from apps.common.permissions import RoleBasedPermission
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = {"Admin", "Manager", "Engineer", "Expert", "Client"}
    filterset_fields = ("is_read",)
    search_fields = ("title", "message")

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

