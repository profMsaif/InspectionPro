from django.db import models

from apps.common.models import TimeStampedUUIDModel


class DictionaryItem(TimeStampedUUIDModel):
    class DictionaryType(models.TextChoices):
        OBJECT_TYPE = "object_type", "Тип объекта"
        INSPECTION_TYPE = "inspection_type", "Вид обследования"
        ELEMENT_TYPE = "element_type", "Тип элемента"
        STRUCTURAL_SYSTEM = "structural_system", "Конструктивная система"
        MATERIAL = "material", "Материал"
        CONDITION_CATEGORY = "condition_category", "Категория технического состояния"
        DEFECT_TYPE = "defect_type", "Тип дефекта"
        DEFECT_SEVERITY = "defect_severity", "Степень дефекта"
        DEFECT_CAUSE = "defect_cause", "Причина дефекта"
        RECOMMENDATION_TYPE = "recommendation_type", "Тип рекомендации"
        INSPECTION_METHOD = "inspection_method", "Метод обследования"
        MEASUREMENT_TYPE = "measurement_type", "Тип измерения"
        MEASUREMENT_UNIT = "measurement_unit", "Единица измерения"
        DEVICE = "device", "Прибор / оборудование"
        ELEMENT_INSPECTION_STATUS = "element_inspection_status", "Статус обследования элемента"

    dictionary_type = models.CharField(max_length=64, choices=DictionaryType.choices)
    code = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ("dictionary_type", "sort_order", "name_ru")
        constraints = [
            models.UniqueConstraint(fields=("dictionary_type", "code"), name="dictionary_item_type_code_unique"),
        ]

    def __str__(self):
        return f"{self.get_dictionary_type_display()}: {self.name_ru}"
