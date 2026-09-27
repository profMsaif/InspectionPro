from django.db import migrations, models
import django.db.models.deletion


def backfill_element_dictionaries(apps, schema_editor):
    StructuralElement = apps.get_model("elements", "StructuralElement")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")
    status_map = {
        False: "inspected_no_defects",
        True: "inspected_with_defects",
    }
    for element in StructuralElement.objects.all():
        if element.element_type and not element.element_type_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="element_type", name_ru__iexact=element.element_type).first()
            if match:
                element.element_type_dictionary_id = match.id
        if element.material and not element.material_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="material", name_ru__iexact=element.material).first()
            if match:
                element.material_dictionary_id = match.id
        if element.inspection_method and not element.inspection_method_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="inspection_method", name_ru__iexact=element.inspection_method).first()
            if match:
                element.inspection_method_dictionary_id = match.id
        if element.condition_category and not element.condition_category_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="condition_category", name_ru__iexact=element.condition_category).first()
            if match:
                element.condition_category_dictionary_id = match.id
        if not element.inspection_status_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="element_inspection_status", code=status_map[element.has_defects]).first()
            if match:
                element.inspection_status_dictionary_id = match.id
        element.save(
            update_fields=[
                "element_type_dictionary",
                "material_dictionary",
                "inspection_method_dictionary",
                "condition_category_dictionary",
                "inspection_status_dictionary",
            ]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("dictionaries", "0002_dictionaryitem"),
        ("elements", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="structuralelement",
            name="condition_category_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "condition_category"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="condition_elements", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="structuralelement",
            name="element_type_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "element_type"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="typed_elements", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="structuralelement",
            name="inspection_method_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "inspection_method"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="inspection_method_elements", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="structuralelement",
            name="inspection_status_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "element_inspection_status"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="status_elements", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="structuralelement",
            name="material_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "material"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="material_elements", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="structuralelement",
            name="recommendation_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "recommendation_type"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="recommendation_elements", to="dictionaries.dictionaryitem"),
        ),
        migrations.RunPython(backfill_element_dictionaries, migrations.RunPython.noop),
    ]
