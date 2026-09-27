from rest_framework import mixins, viewsets

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.common.permissions import RoleBasedPermission


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = {"Admin", "Manager", "Expert"}
    filterset_fields = ("entity_type", "action", "user")
    search_fields = ("entity_id", "action")

