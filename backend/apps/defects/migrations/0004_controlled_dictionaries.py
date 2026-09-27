from django.db import migrations, models
import django.db.models.deletion


def backfill_defect_dictionaries(apps, schema_editor):
    Defect = apps.get_model("defects", "Defect")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")
    for defect in Defect.objects.all():
        for field_name, dictionary_type in (
            ("defect_type", "defect_type"),
            ("severity", "defect_severity"),
            ("probable_cause", "defect_cause"),
            ("preliminary_condition_category", "condition_category"),
            ("final_condition_category", "condition_category"),
            ("recommendation", "recommendation_type"),
        ):
            relation_name = f"{field_name}_dictionary"
            if getattr(defect, field_name) and not getattr(defect, f"{relation_name}_id", None):
                match = DictionaryItem.objects.filter(dictionary_type=dictionary_type, name_ru__iexact=getattr(defect, field_name)).first()
                if match:
                    setattr(defect, f"{relation_name}_id", match.id)
        defect.save(
            update_fields=[
                "defect_type_dictionary",
                "severity_dictionary",
                "probable_cause_dictionary",
                "preliminary_condition_category_dictionary",
                "final_condition_category_dictionary",
                "recommendation_dictionary",
            ]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("dictionaries", "0002_dictionaryitem"),
        ("defects", "0003_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="defect",
            name="defect_type_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "defect_type"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="typed_defects", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="defect",
            name="final_condition_category_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "condition_category"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="final_condition_defects", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="defect",
            name="preliminary_condition_category_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "condition_category"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="preliminary_condition_defects", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="defect",
            name="probable_cause_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "defect_cause"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="cause_defects", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="defect",
            name="recommendation_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "recommendation_type"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="recommendation_defects", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="defect",
            name="severity_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "defect_severity"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="severity_defects", to="dictionaries.dictionaryitem"),
        ),
        migrations.RunPython(backfill_defect_dictionaries, migrations.RunPython.noop),
    ]
