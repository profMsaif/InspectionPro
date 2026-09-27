import logging

from django.http import FileResponse
from django.utils import timezone
from rest_framework import decorators, response
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError

from apps.common.audit import build_model_snapshot, log_audit_event
from apps.common.permissions import RoleBasedPermission
from apps.common.viewsets import AuditedModelViewSet
from apps.inspections.services import validate_project_readiness
from apps.reports.models import Report, ReportTemplate, ReportTemplateBlock
from apps.reports.serializers import ReportSerializer, ReportTemplateBlockSerializer, ReportTemplateSerializer
from apps.reports.services import (
    PDF_EXPORT_AVAILABLE,
    PDF_EXPORT_UNAVAILABLE_MESSAGE,
    attach_generated_report_file,
    build_report_snapshot,
    build_report_title,
    generate_docx_bytes,
    generate_pdf_bytes,
    get_or_create_working_report,
    report_filename,
    update_report_snapshot,
)

logger = logging.getLogger(__name__)


class ReportViewSet(AuditedModelViewSet):
    queryset = Report.objects.select_related("project", "project__building_object", "generated_by", "approved_by").all()
    serializer_class = ReportSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert", "Client"}
    write_roles = {"Admin", "Manager", "Engineer", "Expert"}
    action_roles = {
        "approve": {"Admin", "Expert"},
    }
    filterset_fields = ("project", "status", "approved_by")
    search_fields = ("title", "summary")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == "Client":
            return queryset.filter(status=Report.Status.APPROVED)
        return queryset

    def perform_update(self, serializer):
        if serializer.instance.status == Report.Status.APPROVED:
            raise ValidationError({"status": "Approved reports are locked. Generate a new version instead."})
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.status == Report.Status.APPROVED:
            raise ValidationError({"status": "Approved reports cannot be deleted."})
        super().perform_destroy(instance)

    @decorators.action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        report = self.get_object()
        if request.user.role not in {"Admin", "Expert"} and not request.user.is_superuser:
            raise PermissionDenied("Only experts can approve reports.")
        if report.status not in {Report.Status.GENERATED, Report.Status.APPROVED}:
            raise ValidationError({"status": "Only generated reports can be approved."})
        if not report.json_snapshot:
            raise ValidationError({"report": "Report snapshot is missing. Generate report before approval."})
        if not report.project.final_condition_category:
            raise ValidationError({"project": "Project final condition category must be set before report approval."})
        old_value = build_model_snapshot(report)
        report.status = Report.Status.APPROVED
        report.approved_by = request.user
        report.approved_at = timezone.now()
        report.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        log_audit_event(
            user=request.user,
            action="approved",
            instance=report,
            old_value=old_value,
            new_value=build_model_snapshot(report),
        )
        return response.Response(self.get_serializer(report).data)

    def _download_file(self, report, file_format: str):
        if file_format == "pdf" and not PDF_EXPORT_AVAILABLE:
            raise ValidationError({"file": PDF_EXPORT_UNAVAILABLE_MESSAGE})
        report_file = report.docx_file if file_format == "docx" else report.pdf_file
        if not report_file:
            raise ValidationError({"file": f"{file_format.upper()} file has not been generated yet."})
        as_attachment = file_format == "docx"
        return FileResponse(
            report_file.open("rb"),
            as_attachment=as_attachment,
            filename=report_filename(report, file_format),
            content_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if file_format == "docx"
                else "application/pdf"
            ),
        )

    @decorators.action(detail=True, methods=["get"], url_path="download-docx")
    def download_docx(self, request, pk=None):
        return self._download_file(self.get_object(), "docx")

    @decorators.action(detail=True, methods=["get"], url_path="download-pdf")
    def download_pdf(self, request, pk=None):
        return self._download_file(self.get_object(), "pdf")

    @decorators.action(detail=True, methods=["get"], url_path=r"download/(?P<file_format>docx|pdf)")
    def download(self, request, pk=None, file_format=None):
        return self._download_file(self.get_object(), (file_format or "docx").lower())

    @decorators.action(detail=False, methods=["post"], url_path=r"generate/(?P<project_id>[^/.]+)/(?P<file_format>docx|pdf)")
    def generate(self, request, project_id=None, file_format=None):
        from apps.inspections.models import InspectionProject

        try:
            if file_format == "pdf" and not PDF_EXPORT_AVAILABLE:
                raise ValidationError({"file_format": PDF_EXPORT_UNAVAILABLE_MESSAGE})
            project = InspectionProject.objects.select_related(
                "building_object",
                "responsible_engineer",
                "technical_task",
                "work_program",
            ).get(pk=project_id)
            validate_project_readiness(project)
            report = get_or_create_working_report(project, request.user, build_report_title(project))
            old_value = build_model_snapshot(report)
            snapshot = build_report_snapshot(project)
            report = update_report_snapshot(report, snapshot=snapshot, generated_by=request.user)
            content = generate_docx_bytes(snapshot) if file_format == "docx" else generate_pdf_bytes(snapshot)
            report = attach_generated_report_file(report, file_format=file_format, content=content)
            log_audit_event(
                user=request.user,
                action=f"generated_{file_format}",
                instance=report,
                old_value=old_value,
                new_value=build_model_snapshot(report),
            )
            return response.Response(self.get_serializer(report).data)
        except ValidationError:
            raise
        except Exception as exc:
            logger.exception("Report generation failed for project %s in %s format", project_id, file_format)
            raise APIException("Failed to generate report.") from exc


class ReportTemplateViewSet(AuditedModelViewSet):
    queryset = ReportTemplate.objects.prefetch_related("blocks").all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Expert"}
    filterset_fields = ("is_active", "is_default")
    search_fields = ("name", "code", "description")


class ReportTemplateBlockViewSet(AuditedModelViewSet):
    queryset = ReportTemplateBlock.objects.select_related("template").all()
    serializer_class = ReportTemplateBlockSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Expert"}
    filterset_fields = ("template", "block_type", "is_enabled")
    search_fields = ("title_override",)
