from apps.common.permissions import RoleBasedPermission
from apps.common.viewsets import AuditedModelViewSet
from apps.defects.models import Defect
from apps.defects.serializers import DefectSerializer


class DefectViewSet(AuditedModelViewSet):
    queryset = Defect.objects.select_related(
        "project",
        "building_object",
        "structural_element",
        "created_by",
        "defect_type_dictionary",
        "severity_dictionary",
        "probable_cause_dictionary",
        "preliminary_condition_category_dictionary",
        "final_condition_category_dictionary",
        "recommendation_dictionary",
    ).all()
    serializer_class = DefectSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Manager", "Engineer"}
    filterset_fields = (
        "project",
        "building_object",
        "structural_element",
        "defect_type",
        "floor",
        "status",
        "final_condition_category",
    )
    search_fields = ("title", "description", "location", "room")
