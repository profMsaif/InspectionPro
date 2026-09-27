from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedUUIDModel
from apps.dictionaries.models import DictionaryItem


class InspectionProject(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        PLANNED = "Planned", "Planned"
        IN_PROGRESS = "In Progress", "In Progress"
        REVIEW = "Review", "Review"
        APPROVED = "Approved", "Approved"
        ARCHIVED = "Archived", "Archived"

    class InspectionType(models.TextChoices):
        PLANNED = "planned", "Planned"
        EXCEPTIONAL = "exceptional", "Exceptional"
        MONITORING = "monitoring", "Monitoring"

    building_object = models.ForeignKey("objects.BuildingObject", on_delete=models.CASCADE, related_name="projects")
    customer_name = models.CharField(max_length=255)
    contract_number = models.CharField(max_length=100, blank=True)
    inspection_reason = models.TextField()
    inspection_goal = models.TextField()
    inspection_type = models.CharField(max_length=255)
    inspection_type_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="inspection_type_projects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.INSPECTION_TYPE},
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    responsible_engineer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="responsible_projects")
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="inspection_teams")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    final_condition_category = models.CharField(max_length=100, blank=True)
    final_condition_category_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="final_condition_projects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.CONDITION_CATEGORY},
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_projects")
    report_template = models.ForeignKey(
        "reports.ReportTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="projects",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.building_object.name} - {self.id}"


class TechnicalTask(TimeStampedUUIDModel):
    project = models.OneToOneField(InspectionProject, on_delete=models.CASCADE, related_name="technical_task")
    execution_basis = models.TextField(blank=True)
    survey_goal = models.TextField(blank=True)
    building_parts = models.TextField(blank=True)
    engineering_systems = models.TextField(blank=True)
    required_methods = models.TextField(blank=True)
    result_requirements = models.TextField(blank=True)
    deadlines = models.TextField(blank=True)
    output_documentation = models.TextField(blank=True)

    def __str__(self):
        return f"Technical Task: {self.project_id}"


class WorkProgram(TimeStampedUUIDModel):
    project = models.OneToOneField(InspectionProject, on_delete=models.CASCADE, related_name="work_program")
    structures = models.TextField(blank=True)
    zones = models.TextField(blank=True)
    methods = models.TextField(blank=True)
    tools_and_devices = models.TextField(blank=True)
    measurements = models.TextField(blank=True)
    photo_requirements = models.TextField(blank=True)
    responsible_executors = models.TextField(blank=True)
    completeness_checklist = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Work Program: {self.project_id}"
