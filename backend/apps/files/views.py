from apps.common.permissions import RoleBasedPermission
from apps.common.viewsets import AuditedModelViewSet
from apps.files.models import InspectionFile
from apps.files.serializers import InspectionFileSerializer


class InspectionFileViewSet(AuditedModelViewSet):
    queryset = InspectionFile.objects.select_related(
        "uploaded_by",
        "building_object",
        "project",
        "structural_element",
        "defect",
        "measurement",
        "report",
    ).all()
    serializer_class = InspectionFileSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Manager", "Engineer"}
    filterset_fields = ("category", "project", "defect", "structural_element", "is_for_report", "appendix_type")
    search_fields = ("original_name", "caption")
