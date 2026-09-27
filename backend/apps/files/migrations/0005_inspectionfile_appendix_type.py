from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("files", "0004_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspectionfile",
            name="appendix_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("technical_documentation", "Техническая документация"),
                    ("sro_certificate", "Свидетельства СРО"),
                    ("specialist_qualification", "Квалификация специалистов"),
                    ("device_calibration", "Поверка приборов и оборудования"),
                    ("technical_task", "Техническое задание"),
                    ("work_program", "Программа работ"),
                    ("source_data", "Исходные данные"),
                    ("survey_protocol", "Протоколы обследования"),
                    ("calculation", "Поверочные расчеты"),
                    ("survey_act", "Акты обследования"),
                    ("normative_reference", "Нормативные ссылки"),
                    ("terms_definitions", "Термины и определения"),
                    ("abbreviations", "Обозначения и сокращения"),
                    ("graphic_material", "Графические материалы"),
                    ("other_appendix", "Прочие приложения"),
                ],
                max_length=64,
            ),
        ),
    ]
