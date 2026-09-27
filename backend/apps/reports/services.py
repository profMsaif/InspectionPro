from __future__ import annotations

import logging
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape

from django.core.files.base import ContentFile
from django.db.models import Max
from django.utils import timezone

from apps.files.models import InspectionFile
from apps.reports.models import Report, ReportTemplate, REPORT_TEMPLATE_BLOCK_CHOICES

logger = logging.getLogger(__name__)

TECHNICAL_REPORT_TITLE = "ТЕХНИЧЕСКИЙ ОТЧЕТ"
TECHNICAL_REPORT_SUBTITLE = "по результатам обследования технического состояния конструкций"
PDF_EXPORT_AVAILABLE = False
PDF_EXPORT_UNAVAILABLE_MESSAGE = (
    "PDF export is temporarily unavailable. Use DOCX export while the PDF renderer is being upgraded for Cyrillic support."
)

APPENDIX_SECTION_TITLES = {
    InspectionFile.AppendixType.TECHNICAL_DOCUMENTATION: "Техническая документация",
    InspectionFile.AppendixType.SRO_CERTIFICATE: "Копии свидетельств СРО",
    InspectionFile.AppendixType.SPECIALIST_QUALIFICATION: "Сведения о составе и квалификации специалистов",
    InspectionFile.AppendixType.DEVICE_CALIBRATION: "Перечень приборов и оборудования с документами о поверке",
    InspectionFile.AppendixType.TECHNICAL_TASK: "Копия технического задания",
    InspectionFile.AppendixType.WORK_PROGRAM: "Программа проведения обследования",
    InspectionFile.AppendixType.SOURCE_DATA: "Исходные данные",
    InspectionFile.AppendixType.SURVEY_PROTOCOL: "Протоколы обследования технического состояния",
    InspectionFile.AppendixType.CALCULATION: "Поверочные расчеты",
    InspectionFile.AppendixType.SURVEY_ACT: "Акты обследования",
    InspectionFile.AppendixType.NORMATIVE_REFERENCE: "Нормативные ссылки",
    InspectionFile.AppendixType.TERMS_DEFINITIONS: "Термины и определения",
    InspectionFile.AppendixType.ABBREVIATIONS: "Обозначения и сокращения",
    InspectionFile.AppendixType.GRAPHIC_MATERIAL: "Графические материалы",
    InspectionFile.AppendixType.OTHER_APPENDIX: "Прочие приложения",
}

APPENDIX_DISPLAY_ORDER = [
    InspectionFile.AppendixType.TECHNICAL_DOCUMENTATION,
    InspectionFile.AppendixType.SRO_CERTIFICATE,
    InspectionFile.AppendixType.SPECIALIST_QUALIFICATION,
    InspectionFile.AppendixType.DEVICE_CALIBRATION,
    InspectionFile.AppendixType.TECHNICAL_TASK,
    InspectionFile.AppendixType.WORK_PROGRAM,
    InspectionFile.AppendixType.SOURCE_DATA,
    InspectionFile.AppendixType.SURVEY_PROTOCOL,
    InspectionFile.AppendixType.CALCULATION,
    InspectionFile.AppendixType.SURVEY_ACT,
    InspectionFile.AppendixType.NORMATIVE_REFERENCE,
    InspectionFile.AppendixType.TERMS_DEFINITIONS,
    InspectionFile.AppendixType.ABBREVIATIONS,
    InspectionFile.AppendixType.GRAPHIC_MATERIAL,
    InspectionFile.AppendixType.OTHER_APPENDIX,
]

REPORT_TEMPLATE_BLOCK_TITLES = dict(REPORT_TEMPLATE_BLOCK_CHOICES)

DOCUMENT_ANALYSIS_TYPES = {
    InspectionFile.AppendixType.TECHNICAL_DOCUMENTATION,
    InspectionFile.AppendixType.TECHNICAL_TASK,
    InspectionFile.AppendixType.WORK_PROGRAM,
    InspectionFile.AppendixType.SOURCE_DATA,
    InspectionFile.AppendixType.NORMATIVE_REFERENCE,
}

CALCULATION_INPUT_TYPES = {
    InspectionFile.AppendixType.SOURCE_DATA,
}

CALCULATION_RESULT_TYPES = {
    InspectionFile.AppendixType.CALCULATION,
}

DETAILED_SECTION_TITLE_OVERRIDES = {
    "Фундаменты": "Фундаменты и основания",
    "Перекрытия / плиты": "Плиты перекрытия",
    "Покрытия": "Плиты покрытия",
    "Инженерные системы": "Инженерные системы",
}


def dictionary_name(dictionary_item, fallback: str | None) -> str:
    if dictionary_item:
        return dictionary_item.name_ru
    return fallback or "—"


def display_value(value) -> str:
    if value in (None, "", [], {}):
        return "—"
    if isinstance(value, bool):
        return "Да" if value else "Нет"
    return str(value)


def serialize_date(value):
    if not value:
        return None
    return value.isoformat()


def serialize_datetime(value):
    if not value:
        return None
    return value.isoformat()


def safe_file_url(file_field) -> str | None:
    try:
        return file_field.url if file_field else None
    except Exception:
        return None


def appendix_type_title(appendix_type: str | None) -> str:
    if not appendix_type:
        return APPENDIX_SECTION_TITLES[InspectionFile.AppendixType.OTHER_APPENDIX]
    return APPENDIX_SECTION_TITLES.get(appendix_type, APPENDIX_SECTION_TITLES[InspectionFile.AppendixType.OTHER_APPENDIX])


def build_report_title(project) -> str:
    return f"{TECHNICAL_REPORT_TITLE}: {project.building_object.name}"


def translate_project_status(status: str | None) -> str:
    mapping = {
        "In Progress": "В работе",
        "Review": "На проверке",
        "Approved": "Утвержден",
        "Archived": "Архив",
    }
    return mapping.get(status or "", status or "—")


def resolve_project_report_template(project) -> ReportTemplate | None:
    if getattr(project, "report_template_id", None):
        return project.report_template
    return ReportTemplate.objects.filter(is_active=True, is_default=True).prefetch_related("blocks").first()


def resolve_block_title(block_type: str, title_override: str | None = None) -> str:
    return title_override or REPORT_TEMPLATE_BLOCK_TITLES.get(block_type, block_type)


def active_template_blocks(project) -> list[dict]:
    template = resolve_project_report_template(project)
    if not template:
        return [
            {
                "block_type": block_type,
                "title": label,
                "sort_order": index,
                "is_enabled": True,
                "is_required": False,
            }
            for index, (block_type, label) in enumerate(REPORT_TEMPLATE_BLOCK_CHOICES, start=1)
        ]

    return [
        {
            "id": str(block.id),
            "block_type": block.block_type,
            "title": resolve_block_title(block.block_type, block.title_override),
            "sort_order": block.sort_order,
            "is_enabled": block.is_enabled,
            "is_required": block.is_required,
        }
        for block in template.blocks.all().order_by("sort_order", "created_at")
        if block.is_enabled
    ]


def report_filename(report: Report, file_format: str) -> str:
    file_name = report.docx_file.name if file_format == "docx" else report.pdf_file.name
    base = Path(file_name).name if file_name else ""
    return base or f"report_v{report.version}.{file_format}"


def join_nonempty(values: list[str], separator: str = ", ") -> str:
    return separator.join([value for value in values if value and value != "—"]) or "—"


def make_plain_text(*parts: str) -> str:
    return " ".join(part.strip() for part in parts if part and part.strip()) or "—"


def normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def build_file_entry(file_item: InspectionFile) -> dict:
    appendix_type = file_item.appendix_type or ""
    return {
        "id": str(file_item.id),
        "category": file_item.category,
        "appendix_type": appendix_type or None,
        "appendix_type_display": (
            appendix_type_title(appendix_type)
            if appendix_type
            else (
                APPENDIX_SECTION_TITLES[InspectionFile.AppendixType.OTHER_APPENDIX]
                if file_item.category == InspectionFile.Category.PROJECT
                else "—"
            )
        ),
        "original_name": file_item.original_name,
        "content_type": file_item.content_type or "",
        "caption": file_item.caption,
        "url": safe_file_url(file_item.file),
        "uploaded_at": serialize_datetime(file_item.created_at),
        "uploaded_by": file_item.uploaded_by.full_name if file_item.uploaded_by_id else "—",
    }


def element_sort_key(element) -> tuple[int, str, str]:
    sort_order = element.element_type_dictionary.sort_order if element.element_type_dictionary_id else 9999
    return (
        sort_order,
        dictionary_name(element.element_type_dictionary, element.element_type),
        element.name,
    )


def section_title_for_element_type(element_type: str) -> str:
    return DETAILED_SECTION_TITLE_OVERRIDES.get(element_type, element_type)


def summarize_file_group(files: list[dict], *, empty_message: str) -> str:
    if not files:
        return empty_message
    labels = [item["original_name"] for item in files]
    return f"Приложено файлов: {len(files)}. {join_nonempty(labels)}."


def build_environmental_impact(defects: list[dict], element_assessments: list[dict]) -> dict:
    factors = [
        ("hydrological", "Гидрологические воздействия", ("увлаж", "влаж", "протеч", "гидро")),
        ("atmospheric", "Аэрологические и атмосферные воздействия", ("атмосфер", "осадк", "ветер", "снег")),
        ("temperature", "Температурные воздействия", ("температ", "замораж", "оттаив", "перепад")),
        ("corrosion", "Коррозионные воздействия", ("корроз", "ржав", "окисл")),
        ("operational", "Эксплуатационные и механические воздействия", ("эксплуатац", "перегруз", "механичес", "поврежден")),
    ]
    findings = []
    total_matches = 0

    for code, title, keywords in factors:
        matches = []
        for defect in defects:
            defect_text = normalize_text(
                make_plain_text(
                    defect.get("defect_type"),
                    defect.get("description"),
                    defect.get("probable_cause"),
                    defect.get("recommendation"),
                    defect.get("influence_on_condition"),
                )
            )
            if any(keyword in defect_text for keyword in keywords):
                matches.append(defect.get("title") or defect.get("defect_type") or "Дефект")
        unique_matches = list(dict.fromkeys(matches))
        total_matches += len(unique_matches)
        findings.append(
            {
                "code": code,
                "title": title,
                "finding": join_nonempty(unique_matches, "; ") if unique_matches else "Не выявлено / Не предоставлено",
            }
        )

    inaccessible_count = sum(1 for item in element_assessments if item["is_accessible"] == "Нет")
    if total_matches == 0 and inaccessible_count == 0:
        summary = "По имеющимся материалам признаки существенного влияния внешних воздействий не выявлены."
    elif total_matches == 0:
        summary = f"Прямые признаки внешних воздействий не зафиксированы, однако {inaccessible_count} элементов были недоступны для осмотра."
    else:
        summary = f"Выявлены признаки влияния внешних воздействий по {total_matches} зафиксированным проявлениям."

    return {
        "summary": summary,
        "factors": findings,
    }


def build_appendix_groups(project_file_entries: list[dict]) -> list[dict]:
    grouped_files: dict[str, list[dict]] = defaultdict(list)
    for entry in project_file_entries:
        appendix_type = entry["appendix_type"] or InspectionFile.AppendixType.OTHER_APPENDIX
        grouped_files[appendix_type].append(entry)

    groups = []
    group_index = 1
    for appendix_type in APPENDIX_DISPLAY_ORDER:
        files = grouped_files.get(appendix_type, [])
        if not files:
            continue
        groups.append(
            {
                "number": f"9.{group_index}",
                "appendix_type": appendix_type,
                "title": appendix_type_title(appendix_type),
                "files": files,
            }
        )
        group_index += 1
    return groups


def build_report_snapshot(project) -> dict:
    project = (
        project.__class__.objects.select_related(
            "building_object",
            "building_object__object_type_dictionary",
            "building_object__structural_system_dictionary",
            "building_object__main_material_dictionary",
            "responsible_engineer",
            "inspection_type_dictionary",
            "final_condition_category_dictionary",
            "report_template",
        )
        .prefetch_related(
            "report_template__blocks",
            "team",
            "elements__element_type_dictionary",
            "elements__material_dictionary",
            "elements__inspection_method_dictionary",
            "elements__condition_category_dictionary",
            "elements__inspection_status_dictionary",
            "elements__recommendation_dictionary",
            "elements__defects__defect_type_dictionary",
            "elements__defects__severity_dictionary",
            "elements__defects__probable_cause_dictionary",
            "elements__defects__preliminary_condition_category_dictionary",
            "elements__defects__final_condition_category_dictionary",
            "elements__defects__recommendation_dictionary",
            "elements__measurements__measurement_type_dictionary",
            "elements__measurements__unit_dictionary",
            "elements__measurements__device_dictionary",
            "elements__measurements__method_dictionary",
            "defects__structural_element",
            "defects__defect_type_dictionary",
            "defects__severity_dictionary",
            "defects__probable_cause_dictionary",
            "defects__preliminary_condition_category_dictionary",
            "defects__final_condition_category_dictionary",
            "defects__recommendation_dictionary",
            "measurements__structural_element",
            "measurements__defect",
            "measurements__measurement_type_dictionary",
            "measurements__unit_dictionary",
            "measurements__device_dictionary",
            "measurements__method_dictionary",
        )
        .get(pk=project.pk)
    )

    building_object = project.building_object
    report_template = resolve_project_report_template(project)
    responsible_engineer = project.responsible_engineer
    expert = next((member for member in project.team.all() if member.role == "Expert"), None)
    latest_approved_report = (
        project.reports.filter(status=Report.Status.APPROVED)
        .select_related("approved_by")
        .order_by("-version", "-created_at")
        .first()
    )
    inspection_organization = (
        getattr(latest_approved_report.approved_by, "organization", "")
        if latest_approved_report and latest_approved_report.approved_by_id
        else ""
    ) or getattr(responsible_engineer, "organization", "") or getattr(expert, "organization", "") or "—"

    files = list(
        InspectionFile.objects.filter(project=project, is_for_report=True)
        .select_related("uploaded_by", "building_object", "structural_element", "defect", "measurement")
        .order_by("category", "appendix_type", "created_at")
    )

    files_by_element: dict[str, list[dict]] = defaultdict(list)
    files_by_defect: dict[str, list[dict]] = defaultdict(list)
    files_by_measurement: dict[str, list[dict]] = defaultdict(list)
    object_overview_files: list[dict] = []
    project_file_entries: list[dict] = []
    defect_closeup_files: list[dict] = []
    measurement_evidence_files: list[dict] = []

    for file_item in files:
        entry = build_file_entry(file_item)
        if file_item.measurement_id:
            files_by_measurement[str(file_item.measurement_id)].append(entry)
            measurement_evidence_files.append(entry)
        if file_item.defect_id:
            files_by_defect[str(file_item.defect_id)].append(entry)
            defect_closeup_files.append(entry)
        elif file_item.structural_element_id:
            files_by_element[str(file_item.structural_element_id)].append(entry)
        elif file_item.category == InspectionFile.Category.PROJECT:
            project_file_entries.append(entry)
        elif file_item.building_object_id:
            object_overview_files.append(entry)
        else:
            project_file_entries.append(entry)

    measurements_by_element: dict[str, list[dict]] = defaultdict(list)
    measurements_by_defect: dict[str, list[dict]] = defaultdict(list)
    all_measurements: list[dict] = []
    measurement_rows = sorted(project.measurements.all(), key=lambda measurement: (measurement.measured_at, measurement.created_at))
    for measurement in measurement_rows:
        measurement_entry = {
            "id": str(measurement.id),
            "related_element": measurement.structural_element.name if measurement.structural_element_id else "—",
            "related_defect": measurement.defect.title if measurement.defect_id else None,
            "measurement_type": dictionary_name(measurement.measurement_type_dictionary, measurement.measurement_type),
            "value": str(measurement.value),
            "unit": dictionary_name(measurement.unit_dictionary, measurement.unit),
            "device": dictionary_name(measurement.device_dictionary, measurement.device),
            "method": dictionary_name(measurement.method_dictionary, measurement.method),
            "location": measurement.location or "—",
            "date": serialize_datetime(measurement.measured_at),
            "comment": measurement.comment or "—",
            "photos": files_by_measurement.get(str(measurement.id), []),
        }
        all_measurements.append(measurement_entry)
        if measurement.structural_element_id:
            measurements_by_element[str(measurement.structural_element_id)].append(measurement_entry)
        if measurement.defect_id:
            measurements_by_defect[str(measurement.defect_id)].append(measurement_entry)

    defects_by_element: dict[str, list[dict]] = defaultdict(list)
    all_defects: list[dict] = []
    defect_rows = sorted(project.defects.all(), key=lambda defect: defect.created_at)
    for defect in defect_rows:
        defect_entry = {
            "id": str(defect.id),
            "related_element": defect.structural_element.name if defect.structural_element_id else "—",
            "defect_type": dictionary_name(defect.defect_type_dictionary, defect.defect_type),
            "title": defect.title,
            "description": defect.description,
            "location": defect.location or "—",
            "floor": defect.floor or "—",
            "room": defect.room or "—",
            "axes": defect.structural_element.axes if defect.structural_element_id else "—",
            "dimensions": (
                f"{defect.size_value} {defect.size_unit}".strip()
                if defect.size_value is not None or defect.size_unit
                else "—"
            ),
            "severity": dictionary_name(defect.severity_dictionary, defect.severity),
            "probable_cause": dictionary_name(defect.probable_cause_dictionary, defect.probable_cause),
            "influence_on_condition": defect.influence_on_condition or "—",
            "condition_category": dictionary_name(
                defect.final_condition_category_dictionary,
                defect.final_condition_category or defect.preliminary_condition_category,
            ),
            "recommendation": dictionary_name(defect.recommendation_dictionary, defect.recommendation),
            "photos": files_by_defect.get(str(defect.id), []),
            "measurements": measurements_by_defect.get(str(defect.id), []),
        }
        all_defects.append(defect_entry)
        if defect.structural_element_id:
            defects_by_element[str(defect.structural_element_id)].append(defect_entry)

    sorted_elements = sorted(project.elements.all(), key=element_sort_key)
    element_assessments: list[dict] = []
    constructive_characteristics: dict[str, list[dict]] = defaultdict(list)
    recommendation_bucket: list[str] = []
    restrictions: list[str] = []
    needs_monitoring = False
    needs_additional_inspection = False

    for element in sorted_elements:
        element_id = str(element.id)
        recommendation_text = dictionary_name(element.recommendation_dictionary, element.conclusion or element.recommendation)
        recommendation_bucket.append(recommendation_text)
        recommendation_text_lower = recommendation_text.lower()
        if "наблюдение" in recommendation_text_lower:
            needs_monitoring = True
        if "дополнитель" in recommendation_text_lower or "инструмент" in recommendation_text_lower:
            needs_additional_inspection = True
        if "ограничение" in recommendation_text_lower:
            restrictions.append(recommendation_text)

        element_entry = {
            "id": element_id,
            "element_type": dictionary_name(element.element_type_dictionary, element.element_type),
            "element_name": element.name,
            "location": element.location or "—",
            "floor": element.floor or "—",
            "axes": element.axes or "—",
            "material": dictionary_name(element.material_dictionary, element.material),
            "inspection_status": dictionary_name(
                element.inspection_status_dictionary,
                "Обследовано, дефекты выявлены" if element.has_defects else "Обследовано, дефектов не выявлено",
            ),
            "visual_condition": element.visual_condition or "—",
            "condition_category": dictionary_name(element.condition_category_dictionary, element.condition_category),
            "conclusion": element.conclusion or element.no_defects_comment or "—",
            "recommendation": recommendation_text,
            "defects_found": "Да" if defects_by_element.get(element_id) or element.has_defects else "Нет",
            "is_accessible": "Да" if element.is_accessible else "Нет",
            "linked_photos": files_by_element.get(element_id, []),
            "linked_measurements": measurements_by_element.get(element_id, []),
            "linked_defects": defects_by_element.get(element_id, []),
        }
        element_assessments.append(element_entry)
        constructive_characteristics[element_entry["element_type"]].append(
            {
                "name": element.name,
                "location": element.location or "—",
                "material": element_entry["material"],
                "description": element.description or "—",
            }
        )

    object_materials = [
        item
        for item in [
            building_object.main_material_dictionary.name_ru if building_object.main_material_dictionary else "",
            building_object.foundation_material,
            building_object.wall_material,
            building_object.floor_material,
            building_object.roof_material,
        ]
        if item
    ]

    all_recommendations = recommendation_bucket + [item["recommendation"] for item in all_defects]
    for recommendation_text in all_recommendations:
        recommendation_text_lower = (recommendation_text or "").lower()
        if "наблюдение" in recommendation_text_lower:
            needs_monitoring = True
        if "дополнитель" in recommendation_text_lower or "инструмент" in recommendation_text_lower:
            needs_additional_inspection = True
        if "ограничение" in recommendation_text_lower and recommendation_text not in restrictions:
            restrictions.append(recommendation_text)

    unique_recommendations = []
    seen_recommendations = set()
    for recommendation in all_recommendations:
        if not recommendation or recommendation == "—":
            continue
        if recommendation not in seen_recommendations:
            unique_recommendations.append(recommendation)
            seen_recommendations.add(recommendation)

    appendix_groups = build_appendix_groups(project_file_entries)
    documentation_files = [
        entry
        for entry in project_file_entries
        if (entry["appendix_type"] or InspectionFile.AppendixType.OTHER_APPENDIX) in DOCUMENT_ANALYSIS_TYPES
    ]
    calculation_input_files = [
        entry
        for entry in project_file_entries
        if (entry["appendix_type"] or InspectionFile.AppendixType.OTHER_APPENDIX) in CALCULATION_INPUT_TYPES
    ]
    calculation_result_files = [
        entry
        for entry in project_file_entries
        if (entry["appendix_type"] or InspectionFile.AppendixType.OTHER_APPENDIX) in CALCULATION_RESULT_TYPES
    ]

    detailed_sections = []
    section_index = 1
    sections_by_type: dict[str, list[dict]] = defaultdict(list)
    for item in element_assessments:
        sections_by_type[item["element_type"]].append(item)
    for element_type, items in sections_by_type.items():
        section_title = section_title_for_element_type(element_type)
        section_defects = [defect for item in items for defect in item["linked_defects"]]
        section_measurements = [measurement for item in items for measurement in item["linked_measurements"]]
        if section_defects:
            section_summary = f"По разделу зафиксировано дефектов: {len(section_defects)}."
        elif any(item["is_accessible"] == "Нет" for item in items):
            section_summary = "Часть конструкций недоступна для детального осмотра."
        else:
            section_summary = "При детальном инструментальном контроле существенных дефектов не выявлено."
        detailed_sections.append(
            {
                "number": f"4.3.{section_index}",
                "title": section_title,
                "element_type": element_type,
                "elements": items,
                "defects": section_defects,
                "measurements": section_measurements,
                "summary": section_summary,
            }
        )
        section_index += 1

    methods = sorted(
        {
            item["method"]
            for item in all_measurements
            if item["method"] and item["method"] != "—"
        }
        | {
            getattr(project.work_program, "methods", "")
            if hasattr(project, "work_program")
            else ""
        }
    )
    methods = [item for item in methods if item]

    brief_characteristics_summary = (
        f"{dictionary_name(building_object.object_type_dictionary, building_object.object_type)}, "
        f"год постройки: {display_value(building_object.construction_year)}, "
        f"этажность: {display_value(building_object.floors_count)}, "
        f"конструктивная схема: {dictionary_name(building_object.structural_system_dictionary, building_object.structural_scheme)}, "
        f"основные материалы: {join_nonempty(list(dict.fromkeys(object_materials)))}."
    )

    visual_analysis_text = (
        f"Осмотрено элементов: {len(element_assessments)}. "
        f"Без дефектов: {sum(1 for item in element_assessments if item['defects_found'] == 'Нет')}. "
        f"С дефектами: {sum(1 for item in element_assessments if item['defects_found'] == 'Да')}. "
        f"Недоступно для осмотра: {sum(1 for item in element_assessments if item['is_accessible'] == 'Нет')}."
    )
    detailed_analysis_focus = [item["element_name"] for item in element_assessments if item["defects_found"] == "Да"]
    if detailed_analysis_focus:
        detailed_analysis_text = (
            "Наиболее детально проанализированы элементы с выявленными дефектами: "
            f"{join_nonempty(detailed_analysis_focus)}."
        )
    else:
        detailed_analysis_text = "По результатам детального обследования элементы находятся в работоспособном состоянии."

    final_condition_category = dictionary_name(project.final_condition_category_dictionary, project.final_condition_category)
    conclusions_summary = (
        f"По результатам обследования объект отнесен к категории: {final_condition_category}. "
        f"Основные ограничения: {join_nonempty(restrictions) if restrictions else 'отсутствуют'}."
    )

    technical_documentation_summary = summarize_file_group(
        documentation_files,
        empty_message="Техническая документация и исходные данные не приложены.",
    )
    calculation_summary = summarize_file_group(
        calculation_result_files,
        empty_message="Поверочные расчеты не приложены.",
    )

    environmental_impact = build_environmental_impact(all_defects, element_assessments)

    template_blocks = active_template_blocks(project)
    enabled_block_types = {item["block_type"] for item in template_blocks}
    table_of_contents = []
    if "introduction" in enabled_block_types:
        table_of_contents.extend(
            [
                {"number": "1", "title": "ВВЕДЕНИЕ"},
                {"number": "1.1", "title": "Основание для проведения обследования"},
                {"number": "1.2", "title": "Сведения об организации, проводящей обследование"},
                {"number": "1.3", "title": "Сведения о заказчике"},
                {"number": "1.4", "title": "Сведения об эксплуатирующей организации"},
            ]
        )
    if "object_information" in enabled_block_types:
        table_of_contents.extend(
            [
                {"number": "2", "title": "ИНФОРМАЦИЯ ОБ ОБЪЕКТЕ ТЕХНИЧЕСКОГО ОБСЛЕДОВАНИЯ"},
                {"number": "2.1", "title": "Фотоматериалы объекта"},
            ]
        )
    if "technical_documentation_analysis" in enabled_block_types:
        table_of_contents.append({"number": "3", "title": "АНАЛИЗ ТЕХНИЧЕСКОЙ ДОКУМЕНТАЦИИ"})
    if {"brief_characteristics", "visual_measurement_control", "detailed_instrumental_control", "environmental_impact"} & enabled_block_types:
        table_of_contents.append({"number": "4", "title": "РЕЗУЛЬТАТЫ ВИЗУАЛЬНОГО И ДЕТАЛЬНОГО ТЕХНИЧЕСКОГО ОБСЛЕДОВАНИЯ"})
        if "brief_characteristics" in enabled_block_types:
            table_of_contents.append({"number": "4.1", "title": "Краткая характеристика объекта"})
        if "visual_measurement_control" in enabled_block_types:
            table_of_contents.append({"number": "4.2", "title": "Результаты визуального и измерительного контроля"})
        if "detailed_instrumental_control" in enabled_block_types:
            table_of_contents.append({"number": "4.3", "title": "Результаты детального инструментального контроля"})
            table_of_contents.extend([{"number": item["number"], "title": item["title"]} for item in detailed_sections])
        if "environmental_impact" in enabled_block_types:
            table_of_contents.append({"number": "4.4", "title": "Определение степени влияния внешних воздействий"})
    if "verification_calculations" in enabled_block_types:
        table_of_contents.extend(
            [
                {"number": "5", "title": "РЕЗУЛЬТАТЫ ПОВЕРОЧНЫХ РАСЧЕТОВ"},
                {"number": "5.1", "title": "Данные для выполнения расчетов"},
                {"number": "5.2", "title": "Анализ поверочных расчетов"},
            ]
        )
    if "result_analysis" in enabled_block_types:
        table_of_contents.extend(
            [
                {"number": "6", "title": "АНАЛИЗ РЕЗУЛЬТАТОВ ТЕХНИЧЕСКОГО ОБСЛЕДОВАНИЯ"},
                {"number": "6.1", "title": "Анализ визуального обследования"},
                {"number": "6.2", "title": "Анализ детального обследования"},
            ]
        )
    if "conclusions" in enabled_block_types:
        table_of_contents.append({"number": "7", "title": "ВЫВОДЫ"})
    if "recommendations" in enabled_block_types:
        table_of_contents.append({"number": "8", "title": "РЕКОМЕНДАЦИИ"})
    if "appendices" in enabled_block_types:
        table_of_contents.append({"number": "9", "title": "ПРИЛОЖЕНИЯ"})
        table_of_contents.extend([{"number": group["number"], "title": group["title"]} for group in appendix_groups])

    snapshot = {
        "title_page": {
            "report_title": TECHNICAL_REPORT_TITLE,
            "report_subtitle": TECHNICAL_REPORT_SUBTITLE,
            "object_name": building_object.name,
            "address": building_object.address,
            "project_contract": project.contract_number or "—",
            "generated_for_project_id": str(project.id),
        },
        "template": {
            "id": str(report_template.id) if report_template else None,
            "name": report_template.name if report_template else "Системный шаблон",
            "code": report_template.code if report_template else "system-default",
            "blocks": template_blocks,
        },
        "table_of_contents": table_of_contents,
        "introduction": {
            "basis_for_inspection": make_plain_text(
                project.inspection_reason or "—",
                getattr(project.technical_task, "execution_basis", "") if hasattr(project, "technical_task") else "",
            ),
            "inspection_organization": inspection_organization,
            "customer": project.customer_name or "—",
            "operating_organization": building_object.owner_name or project.customer_name or "—",
        },
        "object_information": {
            "name": building_object.name,
            "address": building_object.address,
            "object_type": dictionary_name(building_object.object_type_dictionary, building_object.object_type),
            "purpose": building_object.purpose or "—",
            "construction_year": building_object.construction_year or "—",
            "floors_count": building_object.floors_count or "—",
            "area": str(building_object.area) if building_object.area is not None else "—",
            "structural_system": dictionary_name(building_object.structural_system_dictionary, building_object.structural_scheme),
            "main_materials": ", ".join(dict.fromkeys(object_materials)) or "—",
            "overview_photos": object_overview_files,
        },
        "technical_documentation_analysis": {
            "summary": technical_documentation_summary,
            "documents": documentation_files,
        },
        "survey_results": {
            "brief_characteristics": {
                "summary": brief_characteristics_summary,
                "constructive_characteristics": dict(constructive_characteristics),
            },
            "visual_and_measurement_control": {
                "summary": visual_analysis_text,
                "elements": element_assessments,
                "defects": all_defects,
                "measurements": all_measurements,
            },
            "detailed_instrumental_control": {
                "summary": detailed_analysis_text,
                "sections": detailed_sections,
            },
            "environmental_impact_assessment": environmental_impact,
        },
        "verification_calculations": {
            "input_data": calculation_input_files,
            "input_data_summary": summarize_file_group(
                calculation_input_files,
                empty_message="Исходные данные для расчетов не приложены.",
            ),
            "analysis": calculation_summary,
            "calculation_files": calculation_result_files,
        },
        "result_analysis": {
            "visual_analysis": visual_analysis_text,
            "detailed_analysis": detailed_analysis_text,
        },
        "conclusions": {
            "final_condition_category": final_condition_category,
            "summary": conclusions_summary,
            "restrictions": restrictions,
            "need_for_monitoring": needs_monitoring,
            "need_for_additional_inspection": needs_additional_inspection,
        },
        "recommendations_section": {
            "items": unique_recommendations,
            "summary": join_nonempty(unique_recommendations, "; "),
        },
        "appendices": {
            "summary": summarize_file_group(project_file_entries, empty_message="Приложения не приложены."),
            "groups": appendix_groups,
            "project_files_count": len(project_file_entries),
            "photo_groups_count": {
                "object": len(object_overview_files),
                "element": sum(len(value) for value in files_by_element.values()),
                "defect": len(defect_closeup_files),
                "measurement": len(measurement_evidence_files),
            },
        },
        "general_information": {
            "name": building_object.name,
            "address": building_object.address,
            "object_type": dictionary_name(building_object.object_type_dictionary, building_object.object_type),
            "purpose": building_object.purpose or "—",
            "construction_year": building_object.construction_year or "—",
            "floors_count": building_object.floors_count or "—",
            "area": str(building_object.area) if building_object.area is not None else "—",
            "structural_system": dictionary_name(building_object.structural_system_dictionary, building_object.structural_scheme),
            "main_materials": ", ".join(dict.fromkeys(object_materials)) or "—",
        },
        "basis_and_purpose": {
            "inspection_basis": project.inspection_reason or "—",
            "inspection_goal": project.inspection_goal or "—",
            "technical_task": {
                "execution_basis": getattr(project.technical_task, "execution_basis", "—") if hasattr(project, "technical_task") else "—",
                "survey_goal": getattr(project.technical_task, "survey_goal", "—") if hasattr(project, "technical_task") else "—",
                "building_parts": getattr(project.technical_task, "building_parts", "—") if hasattr(project, "technical_task") else "—",
                "engineering_systems": getattr(project.technical_task, "engineering_systems", "—") if hasattr(project, "technical_task") else "—",
                "required_methods": getattr(project.technical_task, "required_methods", "—") if hasattr(project, "technical_task") else "—",
                "result_requirements": getattr(project.technical_task, "result_requirements", "—") if hasattr(project, "technical_task") else "—",
            },
        },
        "inspection_type_and_methods": {
            "inspection_type": dictionary_name(project.inspection_type_dictionary, project.inspection_type),
            "responsible_engineer": responsible_engineer.full_name if responsible_engineer else "—",
            "expert": expert.full_name if expert else "—",
            "inspection_start_date": serialize_date(project.start_date) or "—",
            "inspection_end_date": serialize_date(project.end_date) or "—",
            "project_status": translate_project_status(project.status),
            "methods": methods,
        },
        "work_program": {
            "structures": getattr(project.work_program, "structures", "—") if hasattr(project, "work_program") else "—",
            "zones": getattr(project.work_program, "zones", "—") if hasattr(project, "work_program") else "—",
            "methods": getattr(project.work_program, "methods", "—") if hasattr(project, "work_program") else "—",
            "tools_and_devices": getattr(project.work_program, "tools_and_devices", "—") if hasattr(project, "work_program") else "—",
            "measurements": getattr(project.work_program, "measurements", "—") if hasattr(project, "work_program") else "—",
            "photo_requirements": getattr(project.work_program, "photo_requirements", "—") if hasattr(project, "work_program") else "—",
            "responsible_executors": getattr(project.work_program, "responsible_executors", "—") if hasattr(project, "work_program") else "—",
            "completeness_checklist": getattr(project.work_program, "completeness_checklist", []) if hasattr(project, "work_program") else [],
        },
        "constructive_characteristics": dict(constructive_characteristics),
        "element_assessments": element_assessments,
        "defect_register": all_defects,
        "measurements": all_measurements,
        "photo_appendix": {
            "object_overview_photos": object_overview_files,
            "element_overview_photos": [item for values in files_by_element.values() for item in values],
            "defect_closeup_photos": defect_closeup_files,
            "measurement_evidence_photos": measurement_evidence_files,
            "other_project_files": project_file_entries,
        },
        "technical_condition_assessment": {
            "final_condition_category": final_condition_category,
            "elements_without_defects": sum(1 for item in element_assessments if item["defects_found"] == "Нет"),
            "elements_with_defects": sum(1 for item in element_assessments if item["defects_found"] == "Да"),
            "elements_not_accessible": sum(1 for item in element_assessments if item["is_accessible"] == "Нет"),
        },
        "final_conclusion": {
            "final_condition_category": final_condition_category,
            "restrictions": restrictions,
            "recommendations": unique_recommendations,
            "need_for_monitoring": needs_monitoring,
            "need_for_additional_inspection": needs_additional_inspection,
        },
        "snapshot_meta": {
            "project_id": str(project.id),
            "project_status": project.status,
            "generated_source": "inspection_project",
            "generated_from_data_at": serialize_datetime(timezone.now()),
            "report_kind": "technical_report",
        },
    }
    return snapshot


def build_passport_data(project):
    return build_report_snapshot(project)


def _page_break_xml() -> str:
    return "<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>"


def _paragraph_xml(text: str, *, style: str | None = None) -> str:
    safe_text = escape(text or "")
    style_xml = f"<w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>" if style else ""
    return f"<w:p>{style_xml}<w:r><w:t xml:space=\"preserve\">{safe_text}</w:t></w:r></w:p>"


def _table_cell_xml(text: str) -> str:
    return (
        "<w:tc><w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>"
        f"{_paragraph_xml(text)}</w:tc>"
    )


def _table_row_xml(values: list[str]) -> str:
    return "<w:tr>" + "".join(_table_cell_xml(display_value(value)) for value in values) + "</w:tr>"


def _table_xml(headers: list[str], rows: list[list[str]]) -> str:
    table_props = (
        "<w:tblPr>"
        "<w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:left w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:right w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "</w:tblBorders>"
        "</w:tblPr>"
    )
    header_row = _table_row_xml(headers)
    body_rows = "".join(_table_row_xml(row) for row in rows) or _table_row_xml(["—"] * len(headers))
    return f"<w:tbl>{table_props}{header_row}{body_rows}</w:tbl>"


def _list_paragraphs(items: list[str]) -> str:
    if not items:
        return _paragraph_xml("—")
    return "".join(_paragraph_xml(item) for item in items)


def _files_rows(entries: list[dict]) -> list[list[str]]:
    return [
        [
            entry["original_name"],
            entry.get("caption") or "—",
            entry.get("appendix_type_display") or "—",
            entry.get("url") or "—",
        ]
        for entry in entries
    ]


def _snapshot_template_blocks(snapshot: dict) -> list[dict]:
    blocks = snapshot.get("template", {}).get("blocks", [])
    return blocks or [
        {"block_type": block_type, "title": title}
        for block_type, title in REPORT_TEMPLATE_BLOCK_CHOICES
    ]


def _build_document_xml(snapshot: dict) -> str:
    title_page = snapshot["title_page"]
    introduction = snapshot["introduction"]
    object_information = snapshot["object_information"]
    technical_documentation_analysis = snapshot["technical_documentation_analysis"]
    survey_results = snapshot["survey_results"]
    verification_calculations = snapshot["verification_calculations"]
    result_analysis = snapshot["result_analysis"]
    conclusions = snapshot["conclusions"]
    recommendations_section = snapshot["recommendations_section"]
    appendices = snapshot["appendices"]
    inspection_info = snapshot["inspection_type_and_methods"]

    body_parts = []
    for block in _snapshot_template_blocks(snapshot):
        block_type = block["block_type"]
        title = block.get("title") or resolve_block_title(block_type)
        if block_type == "title_page":
            body_parts.extend(
                [
                    _paragraph_xml(title_page["report_title"], style="Heading1"),
                    _paragraph_xml(title_page["report_subtitle"]),
                    _paragraph_xml(title_page["object_name"], style="Heading2"),
                    _paragraph_xml(f"Адрес: {title_page['address']}"),
                    _paragraph_xml(f"Проект / договор: {title_page['project_contract']}"),
                    _page_break_xml(),
                ]
            )
        elif block_type == "table_of_contents":
            body_parts.append(_paragraph_xml(title.upper(), style="Heading1"))
            body_parts.extend([_paragraph_xml(f"{item['number']} {item['title']}") for item in snapshot["table_of_contents"]])
            body_parts.append(_page_break_xml())
        elif block_type == "introduction":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading1"),
                    _paragraph_xml("1.1 Основание для проведения обследования", style="Heading2"),
                    _paragraph_xml(introduction["basis_for_inspection"]),
                    _paragraph_xml("1.2 Сведения об организации, проводящей обследование", style="Heading2"),
                    _paragraph_xml(introduction["inspection_organization"]),
                    _paragraph_xml("1.3 Сведения о заказчике", style="Heading2"),
                    _paragraph_xml(introduction["customer"]),
                    _paragraph_xml("1.4 Сведения об эксплуатирующей организации", style="Heading2"),
                    _paragraph_xml(introduction["operating_organization"]),
                ]
            )
        elif block_type == "inspection_information":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading1"),
                    _table_xml(
                        ["Параметр обследования", "Значение"],
                        [
                            ["Вид обследования", inspection_info["inspection_type"]],
                            ["Ответственный инженер", inspection_info["responsible_engineer"]],
                            ["Эксперт", inspection_info["expert"]],
                            ["Дата начала", inspection_info["inspection_start_date"]],
                            ["Дата окончания", inspection_info["inspection_end_date"]],
                            ["Статус проекта", inspection_info["project_status"]],
                            ["Методы", join_nonempty(inspection_info["methods"])],
                        ],
                    ),
                ]
            )
        elif block_type == "object_information":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading1"),
                    _table_xml(
                        ["Поле", "Значение"],
                        [
                            ["Наименование", object_information["name"]],
                            ["Адрес", object_information["address"]],
                            ["Тип объекта", object_information["object_type"]],
                            ["Назначение", object_information["purpose"]],
                            ["Год постройки", object_information["construction_year"]],
                            ["Этажность", object_information["floors_count"]],
                            ["Площадь", object_information["area"]],
                            ["Конструктивная схема", object_information["structural_system"]],
                            ["Основные материалы", object_information["main_materials"]],
                        ],
                    ),
                    _paragraph_xml("2.1 Фотоматериалы объекта", style="Heading2"),
                    _table_xml(["Файл", "Подпись", "Тип", "Ссылка"], _files_rows(object_information["overview_photos"])),
                ]
            )
        elif block_type == "technical_documentation_analysis":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading1"),
                    _paragraph_xml(technical_documentation_analysis["summary"]),
                    _table_xml(["Файл", "Подпись", "Тип", "Ссылка"], _files_rows(technical_documentation_analysis["documents"])),
                ]
            )
        elif block_type == "brief_characteristics":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading2"),
                    _paragraph_xml(survey_results["brief_characteristics"]["summary"]),
                    _table_xml(
                        ["Тип элемента", "Характеристики"],
                        [
                            [
                                element_type,
                                "; ".join(f"{item['name']} ({item['location']}, {item['material']})" for item in characteristics),
                            ]
                            for element_type, characteristics in survey_results["brief_characteristics"]["constructive_characteristics"].items()
                        ],
                    ),
                ]
            )
        elif block_type == "visual_measurement_control":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading2"),
                    _paragraph_xml(survey_results["visual_and_measurement_control"]["summary"]),
                    _table_xml(
                        ["Тип", "Элемент", "Расположение", "Материал", "Статус", "Категория", "Дефекты", "Рекомендация"],
                        [
                            [
                                item["element_type"],
                                item["element_name"],
                                item["location"],
                                item["material"],
                                item["inspection_status"],
                                item["condition_category"],
                                item["defects_found"],
                                item["recommendation"],
                            ]
                            for item in survey_results["visual_and_measurement_control"]["elements"]
                        ],
                    ),
                    _paragraph_xml("Выявленные дефекты", style="Heading2"),
                    _table_xml(
                        ["Элемент", "Тип дефекта", "Описание", "Категория", "Рекомендация"],
                        [
                            [item["related_element"], item["defect_type"], item["description"], item["condition_category"], item["recommendation"]]
                            for item in survey_results["visual_and_measurement_control"]["defects"]
                        ],
                    ),
                    _paragraph_xml("Результаты измерений", style="Heading2"),
                    _table_xml(
                        ["Элемент", "Дефект", "Тип измерения", "Значение", "Прибор", "Метод", "Место"],
                        [
                            [
                                item["related_element"],
                                item["related_defect"] or "—",
                                item["measurement_type"],
                                f"{item['value']} {item['unit']}",
                                item["device"],
                                item["method"],
                                item["location"],
                            ]
                            for item in survey_results["visual_and_measurement_control"]["measurements"]
                        ],
                    ),
                ]
            )
        elif block_type == "detailed_instrumental_control":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading2"),
                    _paragraph_xml(survey_results["detailed_instrumental_control"]["summary"]),
                ]
            )
            for section in survey_results["detailed_instrumental_control"]["sections"]:
                body_parts.extend(
                    [
                        _paragraph_xml(f"{section['number']} {section['title']}", style="Heading3"),
                        _paragraph_xml(section["summary"]),
                        _table_xml(
                            ["Элемент", "Расположение", "Категория", "Вывод", "Фото"],
                            [
                                [
                                    item["element_name"],
                                    item["location"],
                                    item["condition_category"],
                                    item["conclusion"],
                                    join_nonempty([file_item["original_name"] for file_item in item["linked_photos"]], "; "),
                                ]
                                for item in section["elements"]
                            ],
                        ),
                    ]
                )
        elif block_type == "environmental_impact":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading2"),
                    _paragraph_xml(survey_results["environmental_impact_assessment"]["summary"]),
                    _table_xml(["Фактор", "Вывод"], [[item["title"], item["finding"]] for item in survey_results["environmental_impact_assessment"]["factors"]]),
                ]
            )
        elif block_type == "verification_calculations":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading1"),
                    _paragraph_xml("5.1 Данные для выполнения расчетов", style="Heading2"),
                    _paragraph_xml(verification_calculations["input_data_summary"]),
                    _table_xml(["Файл", "Подпись", "Тип", "Ссылка"], _files_rows(verification_calculations["input_data"])),
                    _paragraph_xml("5.2 Анализ поверочных расчетов", style="Heading2"),
                    _paragraph_xml(verification_calculations["analysis"]),
                    _table_xml(["Файл", "Подпись", "Тип", "Ссылка"], _files_rows(verification_calculations["calculation_files"])),
                ]
            )
        elif block_type == "result_analysis":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading1"),
                    _paragraph_xml("6.1 Анализ визуального обследования", style="Heading2"),
                    _paragraph_xml(result_analysis["visual_analysis"]),
                    _paragraph_xml("6.2 Анализ детального обследования", style="Heading2"),
                    _paragraph_xml(result_analysis["detailed_analysis"]),
                ]
            )
        elif block_type == "conclusions":
            body_parts.extend(
                [
                    _paragraph_xml(title, style="Heading1"),
                    _paragraph_xml(conclusions["summary"]),
                    _table_xml(
                        ["Показатель", "Значение"],
                        [
                            ["Итоговая категория", conclusions["final_condition_category"]],
                            ["Ограничения", join_nonempty(conclusions["restrictions"]) if conclusions["restrictions"] else "отсутствуют"],
                            ["Необходимость мониторинга", "Да" if conclusions["need_for_monitoring"] else "Нет"],
                            ["Необходимость дополнительного обследования", "Да" if conclusions["need_for_additional_inspection"] else "Нет"],
                        ],
                    ),
                ]
            )
        elif block_type == "recommendations":
            body_parts.extend([_paragraph_xml(title, style="Heading1"), _list_paragraphs(recommendations_section["items"])])
        elif block_type == "appendices":
            body_parts.extend([_paragraph_xml(title, style="Heading1"), _paragraph_xml(appendices["summary"])])
            for group in appendices["groups"]:
                body_parts.extend(
                    [
                        _paragraph_xml(f"{group['number']} {group['title']}", style="Heading2"),
                        _table_xml(["Файл", "Подпись", "Тип", "Ссылка"], _files_rows(group["files"])),
                    ]
                )

    body = "".join(body_parts)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:wpc=\"http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas\" "
        "xmlns:mc=\"http://schemas.openxmlformats.org/markup-compatibility/2006\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:m=\"http://schemas.openxmlformats.org/officeDocument/2006/math\" "
        "xmlns:v=\"urn:schemas-microsoft-com:vml\" "
        "xmlns:wp14=\"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\" "
        "xmlns:w10=\"urn:schemas-microsoft-com:office:word\" "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\" "
        "xmlns:w14=\"http://schemas.microsoft.com/office/word/2010/wordml\" "
        "xmlns:w15=\"http://schemas.microsoft.com/office/word/2012/wordml\" "
        "xmlns:wpg=\"http://schemas.microsoft.com/office/word/2010/wordprocessingGroup\" "
        "xmlns:wpi=\"http://schemas.microsoft.com/office/word/2010/wordprocessingInk\" "
        "xmlns:wne=\"http://schemas.microsoft.com/office/2006/wordml\" "
        "xmlns:wps=\"http://schemas.microsoft.com/office/word/2010/wordprocessingShape\" "
        "mc:Ignorable=\"w14 w15 wp14\">"
        f"<w:body>{body}<w:sectPr><w:pgSz w:w=\"11906\" w:h=\"16838\" />"
        "<w:pgMar w:top=\"1080\" w:right=\"720\" w:bottom=\"1080\" w:left=\"720\" "
        "w:header=\"708\" w:footer=\"708\" w:gutter=\"0\" /></w:sectPr></w:body></w:document>"
    )


def generate_docx_bytes(snapshot: dict) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>""",
        )
        archive.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""",
        )
        archive.writestr(
            "word/_rels/document.xml.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>""",
        )
        archive.writestr(
            "word/styles.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="26"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="22"/></w:rPr>
  </w:style>
</w:styles>""",
        )
        archive.writestr("word/document.xml", _build_document_xml(snapshot))
    return buffer.getvalue()


def build_report_lines(snapshot: dict) -> list[str]:
    lines = [
        snapshot["title_page"]["report_title"],
        snapshot["title_page"]["report_subtitle"],
        snapshot["title_page"]["object_name"],
        "",
        "СОДЕРЖАНИЕ",
    ]
    lines.extend(
        f"{item['number']} {item['title']}"
        for item in snapshot["table_of_contents"]
    )
    lines.extend(
        [
            "",
            "1. ВВЕДЕНИЕ",
            f"1.1 Основание: {display_value(snapshot['introduction']['basis_for_inspection'])}",
            f"1.2 Организация: {display_value(snapshot['introduction']['inspection_organization'])}",
            f"1.3 Заказчик: {display_value(snapshot['introduction']['customer'])}",
            f"1.4 Эксплуатирующая организация: {display_value(snapshot['introduction']['operating_organization'])}",
            f"Вид обследования: {display_value(snapshot['inspection_type_and_methods']['inspection_type'])}",
            f"Ответственный инженер: {display_value(snapshot['inspection_type_and_methods']['responsible_engineer'])}",
            f"Эксперт: {display_value(snapshot['inspection_type_and_methods']['expert'])}",
            "",
            "2. ИНФОРМАЦИЯ ОБ ОБЪЕКТЕ ТЕХНИЧЕСКОГО ОБСЛЕДОВАНИЯ",
        ]
    )
    lines.extend(f"{key}: {display_value(value)}" for key, value in snapshot["general_information"].items())
    lines.extend(
        [
            "",
            "3. АНАЛИЗ ТЕХНИЧЕСКОЙ ДОКУМЕНТАЦИИ",
            snapshot["technical_documentation_analysis"]["summary"],
            "",
            "4. РЕЗУЛЬТАТЫ ВИЗУАЛЬНОГО И ДЕТАЛЬНОГО ТЕХНИЧЕСКОГО ОБСЛЕДОВАНИЯ",
            snapshot["survey_results"]["visual_and_measurement_control"]["summary"],
        ]
    )
    for item in snapshot["element_assessments"]:
        lines.append(
            f"{item['element_type']} / {item['element_name']} / {item['location']} / "
            f"Статус: {item['inspection_status']} / Категория: {item['condition_category']} / Дефекты: {item['defects_found']}"
        )
    lines.extend(["", "4.3 Детальный инструментальный контроль"])
    for section in snapshot["survey_results"]["detailed_instrumental_control"]["sections"]:
        lines.append(f"{section['number']} {section['title']}: {section['summary']}")
    lines.extend(["", "4.4 Внешние воздействия"])
    lines.append(snapshot["survey_results"]["environmental_impact_assessment"]["summary"])
    lines.extend(["", "5. РЕЗУЛЬТАТЫ ПОВЕРОЧНЫХ РАСЧЕТОВ"])
    lines.append(snapshot["verification_calculations"]["input_data_summary"])
    lines.append(snapshot["verification_calculations"]["analysis"])
    lines.extend(["", "6. АНАЛИЗ РЕЗУЛЬТАТОВ ТЕХНИЧЕСКОГО ОБСЛЕДОВАНИЯ"])
    lines.append(snapshot["result_analysis"]["visual_analysis"])
    lines.append(snapshot["result_analysis"]["detailed_analysis"])
    lines.extend(["", "7. ВЫВОДЫ"])
    lines.append(snapshot["conclusions"]["summary"])
    lines.extend(["", "8. РЕКОМЕНДАЦИИ"])
    lines.extend(snapshot["recommendations_section"]["items"] or ["Рекомендации отсутствуют."])
    lines.extend(["", "9. ПРИЛОЖЕНИЯ"])
    if snapshot["appendices"]["groups"]:
        for group in snapshot["appendices"]["groups"]:
            lines.append(f"{group['number']} {group['title']}")
            lines.extend(f"- {entry['original_name']}" for entry in group["files"])
    else:
        lines.append("Приложения не приложены.")
    return lines


def generate_pdf_bytes(snapshot: dict) -> bytes:
    lines = build_report_lines(snapshot)
    lines_per_page = 38
    pages = [lines[index : index + lines_per_page] for index in range(0, len(lines), lines_per_page)] or [[""]]
    objects: list[bytes] = []
    page_object_numbers = []
    font_object_number = 3 + len(pages) * 2

    def add_object(payload: str | bytes) -> int:
        obj_number = len(objects) + 1
        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
        objects.append(f"{obj_number} 0 obj\n".encode("ascii") + payload_bytes + b"\nendobj\n")
        return obj_number

    add_object("<< /Type /Catalog /Pages 2 0 R >>")
    add_object("<< /Type /Pages /Kids [] /Count 0 >>")
    kids_refs = []

    for page_lines in pages:
        commands = ["BT", "/F1 10 Tf", "40 800 Td", "14 TL"]
        first = True
        for line in page_lines:
            safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if first:
                commands.append(f"({safe_line}) Tj")
                first = False
            else:
                commands.append(f"T* ({safe_line}) Tj")
        commands.append("ET")
        stream = "\n".join(commands).encode("utf-8")
        content_object_number = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
        )
        page_object_number = add_object(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_object_number} 0 R >> >> "
            f"/Contents {content_object_number} 0 R >>"
        )
        page_object_numbers.append(page_object_number)
        kids_refs.append(f"{page_object_number} 0 R")

    add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects[1] = (
        b"2 0 obj\n<< /Type /Pages /Kids ["
        + " ".join(kids_refs).encode("ascii")
        + b"] /Count "
        + str(len(page_object_numbers)).encode("ascii")
        + b" >>\nendobj\n"
    )

    pdf = BytesIO()
    pdf.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(pdf.tell())
        pdf.write(obj)
    xref_position = pdf.tell()
    pdf.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_position}\n%%EOF".encode("ascii")
    )
    return pdf.getvalue()


def get_or_create_working_report(project, user, title: str) -> Report:
    latest_report = project.reports.order_by("-version", "-created_at").first()
    if latest_report and latest_report.status != Report.Status.APPROVED:
        if latest_report.status == Report.Status.ARCHIVED:
            latest_report = None
        else:
            latest_report.title = title
            latest_report.generated_by = user
            latest_report.summary = "Полный технический отчет сформирован на основе данных проекта обследования."
            latest_report.save(update_fields=["title", "generated_by", "summary", "updated_at"])
            return latest_report

    version = (project.reports.aggregate(max_version=Max("version"))["max_version"] or 0) + 1
    return Report.objects.create(
        project=project,
        version=version,
        status=Report.Status.DRAFT,
        title=title,
        summary="Полный технический отчет сформирован на основе данных проекта обследования.",
        generated_by=user,
    )


def update_report_snapshot(report: Report, *, snapshot: dict, generated_by) -> Report:
    report.json_snapshot = snapshot
    report.generated_by = generated_by
    report.generated_at = timezone.now()
    report.status = Report.Status.GENERATED
    report.summary = "Полный технический отчет сформирован на основе данных проекта обследования."
    report.save(update_fields=["json_snapshot", "generated_by", "generated_at", "status", "summary", "updated_at"])
    return report


def attach_generated_report_file(report: Report, *, file_format: str, content: bytes) -> Report:
    stem = f"technical_report_{report.project_id}_v{report.version}"
    filename = f"{stem}.{file_format}"
    content_file = ContentFile(content, name=filename)
    if file_format == "docx":
        if report.docx_file:
            report.docx_file.delete(save=False)
        report.docx_file.save(filename, content_file, save=False)
        update_fields = ["docx_file", "updated_at"]
    else:
        if report.pdf_file:
            report.pdf_file.delete(save=False)
        report.pdf_file.save(filename, content_file, save=False)
        update_fields = ["pdf_file", "updated_at"]
    report.save(update_fields=update_fields)
    return report
