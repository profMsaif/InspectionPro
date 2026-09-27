from django.contrib import admin

from apps.dictionaries.models import DictionaryItem


@admin.register(DictionaryItem)
class DictionaryItemAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "dictionary_type", "code", "is_active", "sort_order", "updated_at")
    list_filter = ("dictionary_type", "is_active")
    search_fields = ("name_ru", "name_en", "code", "description")
