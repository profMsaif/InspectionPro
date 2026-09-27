from rest_framework import decorators, response, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.viewsets import ModelViewSet

from apps.common.permissions import RoleBasedPermission
from apps.dictionaries.models import DictionaryItem
from apps.dictionaries.serializers import DictionaryItemSerializer, DictionaryReorderSerializer


class DictionaryItemViewSet(ModelViewSet):
    queryset = DictionaryItem.objects.all()
    serializer_class = DictionaryItemSerializer
    permission_classes = [RoleBasedPermission]
    read_roles = {"Admin", "Manager", "Engineer", "Expert"}
    write_roles = {"Admin", "Expert"}
    filterset_fields = ("dictionary_type", "is_active")
    search_fields = ("code", "name_ru", "name_en", "description")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        dictionary_type = self.request.query_params.get("dictionary_type")
        if dictionary_type:
            queryset = queryset.filter(dictionary_type=dictionary_type)
        if user.role not in {"Admin", "Expert"} and not user.is_superuser:
            queryset = queryset.filter(is_active=True)
        return queryset

    def perform_destroy(self, instance):
        if self.request.user.role not in {"Admin", "Expert"} and not self.request.user.is_superuser:
            raise PermissionDenied("Only experts can deactivate dictionary values.")
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])

    @decorators.action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        if request.user.role not in {"Admin", "Expert"} and not request.user.is_superuser:
            raise PermissionDenied("Only experts can reorder dictionary values.")
        serializer = DictionaryReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_ids = serializer.validated_data["items"]
        items = list(DictionaryItem.objects.filter(id__in=item_ids))
        if len(items) != len(item_ids):
            raise ValidationError({"items": "Some dictionary values were not found."})
        dictionary_types = {item.dictionary_type for item in items}
        if len(dictionary_types) != 1:
            raise ValidationError({"items": "Reorder is allowed only within one dictionary type."})
        item_map = {item.id: item for item in items}
        for index, item_id in enumerate(item_ids, start=1):
            item = item_map[item_id]
            item.sort_order = index
            item.save(update_fields=["sort_order", "updated_at"])
        refreshed = DictionaryItem.objects.filter(id__in=item_ids).order_by("sort_order", "name_ru")
        return response.Response(DictionaryItemSerializer(refreshed, many=True).data, status=status.HTTP_200_OK)
