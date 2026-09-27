from rest_framework import serializers

from apps.dictionaries.models import DictionaryItem
from apps.inspections.models import InspectionProject, TechnicalTask, WorkProgram
from apps.reports.models import ReportTemplate


class TechnicalTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalTask
        fields = "__all__"


class WorkProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkProgram
        fields = "__all__"


class InspectionProjectSerializer(serializers.ModelSerializer):
    technical_task = TechnicalTaskSerializer(read_only=True)
    work_program = WorkProgramSerializer(read_only=True)
    building_object_name = serializers.CharField(source="building_object.name", read_only=True)
    responsible_engineer_name = serializers.CharField(source="responsible_engineer.full_name", read_only=True)
    inspection_type_dictionary_name = serializers.CharField(source="inspection_type_dictionary.name_ru", read_only=True)
    final_condition_category_dictionary_name = serializers.CharField(source="final_condition_category_dictionary.name_ru", read_only=True)
    report_template_name = serializers.CharField(source="report_template.name", read_only=True)
    inspection_type_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(
            dictionary_type=DictionaryItem.DictionaryType.INSPECTION_TYPE,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )
    final_condition_category_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(
            dictionary_type=DictionaryItem.DictionaryType.CONDITION_CATEGORY,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )
    report_template = serializers.PrimaryKeyRelatedField(
        queryset=ReportTemplate.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = InspectionProject
        fields = "__all__"
        read_only_fields = ("created_by",)

    def validate(self, attrs):
        inspection_type = attrs.get("inspection_type_dictionary")
        final_condition = attrs.get("final_condition_category_dictionary")
        if inspection_type:
            attrs["inspection_type"] = inspection_type.name_ru
        if final_condition:
            attrs["final_condition_category"] = final_condition.name_ru
        return attrs

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
