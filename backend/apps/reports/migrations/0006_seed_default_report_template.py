from django.db import migrations


def create_default_report_template(apps, schema_editor):
    ReportTemplate = apps.get_model("reports", "ReportTemplate")
    ReportTemplateBlock = apps.get_model("reports", "ReportTemplateBlock")

    template, _ = ReportTemplate.objects.get_or_create(
        code="gost-technical-report",
        defaults={
            "name": "Полный технический отчет ГОСТ",
            "description": "Базовый шаблон полного технического отчета по обследованию здания или сооружения.",
            "is_active": True,
            "is_default": True,
        },
    )
    ReportTemplate.objects.exclude(pk=template.pk).filter(is_default=True).update(is_default=False)
    template.is_active = True
    template.is_default = True
    template.save(update_fields=["is_active", "is_default", "updated_at"])

    blocks = [
        ("title_page", "Титульный лист"),
        ("table_of_contents", "Содержание"),
        ("introduction", "Введение"),
        ("inspection_information", "Сведения об обследовании"),
        ("object_information", "Информация об объекте"),
        ("technical_documentation_analysis", "Анализ технической документации"),
        ("brief_characteristics", "Краткая характеристика объекта"),
        ("visual_measurement_control", "Результаты визуального и измерительного контроля"),
        ("detailed_instrumental_control", "Результаты детального инструментального контроля"),
        ("environmental_impact", "Определение степени влияния внешних воздействий"),
        ("verification_calculations", "Результаты поверочных расчетов"),
        ("result_analysis", "Анализ результатов технического обследования"),
        ("conclusions", "Выводы"),
        ("recommendations", "Рекомендации"),
        ("appendices", "Приложения"),
    ]
    for index, (block_type, title) in enumerate(blocks, start=1):
        ReportTemplateBlock.objects.get_or_create(
            template=template,
            block_type=block_type,
            defaults={
                "title_override": title,
                "sort_order": index,
                "is_enabled": True,
                "is_required": block_type in {"title_page", "introduction", "object_information", "visual_measurement_control", "conclusions"},
                "settings": {},
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0005_reporttemplate_reporttemplateblock"),
    ]

    operations = [
        migrations.RunPython(create_default_report_template, migrations.RunPython.noop),
    ]
