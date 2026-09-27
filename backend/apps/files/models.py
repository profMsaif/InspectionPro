from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedUUIDModel


class InspectionFile(TimeStampedUUIDModel):
    class Category(models.TextChoices):
        OBJECT = "object", "Object"
        PROJECT = "project", "Project"
        ELEMENT = "element", "Element"
        DEFECT = "defect", "Defect"
        MEASUREMENT = "measurement", "Measurement"
        REPORT = "report", "Report"

    class AppendixType(models.TextChoices):
        TECHNICAL_DOCUMENTATION = "technical_documentation", "Техническая документация"
        SRO_CERTIFICATE = "sro_certificate", "Свидетельства СРО"
        SPECIALIST_QUALIFICATION = "specialist_qualification", "Квалификация специалистов"
        DEVICE_CALIBRATION = "device_calibration", "Поверка приборов и оборудования"
        TECHNICAL_TASK = "technical_task", "Техническое задание"
        WORK_PROGRAM = "work_program", "Программа работ"
        SOURCE_DATA = "source_data", "Исходные данные"
        SURVEY_PROTOCOL = "survey_protocol", "Протоколы обследования"
        CALCULATION = "calculation", "Поверочные расчеты"
        SURVEY_ACT = "survey_act", "Акты обследования"
        NORMATIVE_REFERENCE = "normative_reference", "Нормативные ссылки"
        TERMS_DEFINITIONS = "terms_definitions", "Термины и определения"
        ABBREVIATIONS = "abbreviations", "Обозначения и сокращения"
        GRAPHIC_MATERIAL = "graphic_material", "Графические материалы"
        OTHER_APPENDIX = "other_appendix", "Прочие приложения"

    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    caption = models.CharField(max_length=255, blank=True)
    is_for_report = models.BooleanField(default=False)
    category = models.CharField(max_length=32, choices=Category.choices)
    appendix_type = models.CharField(max_length=64, choices=AppendixType.choices, blank=True)
    building_object = models.ForeignKey("objects.BuildingObject", null=True, blank=True, on_delete=models.CASCADE, related_name="files")
    project = models.ForeignKey("inspections.InspectionProject", null=True, blank=True, on_delete=models.CASCADE, related_name="files")
    structural_element = models.ForeignKey("elements.StructuralElement", null=True, blank=True, on_delete=models.CASCADE, related_name="files")
    defect = models.ForeignKey("defects.Defect", null=True, blank=True, on_delete=models.CASCADE, related_name="files")
    measurement = models.ForeignKey("measurements.Measurement", null=True, blank=True, on_delete=models.CASCADE, related_name="files")
    report = models.ForeignKey("reports.Report", null=True, blank=True, on_delete=models.CASCADE, related_name="files")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploaded_files")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.original_name
