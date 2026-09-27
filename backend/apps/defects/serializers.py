from rest_framework import serializers

from apps.dictionaries.models import DictionaryItem
from apps.defects.models import Defect


class DefectSerializer(serializers.ModelSerializer):
    structural_element_name = serializers.CharField(source="structural_element.name", read_only=True)
    project_display = serializers.CharField(source="project.contract_number", read_only=True)
    defect_type_dictionary_name = serializers.CharField(source="defect_type_dictionary.name_ru", read_only=True)
    severity_dictionary_name = serializers.CharField(source="severity_dictionary.name_ru", read_only=True)
    probable_cause_dictionary_name = serializers.CharField(source="probable_cause_dictionary.name_ru", read_only=True)
    preliminary_condition_category_dictionary_name = serializers.CharField(source="preliminary_condition_category_dictionary.name_ru", read_only=True)
    final_condition_category_dictionary_name = serializers.CharField(source="final_condition_category_dictionary.name_ru", read_only=True)
    recommendation_dictionary_name = serializers.CharField(source="recommendation_dictionary.name_ru", read_only=True)
    defect_type_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.DEFECT_TYPE, is_active=True),
        required=False,
        allow_null=True,
    )
    severity_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.DEFECT_SEVERITY, is_active=True),
        required=False,
        allow_null=True,
    )
    probable_cause_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.DEFECT_CAUSE, is_active=True),
        required=False,
        allow_null=True,
    )
    preliminary_condition_category_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.CONDITION_CATEGORY, is_active=True),
        required=False,
        allow_null=True,
    )
    final_condition_category_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.CONDITION_CATEGORY, is_active=True),
        required=False,
        allow_null=True,
    )
    recommendation_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.RECOMMENDATION_TYPE, is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Defect
        fields = "__all__"
        read_only_fields = ("created_by",)

    def validate(self, attrs):
        mapping = {
            "defect_type": "defect_type_dictionary",
            "severity": "severity_dictionary",
            "preliminary_condition_category": "preliminary_condition_category_dictionary",
            "final_condition_category": "final_condition_category_dictionary",
        }
        for target, source in mapping.items():
            item = attrs.get(source)
            if item:
                attrs[target] = item.name_ru
        probable_cause = attrs.get("probable_cause_dictionary")
        if probable_cause:
            attrs["probable_cause"] = probable_cause.name_ru
        recommendation = attrs.get("recommendation_dictionary")
        if recommendation:
            attrs["recommendation"] = recommendation.name_ru
        return attrs

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
