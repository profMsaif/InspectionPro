from rest_framework import serializers

from apps.dictionaries.models import DictionaryItem
from apps.measurements.models import Measurement


class MeasurementSerializer(serializers.ModelSerializer):
    structural_element_name = serializers.CharField(source="structural_element.name", read_only=True)
    engineer_name = serializers.CharField(source="engineer.full_name", read_only=True)
    measurement_type_dictionary_name = serializers.CharField(source="measurement_type_dictionary.name_ru", read_only=True)
    unit_dictionary_name = serializers.CharField(source="unit_dictionary.name_ru", read_only=True)
    device_dictionary_name = serializers.CharField(source="device_dictionary.name_ru", read_only=True)
    method_dictionary_name = serializers.CharField(source="method_dictionary.name_ru", read_only=True)
    measurement_type_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.MEASUREMENT_TYPE, is_active=True),
        required=False,
        allow_null=True,
    )
    unit_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.MEASUREMENT_UNIT, is_active=True),
        required=False,
        allow_null=True,
    )
    device_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.DEVICE, is_active=True),
        required=False,
        allow_null=True,
    )
    method_dictionary = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.INSPECTION_METHOD, is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Measurement
        fields = "__all__"

    def validate(self, attrs):
        mapping = {
            "measurement_type": "measurement_type_dictionary",
            "unit": "unit_dictionary",
            "device": "device_dictionary",
            "method": "method_dictionary",
        }
        for target, source in mapping.items():
            item = attrs.get(source)
            if item:
                attrs[target] = item.name_ru
        return attrs
