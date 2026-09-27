from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedUUIDModel


REPORT_TEMPLATE_BLOCK_CHOICES = [
    ("title_page", "Титульный лист"),
    ("table_of_contents", "Содержание"),
    ("introduction", "Введение"),
    ("inspection_information", "Сведения об обследовании"),
    ("object_information", "Информация об объекте"),
    ("technical_documentation_analysis", "Анализ технической документации"),
    ("brief_characteristics", "Краткая характеристика объекта"),
    ("visual_measurement_control", "Результаты визуального и измерительного контроля"),
    ("detailed_instrumental_control", "Результаты детального инструментального контроля"),
    ("environmental_impact", "Определение степени влияния внешних воздействий"),
    ("verification_calculations", "Результаты поверочных расчетов"),
    ("result_analysis", "Анализ результатов технического обследования"),
    ("conclusions", "Выводы"),
    ("recommendations", "Рекомендации"),
    ("appendices", "Приложения"),
]


def default_report_template_blocks():
    return [
        {
            "block_type": block_type,
            "title_override": label,
            "sort_order": index,
            "is_enabled": True,
            "is_required": block_type in {"title_page", "introduction", "object_information", "visual_measurement_control", "conclusions"},
        }
        for index, (block_type, label) in enumerate(REPORT_TEMPLATE_BLOCK_CHOICES, start=1)
    ]


class ReportTemplate(TimeStampedUUIDModel):
    code = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_report_templates")

    class Meta:
        ordering = ("name", "created_at")

    def __str__(self):
        return self.name


class Report(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        APPROVED = "approved", "Approved"
        ARCHIVED = "archived", "Archived"

    project = models.ForeignKey("inspections.InspectionProject", on_delete=models.CASCADE, related_name="reports")
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    docx_file = models.FileField(upload_to="reports/docx/", blank=True)
    pdf_file = models.FileField(upload_to="reports/pdf/", blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="generated_reports")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_reports")
    generated_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    json_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-generated_at", "-created_at")

    def __str__(self):
        return self.title


class ReportTemplateBlock(TimeStampedUUIDModel):
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name="blocks")
    block_type = models.CharField(max_length=64, choices=REPORT_TEMPLATE_BLOCK_CHOICES)
    title_override = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=1)
    is_enabled = models.BooleanField(default=True)
    is_required = models.BooleanField(default=False)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("sort_order", "created_at")
        constraints = [
            models.UniqueConstraint(fields=("template", "block_type"), name="unique_template_block_type"),
        ]

    def __str__(self):
        return f"{self.template.name}: {self.block_type}"
