from django.db import models

from apps.common.models import TimeStampedUUIDModel
from apps.dictionaries.models import DictionaryItem


class StructuralElement(TimeStampedUUIDModel):
    class Recommendation(models.TextChoices):
        NOT_REQUIRED = "not_required", "Не требуются"
        OBSERVE = "observe", "Требуется наблюдение"
        REPAIR = "repair", "Требуется ремонт"
        DETAILED_SURVEY = "detailed_survey", "Требуется детальное обследование"

    project = models.ForeignKey("inspections.InspectionProject", on_delete=models.CASCADE, related_name="elements")
    building_object = models.ForeignKey("objects.BuildingObject", on_delete=models.CASCADE, related_name="elements")
    element_type = models.CharField(max_length=100)
    element_type_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="typed_elements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.ELEMENT_TYPE},
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    floor = models.CharField(max_length=100, blank=True)
    axes = models.CharField(max_length=100, blank=True)
    material = models.CharField(max_length=255, blank=True)
    material_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="material_elements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.MATERIAL},
    )
    description = models.TextField(blank=True)
    is_accessible = models.BooleanField(default=True)
    inspection_method = models.CharField(max_length=255, blank=True)
    inspection_method_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="inspection_method_elements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.INSPECTION_METHOD},
    )
    visual_condition = models.CharField(max_length=255, blank=True)
    has_defects = models.BooleanField(default=False)
    no_defects_comment = models.CharField(max_length=255, blank=True)
    condition_category = models.CharField(max_length=100, blank=True)
    condition_category_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="condition_elements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.CONDITION_CATEGORY},
    )
    inspection_status_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="status_elements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.ELEMENT_INSPECTION_STATUS},
    )
    conclusion = models.TextField(blank=True)
    recommendation = models.CharField(max_length=32, choices=Recommendation.choices, default=Recommendation.NOT_REQUIRED)
    recommendation_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="recommendation_elements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.RECOMMENDATION_TYPE},
    )

    class Meta:
        ordering = ("element_type", "name")

    def __str__(self):
        return self.name
