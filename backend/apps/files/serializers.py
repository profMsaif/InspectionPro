from rest_framework import serializers

from apps.files.models import InspectionFile


class InspectionFileSerializer(serializers.ModelSerializer):
    appendix_type_display = serializers.CharField(source="get_appendix_type_display", read_only=True)

    class Meta:
        model = InspectionFile
        fields = "__all__"
        read_only_fields = ("uploaded_by", "original_name", "size")

    def create(self, validated_data):
        uploaded_file = validated_data["file"]
        validated_data["uploaded_by"] = self.context["request"].user
        validated_data["original_name"] = uploaded_file.name
        validated_data["size"] = uploaded_file.size
        validated_data["content_type"] = getattr(uploaded_file, "content_type", "")
        return super().create(validated_data)
