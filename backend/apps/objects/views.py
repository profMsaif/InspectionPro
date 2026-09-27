from apps.common.permissions import RoleBasedPermission
from apps.common.viewsets import AuditedModelViewSet
from apps.objects.models import BuildingObject
from apps.objects.serializers import BuildingObjectSerializer


class BuildingObjectViewSet(AuditedModelViewSet):
    queryset = BuildingObject.objects.select_related(
        "created_by",
        "object_type_dictionary",
        "structural_system_dictionary",
        "main_material_dictionary",
    ).all()
    serializer_class = BuildingObjectSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Manager"}
    filterset_fields = ("object_type", "construction_year")
    search_fields = ("name", "address", "cadastral_number")
