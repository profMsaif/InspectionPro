from apps.common.permissions import RoleBasedPermission
from apps.common.viewsets import AuditedModelViewSet
from apps.measurements.models import Measurement
from apps.measurements.serializers import MeasurementSerializer


class MeasurementViewSet(AuditedModelViewSet):
    queryset = Measurement.objects.select_related(
        "project",
        "structural_element",
        "defect",
        "engineer",
        "measurement_type_dictionary",
        "unit_dictionary",
        "device_dictionary",
        "method_dictionary",
    ).all()
    serializer_class = MeasurementSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Manager", "Engineer"}
    filterset_fields = ("project", "structural_element", "defect", "measurement_type", "unit", "engineer")
    search_fields = ("measurement_type", "device", "method", "location")
