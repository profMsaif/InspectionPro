from rest_framework import serializers

from apps.dictionaries.models import DictionaryItem
from apps.objects.models import BuildingObject


class BuildingObjectSerializer(serializers.ModelSerializer):
    object_type_dictionary_name = serializers.CharField(source="object_type_dictionary.name_ru", read_only=True)
    structural_system_dictionary_name = serializers.CharField(source="structural_system_dictionary.name_ru", read_only=True)
    main_material_dictionary_name = serializers.CharField(source="main_material_dictionary.name_ru", read_only=True)
    object_type_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(
            dictionary_type=DictionaryItem.DictionaryType.OBJECT_TYPE,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )
    structural_system_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(
            dictionary_type=DictionaryItem.DictionaryType.STRUCTURAL_SYSTEM,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )
    main_material_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(
            dictionary_type=DictionaryItem.DictionaryType.MATERIAL,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = BuildingObject
        fields = "__all__"
        read_only_fields = ("created_by",)

    def validate(self, attrs):
        object_type = attrs.get("object_type_dictionary")
        structural_system = attrs.get("structural_system_dictionary")
        main_material = attrs.get("main_material_dictionary")
        if object_type:
            attrs["object_type"] = object_type.name_ru
        if structural_system:
            attrs["structural_scheme"] = structural_system.name_ru
        if main_material:
            attrs["foundation_material"] = attrs.get("foundation_material") or main_material.name_ru
            attrs["wall_material"] = attrs.get("wall_material") or main_material.name_ru
            attrs["floor_material"] = attrs.get("floor_material") or main_material.name_ru
            attrs["roof_material"] = attrs.get("roof_material") or main_material.name_ru
        return attrs

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
