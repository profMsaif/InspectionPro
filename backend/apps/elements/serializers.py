from rest_framework import serializers

from apps.dictionaries.models import DictionaryItem
from apps.elements.models import StructuralElement


class StructuralElementSerializer(serializers.ModelSerializer):
    building_object_name = serializers.CharField(source="building_object.name", read_only=True)
    project_display = serializers.CharField(source="project.contract_number", read_only=True)
    element_type_dictionary_name = serializers.CharField(source="element_type_dictionary.name_ru", read_only=True)
    material_dictionary_name = serializers.CharField(source="material_dictionary.name_ru", read_only=True)
    inspection_method_dictionary_name = serializers.CharField(source="inspection_method_dictionary.name_ru", read_only=True)
    condition_category_dictionary_name = serializers.CharField(source="condition_category_dictionary.name_ru", read_only=True)
    inspection_status_dictionary_name = serializers.CharField(source="inspection_status_dictionary.name_ru", read_only=True)
    recommendation_dictionary_name = serializers.CharField(source="recommendation_dictionary.name_ru", read_only=True)
    element_type_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.ELEMENT_TYPE, is_active=True),
        required=False,
        allow_null=True,
    )
    material_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.MATERIAL, is_active=True),
        required=False,
        allow_null=True,
    )
    inspection_method_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.INSPECTION_METHOD, is_active=True),
        required=False,
        allow_null=True,
    )
    condition_category_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.CONDITION_CATEGORY, is_active=True),
        required=False,
        allow_null=True,
    )
    inspection_status_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(
            dictionary_type=DictionaryItem.DictionaryType.ELEMENT_INSPECTION_STATUS,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )
    recommendation_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.RECOMMENDATION_TYPE, is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = StructuralElement
        fields = "__all__"

    def validate(self, attrs):
        has_defects = attrs.get("has_defects", getattr(self.instance, "has_defects", False))
        no_defects_comment = attrs.get("no_defects_comment", getattr(self.instance, "no_defects_comment", ""))
        if not has_defects and not no_defects_comment:
            raise serializers.ValidationError(
                {"no_defects_comment": "Fill in the note for elements without defects."}
            )
        mapping = {
            "element_type": "element_type_dictionary",
            "material": "material_dictionary",
            "inspection_method": "inspection_method_dictionary",
            "condition_category": "condition_category_dictionary",
        }
        for target, source in mapping.items():
            item = attrs.get(source)
            if item:
                attrs[target] = item.name_ru
        recommendation = attrs.get("recommendation_dictionary")
        if recommendation:
            if not attrs.get("conclusion"):
                attrs["conclusion"] = recommendation.name_ru
            recommendation_name = recommendation.name_ru.lower()
            if "наблюдение" in recommendation_name:
                attrs["recommendation"] = StructuralElement.Recommendation.OBSERVE
            elif any(token in recommendation_name for token in ("ремонт", "усиление", "ограждение", "устранение", "ограничение")):
                attrs["recommendation"] = StructuralElement.Recommendation.REPAIR
            elif "обслед" in recommendation_name:
                attrs["recommendation"] = StructuralElement.Recommendation.DETAILED_SURVEY
            else:
                attrs["recommendation"] = StructuralElement.Recommendation.NOT_REQUIRED
        return attrs
