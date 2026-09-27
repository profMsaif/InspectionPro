from apps.common.permissions import RoleBasedPermission
from apps.common.viewsets import AuditedModelViewSet
from apps.elements.models import StructuralElement
from apps.elements.serializers import StructuralElementSerializer


class StructuralElementViewSet(AuditedModelViewSet):
    queryset = StructuralElement.objects.select_related(
        "project",
        "building_object",
        "element_type_dictionary",
        "material_dictionary",
        "inspection_method_dictionary",
        "condition_category_dictionary",
        "inspection_status_dictionary",
        "recommendation_dictionary",
    ).all()
    serializer_class = StructuralElementSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Manager", "Engineer"}
    filterset_fields = ("project", "building_object", "element_type", "condition_category", "floor", "has_defects")
    search_fields = ("name", "location", "axes", "material")
