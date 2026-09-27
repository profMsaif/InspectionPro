from django.db import migrations, models
import django.db.models.deletion


def backfill_measurement_dictionaries(apps, schema_editor):
    Measurement = apps.get_model("measurements", "Measurement")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")
    for measurement in Measurement.objects.all():
        for field_name, dictionary_type in (
            ("measurement_type", "measurement_type"),
            ("unit", "measurement_unit"),
            ("device", "device"),
            ("method", "inspection_method"),
        ):
            relation_name = f"{field_name}_dictionary"
            value = getattr(measurement, field_name)
            if value and not getattr(measurement, f"{relation_name}_id", None):
                match = DictionaryItem.objects.filter(dictionary_type=dictionary_type, name_ru__iexact=value).first()
                if match:
                    setattr(measurement, f"{relation_name}_id", match.id)
        measurement.save(
            update_fields=[
                "measurement_type_dictionary",
                "unit_dictionary",
                "device_dictionary",
                "method_dictionary",
            ]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("dictionaries", "0002_dictionaryitem"),
        ("measurements", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="measurement",
            name="device_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "device"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="device_measurements", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="measurement",
            name="measurement_type_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "measurement_type"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="typed_measurements", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="measurement",
            name="method_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "inspection_method"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="method_measurements", to="dictionaries.dictionaryitem"),
        ),
        migrations.AddField(
            model_name="measurement",
            name="unit_dictionary",
            field=models.ForeignKey(blank=True, limit_choices_to={"dictionary_type": "measurement_unit"}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="unit_measurements", to="dictionaries.dictionaryitem"),
        ),
        migrations.RunPython(backfill_measurement_dictionaries, migrations.RunPython.noop),
    ]
