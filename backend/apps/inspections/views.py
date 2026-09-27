import logging

from rest_framework import decorators, response
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError

from apps.common.audit import build_model_snapshot, log_audit_event
from apps.common.permissions import RoleBasedPermission
from apps.common.viewsets import AuditedModelViewSet
from apps.inspections.services import validate_project_readiness
from apps.inspections.models import InspectionProject, TechnicalTask, WorkProgram
from apps.inspections.serializers import InspectionProjectSerializer, TechnicalTaskSerializer, WorkProgramSerializer
from apps.reports.models import Report, ReportTemplate
from apps.reports.serializers import ReportSerializer
from apps.reports.services import (
    PDF_EXPORT_AVAILABLE,
    PDF_EXPORT_UNAVAILABLE_MESSAGE,
    attach_generated_report_file,
    build_passport_data,
    build_report_snapshot,
    build_report_title,
    generate_docx_bytes,
    generate_pdf_bytes,
    get_or_create_working_report,
    update_report_snapshot,
)

logger = logging.getLogger(__name__)


class InspectionProjectViewSet(AuditedModelViewSet):
    queryset = InspectionProject.objects.select_related(
        "building_object",
        "responsible_engineer",
        "created_by",
        "inspection_type_dictionary",
        "final_condition_category_dictionary",
        "report_template",
    ).prefetch_related("team").all()
    serializer_class = InspectionProjectSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Manager"}
    action_roles = {
        "submit_review": {"Admin", "Manager", "Engineer"},
        "approve": {"Admin", "Expert"},
        "archive": {"Admin", "Manager"},
        "return_for_correction": {"Admin", "Expert"},
        "generate_docx": {"Admin", "Manager", "Engineer", "Expert"},
        "generate_pdf": {"Admin", "Manager", "Engineer", "Expert"},
        "generate_report": {"Admin", "Manager", "Engineer", "Expert"},
        "set_report_template": {"Admin", "Manager", "Expert"},
        "reports": {"Admin", "Manager", "Engineer", "Expert", "Client"},
        "passport": {"Admin", "Manager", "Engineer", "Expert", "Client"},
    }
    filterset_fields = ("status", "inspection_type", "responsible_engineer")
    search_fields = ("customer_name", "contract_number", "building_object__name")

    def _generate_project_report(self, project, user, serializer_context, *, file_format: str):
        try:
            if file_format == "pdf" and not PDF_EXPORT_AVAILABLE:
                raise ValidationError({"file_format": PDF_EXPORT_UNAVAILABLE_MESSAGE})
            validate_project_readiness(project)
            report = get_or_create_working_report(project, user, build_report_title(project))
            old_value = build_model_snapshot(report)
            snapshot = build_report_snapshot(project)
            report = update_report_snapshot(report, snapshot=snapshot, generated_by=user)
            content = generate_docx_bytes(snapshot) if file_format == "docx" else generate_pdf_bytes(snapshot)
            report = attach_generated_report_file(report, file_format=file_format, content=content)
            log_audit_event(
                user=user,
                action=f"generated_{file_format}",
                instance=report,
                old_value=old_value,
                new_value=build_model_snapshot(report),
            )
            return response.Response(ReportSerializer(report, context=serializer_context).data)
        except ValidationError:
            raise
        except Exception as exc:
            logger.exception("Report generation failed for project %s in %s format", project.pk, file_format)
            raise APIException("Failed to generate report.") from exc

    @decorators.action(detail=True, methods=["post"])
    def submit_review(self, request, pk=None):
        project = self.get_object()
        validate_project_readiness(project)
        old_value = build_model_snapshot(project)
        project.status = InspectionProject.Status.REVIEW
        project.save(update_fields=["status", "updated_at"])
        log_audit_event(
            user=request.user,
            action="submitted_for_review",
            instance=project,
            old_value=old_value,
            new_value=build_model_snapshot(project),
        )
        return response.Response({"status": project.status})

    @decorators.action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        project = self.get_object()
        if request.user.role not in {"Admin", "Expert"} and not request.user.is_superuser:
            raise PermissionDenied("Only experts can approve inspection projects.")
        old_value = build_model_snapshot(project)
        project.status = InspectionProject.Status.APPROVED
        project.save(update_fields=["status", "updated_at"])
        log_audit_event(
            user=request.user,
            action="approved",
            instance=project,
            old_value=old_value,
            new_value=build_model_snapshot(project),
        )
        return response.Response({"status": project.status})

    @decorators.action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        project = self.get_object()
        old_value = build_model_snapshot(project)
        project.status = InspectionProject.Status.ARCHIVED
        project.save(update_fields=["status", "updated_at"])
        log_audit_event(
            user=request.user,
            action="archived",
            instance=project,
            old_value=old_value,
            new_value=build_model_snapshot(project),
        )
        return response.Response({"status": project.status})

    @decorators.action(detail=True, methods=["post"])
    def return_for_correction(self, request, pk=None):
        project = self.get_object()
        if project.status != InspectionProject.Status.REVIEW:
            raise ValidationError({"status": "Only projects in Review can be returned for correction."})
        old_value = build_model_snapshot(project)
        project.status = InspectionProject.Status.IN_PROGRESS
        project.save(update_fields=["status", "updated_at"])
        log_audit_event(
            user=request.user,
            action="returned_for_correction",
            instance=project,
            old_value=old_value,
            new_value=build_model_snapshot(project),
        )
        return response.Response({"status": project.status})

    @decorators.action(detail=True, methods=["post"], url_path="set-report-template")
    def set_report_template(self, request, pk=None):
        project = self.get_object()
        template_id = request.data.get("report_template")
        if template_id and not ReportTemplate.objects.filter(pk=template_id, is_active=True).exists():
            raise ValidationError({"report_template": "Выбранный шаблон недоступен."})
        old_value = build_model_snapshot(project)
        project.report_template_id = template_id or None
        project.save(update_fields=["report_template", "updated_at"])
        log_audit_event(
            user=request.user,
            action="set_report_template",
            instance=project,
            old_value=old_value,
            new_value=build_model_snapshot(project),
        )
        return response.Response(self.get_serializer(project).data)

    @decorators.action(detail=True, methods=["get"], url_path="reports")
    def reports(self, request, pk=None):
        project = self.get_object()
        queryset = project.reports.select_related("project", "project__building_object", "generated_by", "approved_by").order_by("-version", "-created_at")
        if request.user.role == "Client":
            queryset = queryset.filter(status=Report.Status.APPROVED)
        serializer = ReportSerializer(queryset, many=True, context=self.get_serializer_context())
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=["get"], url_path="passport")
    def passport(self, request, pk=None):
        project = self.get_object()
        if project.status != InspectionProject.Status.APPROVED and request.user.role == "Client":
            raise PermissionDenied("Client access is available only for approved projects.")
        report_queryset = project.reports.order_by("-version", "-created_at")
        if request.user.role == "Client":
            report_queryset = report_queryset.filter(status=Report.Status.APPROVED)
        latest_report = report_queryset.first()
        if request.user.role == "Client" and not latest_report:
            raise PermissionDenied("Client access is available only for approved reports.")
        if latest_report and latest_report.json_snapshot:
            return response.Response(latest_report.json_snapshot)
        return response.Response(build_passport_data(project))

    @decorators.action(detail=True, methods=["post"], url_path="reports/generate-docx")
    def generate_docx(self, request, pk=None):
        return self._generate_project_report(self.get_object(), request.user, self.get_serializer_context(), file_format="docx")

    @decorators.action(detail=True, methods=["post"], url_path="reports/generate-pdf")
    def generate_pdf(self, request, pk=None):
        return self._generate_project_report(self.get_object(), request.user, self.get_serializer_context(), file_format="pdf")

    @decorators.action(detail=True, methods=["post"], url_path="reports/generate")
    def generate_report(self, request, pk=None):
        project = self.get_object()
        file_format = (request.data.get("file_format") or request.query_params.get("file_format") or "docx").lower()
        if file_format not in {"docx", "pdf"}:
            raise ValidationError({"file_format": "Supported values are docx and pdf."})
        return self._generate_project_report(project, request.user, self.get_serializer_context(), file_format=file_format)


class TechnicalTaskViewSet(AuditedModelViewSet):
    queryset = TechnicalTask.objects.select_related("project").all()
    serializer_class = TechnicalTaskSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Manager", "Engineer"}


class WorkProgramViewSet(AuditedModelViewSet):
    queryset = WorkProgram.objects.select_related("project").all()
    serializer_class = WorkProgramSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Manager", "Engineer"}
