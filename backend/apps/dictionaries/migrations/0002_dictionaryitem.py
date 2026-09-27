# Generated manually for controlled dictionaries support.

import uuid

from django.db import migrations, models


def seed_dictionary_items(apps, schema_editor):
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")
    seed_data = {
        "object_type": [
            ("residential_building", "Жилое здание"),
            ("administrative_building", "Административное здание"),
            ("industrial_building", "Производственное здание"),
            ("warehouse_building", "Складское здание"),
            ("structure", "Сооружение"),
        ],
        "inspection_type": [
            ("visual_inspection", "Визуальное обследование"),
            ("instrumental_inspection", "Инструментальное обследование"),
            ("comprehensive_inspection", "Комплексное обследование"),
            ("periodic_inspection", "Периодическое обследование"),
            ("extraordinary_inspection", "Внеочередное обследование"),
            ("before_reconstruction", "Обследование перед реконструкцией"),
            ("after_accident", "Обследование после аварии"),
        ],
        "element_type": [
            ("foundations", "Фундаменты"),
            ("columns", "Колонны"),
            ("beams", "Балки"),
            ("bearing_walls", "Несущие стены"),
            ("slabs", "Перекрытия / плиты"),
            ("coverings", "Покрытия"),
            ("roof", "Кровля"),
            ("facades", "Фасады"),
            ("stairs", "Лестницы"),
            ("floors", "Полы"),
            ("partitions", "Перегородки"),
            ("engineering_systems", "Инженерные системы"),
        ],
        "structural_system": [
            ("frame", "Каркасная"),
            ("wall", "Стеновая"),
            ("mixed", "Смешанная"),
            ("monolithic_reinforced_concrete", "Монолитный железобетон"),
            ("precast_reinforced_concrete", "Сборный железобетон"),
            ("brick", "Кирпичная"),
            ("metal_frame", "Металлический каркас"),
            ("wood", "Деревянная"),
        ],
        "material": [
            ("monolithic_reinforced_concrete", "Монолитный железобетон"),
            ("precast_reinforced_concrete", "Сборный железобетон"),
            ("brick", "Кирпич"),
            ("metal", "Металл"),
            ("wood", "Дерево"),
            ("concrete", "Бетон"),
            ("stone_masonry", "Каменная кладка"),
            ("aac", "Газобетон"),
            ("plaster_layer", "Штукатурный слой"),
            ("roofing_material", "Кровельный материал"),
        ],
        "condition_category": [
            ("normative", "Нормативное"),
            ("serviceable", "Работоспособное"),
            ("limited_serviceable", "Ограниченно-работоспособное"),
            ("emergency", "Аварийное"),
        ],
        "defect_type": [
            ("crack", "Трещина"),
            ("chip", "Скол"),
            ("corrosion", "Коррозия"),
            ("deflection", "Прогиб"),
            ("deformation", "Деформация"),
            ("moistening", "Увлажнение"),
            ("leak", "Протечка"),
            ("delamination", "Отслоение"),
            ("protective_layer_failure", "Разрушение защитного слоя"),
            ("support_node_failure", "Нарушение узла опирания"),
        ],
        "defect_severity": [
            ("minor", "Незначительный"),
            ("moderate", "Умеренный"),
            ("major", "Значительный"),
            ("critical", "Критический"),
            ("emergency", "Аварийный"),
        ],
        "defect_cause": [
            ("physical_wear", "Физический износ"),
            ("corrosion", "Коррозия"),
            ("moistening", "Увлажнение"),
            ("operational_violation", "Нарушение эксплуатации"),
            ("overload", "Перегрузка"),
            ("temperature_impact", "Температурное воздействие"),
            ("shrinkage", "Усадочные процессы"),
            ("design_errors", "Ошибки проектирования"),
            ("construction_errors", "Ошибки строительства"),
            ("mechanical_damage", "Механическое повреждение"),
            ("needs_clarification", "Причина требует уточнения"),
        ],
        "recommendation_type": [
            ("repair_not_required", "Ремонт не требуется"),
            ("routine_repair", "Требуется текущий ремонт"),
            ("major_repair", "Требуется капитальный ремонт"),
            ("strengthening", "Требуется усиление конструкции"),
            ("additional_instrumental_inspection", "Требуется дополнительное инструментальное обследование"),
            ("monitoring", "Требуется наблюдение в динамике"),
            ("restricted_operation", "Требуется ограничение эксплуатации"),
            ("immediate_fix", "Требуется немедленное устранение дефекта"),
            ("design_solution", "Требуется разработка проектного решения"),
            ("emergency_fencing", "Требуется аварийное ограждение зоны"),
        ],
        "inspection_method": [
            ("visual_inspection", "Визуальное обследование"),
            ("photo_fixation", "Фотофиксация"),
            ("instrumental_measurement", "Инструментальное измерение"),
            ("dimensional_survey", "Обмерные работы"),
            ("ndt", "Неразрушающий контроль"),
            ("crack_width_measurement", "Измерение раскрытия трещин"),
            ("moisture_measurement", "Измерение влажности"),
            ("concrete_strength", "Определение прочности бетона"),
            ("geodetic_survey", "Геодезическая съёмка"),
            ("thermal_imaging", "Тепловизионное обследование"),
        ],
        "measurement_type": [
            ("crack_width", "Ширина раскрытия трещины"),
            ("deflection", "Прогиб"),
            ("vertical_deviation", "Отклонение от вертикали"),
            ("moisture", "Влажность"),
            ("material_strength", "Прочность материала"),
            ("geometric_size", "Геометрический размер"),
            ("protective_layer_thickness", "Толщина защитного слоя"),
            ("temperature", "Температура"),
        ],
        "measurement_unit": [
            ("mm", "мм"),
            ("cm", "см"),
            ("m", "м"),
            ("m2", "м²"),
            ("m3", "м³"),
            ("percent", "%"),
            ("degree", "градус"),
            ("mpa", "МПа"),
            ("kg_cm2", "кг/см²"),
            ("mm_m", "мм/м"),
        ],
        "device": [
            ("laser_rangefinder", "Лазерный дальномер"),
            ("level", "Нивелир"),
            ("tape_measure", "Рулетка"),
            ("caliper", "Штангенциркуль"),
            ("feeler_gauge", "Щуп"),
            ("moisture_meter", "Влагомер"),
            ("concrete_strength_meter", "Измеритель прочности бетона"),
            ("thermal_imager", "Тепловизор"),
            ("thickness_gauge", "Толщиномер"),
            ("crack_meter", "Трещиномер"),
            ("geodetic_equipment", "Геодезическое оборудование"),
        ],
        "element_inspection_status": [
            ("not_inspected", "Не обследовано"),
            ("inspected_no_defects", "Обследовано, дефектов не выявлено"),
            ("inspected_with_defects", "Обследовано, дефекты выявлены"),
            ("not_accessible", "Недоступно для осмотра"),
            ("needs_additional_inspection", "Требуется дополнительное обследование"),
            ("needs_instrumental_inspection", "Требуется инструментальное обследование"),
        ],
    }
    for dictionary_type, items in seed_data.items():
        for index, (code, name_ru) in enumerate(items, start=1):
            DictionaryItem.objects.update_or_create(
                dictionary_type=dictionary_type,
                code=code,
                defaults={
                    "name_ru": name_ru,
                    "name_en": "",
                    "description": "",
                    "is_active": True,
                    "sort_order": index,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("dictionaries", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DictionaryItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("dictionary_type", models.CharField(choices=[("object_type", "Тип объекта"), ("inspection_type", "Вид обследования"), ("element_type", "Тип элемента"), ("structural_system", "Конструктивная система"), ("material", "Материал"), ("condition_category", "Категория технического состояния"), ("defect_type", "Тип дефекта"), ("defect_severity", "Степень дефекта"), ("defect_cause", "Причина дефекта"), ("recommendation_type", "Тип рекомендации"), ("inspection_method", "Метод обследования"), ("measurement_type", "Тип измерения"), ("measurement_unit", "Единица измерения"), ("device", "Прибор / оборудование"), ("element_inspection_status", "Статус обследования элемента")], max_length=64)),
                ("code", models.CharField(max_length=100)),
                ("name_ru", models.CharField(max_length=255)),
                ("name_en", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=100)),
            ],
            options={"ordering": ("dictionary_type", "sort_order", "name_ru")},
        ),
        migrations.AddConstraint(
            model_name="dictionaryitem",
            constraint=models.UniqueConstraint(fields=("dictionary_type", "code"), name="dictionary_item_type_code_unique"),
        ),
        migrations.RunPython(seed_dictionary_items, migrations.RunPython.noop),
    ]
