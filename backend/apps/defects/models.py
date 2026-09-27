from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedUUIDModel
from apps.dictionaries.models import DictionaryItem


class Defect(TimeStampedUUIDModel):
    project = models.ForeignKey("inspections.InspectionProject", on_delete=models.CASCADE, related_name="defects")
    building_object = models.ForeignKey("objects.BuildingObject", on_delete=models.CASCADE, related_name="defects")
    structural_element = models.ForeignKey("elements.StructuralElement", on_delete=models.CASCADE, related_name="defects")
    defect_type = models.CharField(max_length=100)
    defect_type_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="typed_defects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.DEFECT_TYPE},
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    floor = models.CharField(max_length=100, blank=True)
    room = models.CharField(max_length=100, blank=True)
    size_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    size_unit = models.CharField(max_length=50, blank=True)
    severity = models.CharField(max_length=100, blank=True)
    severity_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="severity_defects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.DEFECT_SEVERITY},
    )
    probable_cause = models.TextField(blank=True)
    probable_cause_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="cause_defects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.DEFECT_CAUSE},
    )
    influence_on_condition = models.TextField(blank=True)
    preliminary_condition_category = models.CharField(max_length=100, blank=True)
    preliminary_condition_category_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="preliminary_condition_defects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.CONDITION_CATEGORY},
    )
    final_condition_category = models.CharField(max_length=100, blank=True)
    final_condition_category_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="final_condition_defects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.CONDITION_CATEGORY},
    )
    recommendation = models.TextField(blank=True)
    recommendation_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="recommendation_defects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.RECOMMENDATION_TYPE},
    )
    status = models.CharField(max_length=50, default="Draft")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_defects")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title
