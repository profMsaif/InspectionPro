from django.db import migrations, models
import django.db.models.deletion


def backfill_project_dictionaries(apps, schema_editor):
    InspectionProject = apps.get_model("inspections", "InspectionProject")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")
    for project in InspectionProject.objects.all():
        if project.inspection_type and not project.inspection_type_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="inspection_type", name_ru__iexact=project.inspection_type).first()
            if match:
                project.inspection_type_dictionary_id = match.id
        if project.final_condition_category and not project.final_condition_category_dictionary_id:
            match = DictionaryItem.objects.filter(dictionary_type="condition_category", name_ru__iexact=project.final_condition_category).first()
            if match:
                project.final_condition_category_dictionary_id = match.id
        project.save(update_fields=["inspection_type_dictionary", "final_condition_category_dictionary"])


class Migration(migrations.Migration):
    dependencies = [
        ("dictionaries", "0002_dictionaryitem"),
        ("inspections", "0003_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inspectionproject",
            name="inspection_type",
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name="inspectionproject",
            name="final_condition_category_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "condition_category"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="final_condition_projects", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="inspectionproject",
            name="inspection_type_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "inspection_type"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="inspection_type_projects", to="dictionaries.dictionaryitem"),
        ),
        migrations.RunPython(backfill_project_dictionaries, migrations.RunPython.noop),
    ]
