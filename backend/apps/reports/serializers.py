from rest_framework import serializers

from apps.reports.models import Report, ReportTemplate, ReportTemplateBlock, default_report_template_blocks
from apps.reports.services import PDF_EXPORT_AVAILABLE


class ReportSerializer(serializers.ModelSerializer):
    project_display = serializers.CharField(source="project.contract_number", read_only=True)
    project_id = serializers.UUIDField(source="project.id", read_only=True)
    object_name = serializers.CharField(source="project.building_object.name", read_only=True)
    download_docx_url = serializers.SerializerMethodField()
    download_pdf_url = serializers.SerializerMethodField()
    preview_available = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ("generated_by", "generated_at", "approved_by", "approved_at")

    def create(self, validated_data):
        validated_data["generated_by"] = self.context["request"].user
        return super().create(validated_data)

    def get_download_docx_url(self, obj):
        if not obj.docx_file:
            return None
        path = f"/api/reports/{obj.pk}/download-docx/"
        return path

    def get_download_pdf_url(self, obj):
        if not PDF_EXPORT_AVAILABLE or not obj.pdf_file:
            return None
        path = f"/api/reports/{obj.pk}/download-pdf/"
        return path

    def get_preview_available(self, obj):
        return bool(obj.json_snapshot)


class ReportTemplateBlockSerializer(serializers.ModelSerializer):
    block_type_display = serializers.CharField(source="get_block_type_display", read_only=True)

    class Meta:
        model = ReportTemplateBlock
        fields = "__all__"
        read_only_fields = ()


class ReportTemplateSerializer(serializers.ModelSerializer):
    blocks = ReportTemplateBlockSerializer(many=True, read_only=True)

    class Meta:
        model = ReportTemplate
        fields = "__all__"
        read_only_fields = ("created_by",)

    def create(self, validated_data):
        request = self.context["request"]
        if validated_data.get("is_default"):
            ReportTemplate.objects.filter(is_default=True).update(is_default=False)
        template = ReportTemplate.objects.create(created_by=request.user, **validated_data)
        ReportTemplateBlock.objects.bulk_create(
            [
                ReportTemplateBlock(template=template, **block)
                for block in default_report_template_blocks()
            ]
        )
        return template

    def update(self, instance, validated_data):
        if validated_data.get("is_default"):
            ReportTemplate.objects.exclude(pk=instance.pk).filter(is_default=True).update(is_default=False)
        return super().update(instance, validated_data)
