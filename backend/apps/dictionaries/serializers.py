from rest_framework import serializers

from apps.dictionaries.models import DictionaryItem


class DictionaryItemSerializer(serializers.ModelSerializer):
    dictionary_type_display = serializers.CharField(source="get_dictionary_type_display", read_only=True)

    class Meta:
        model = DictionaryItem
        fields = (
            "id",
            "dictionary_type",
            "dictionary_type_display",
            "code",
            "name_ru",
            "name_en",
            "description",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        )


class DictionaryReorderSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)
