from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedUUIDModel
from apps.dictionaries.models import DictionaryItem


class Measurement(TimeStampedUUIDModel):
    project = models.ForeignKey("inspections.InspectionProject", on_delete=models.CASCADE, related_name="measurements")
    structural_element = models.ForeignKey("elements.StructuralElement", on_delete=models.CASCADE, related_name="measurements")
    defect = models.ForeignKey("defects.Defect", null=True, blank=True, on_delete=models.SET_NULL, related_name="measurements")
    measurement_type = models.CharField(max_length=100)
    measurement_type_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="typed_measurements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.MEASUREMENT_TYPE},
    )
    value = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=30)
    unit_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="unit_measurements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.MEASUREMENT_UNIT},
    )
    device = models.CharField(max_length=100, blank=True)
    device_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="device_measurements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.DEVICE},
    )
    method = models.CharField(max_length=255, blank=True)
    method_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="method_measurements",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.INSPECTION_METHOD},
    )
    location = models.CharField(max_length=255, blank=True)
    measured_at = models.DateTimeField()
    engineer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="measurements")
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ("-measured_at",)

    def __str__(self):
        return f"{self.measurement_type}: {self.value} {self.unit}"
