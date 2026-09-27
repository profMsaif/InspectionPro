from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedUUIDModel
from apps.dictionaries.models import DictionaryItem


class BuildingObject(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    cadastral_number = models.CharField(max_length=100, blank=True)
    object_type = models.CharField(max_length=100)
    object_type_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="object_type_objects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.OBJECT_TYPE},
    )
    purpose = models.CharField(max_length=255, blank=True)
    construction_year = models.PositiveIntegerField(null=True, blank=True)
    reconstruction_year = models.PositiveIntegerField(null=True, blank=True)
    floors_count = models.PositiveIntegerField(null=True, blank=True)
    area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    volume = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    structural_scheme = models.CharField(max_length=255, blank=True)
    structural_system_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="structural_system_objects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.STRUCTURAL_SYSTEM},
    )
    foundation_material = models.CharField(max_length=255, blank=True)
    wall_material = models.CharField(max_length=255, blank=True)
    floor_material = models.CharField(max_length=255, blank=True)
    roof_material = models.CharField(max_length=255, blank=True)
    main_material_dictionary = models.ForeignKey(
        DictionaryItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="main_material_objects",
        limit_choices_to={"dictionary_type": DictionaryItem.DictionaryType.MATERIAL},
    )
    description = models.TextField(blank=True)
    owner_name = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_objects")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name
