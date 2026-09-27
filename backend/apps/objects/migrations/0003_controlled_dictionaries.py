from django.db import migrations, models
import django.db.models.deletion


def backfill_object_dictionaries(apps, schema_editor):
    BuildingObject = apps.get_model("objects", "BuildingObject")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")
    for item in BuildingObject.objects.all():
        if item.object_type and not item.object_type_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="object_type", name_ru__iexact=item.object_type).first()
            if match:
                item.object_type_dictionary_id = match.id
        if item.structural_scheme and not item.structural_system_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="structural_system", name_ru__iexact=item.structural_scheme).first()
            if match:
                item.structural_system_dictionary_id = match.id
        if item.foundation_material and not item.main_material_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="material", name_ru__iexact=item.foundation_material).first()
            if match:
                item.main_material_dictionary_id = match.id
        item.save(update_fields=["object_type_dictionary", "structural_system_dictionary", "main_material_dictionary"])


class Migration(migrations.Migration):
    dependencies = [
        ("dictionaries", "0002_dictionaryitem"),
        ("objects", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="buildingobject",
            name="main_material_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "material"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="main_material_objects", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="buildingobject",
            name="object_type_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "object_type"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="object_type_objects", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="buildingobject",
            name="structural_system_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "structural_system"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="structural_system_objects", to="dictionaries.dictionaryitem"),
        ),
        migrations.RunPython(backfill_object_dictionaries, migrations.RunPython.noop),
    ]
