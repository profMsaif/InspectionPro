from __future__ import annotations

from collections import Counter

from rest_framework.exceptions import ValidationError


def _error(section: str, message: str, *, items: list[str] | None = None):
    payload = {
        "section": section,
        "message": message,
    }
    if items:
        payload["items"] = items
    return payload


def collect_project_generation_errors(project) -> list[dict]:
    errors: list[dict] = []

    if not project.building_object_id:
        errors.append(_error("Object", "Project is not linked to an inspection object."))

    if not (project.inspection_type_dictionary_id or project.inspection_type):
        errors.append(_error("Project", "Inspection type is required."))

    has_technical_task = hasattr(project, "technical_task")
    if not has_technical_task and not project.inspection_reason:
        errors.append(_error("Project", "Inspection basis or technical task is required."))

    has_work_program = hasattr(project, "work_program")
    elements = list(project.elements.all().order_by("name"))
    if not has_work_program and not elements:
        errors.append(_error("Work program", "Work program or planned element list is required."))

    if not elements:
        errors.append(_error("Structural elements", "At least one structural element assessment is required."))
        return errors

    missing_condition = [element.name for element in elements if not element.condition_category and not element.condition_category_dictionary_id]
    if missing_condition:
        errors.append(
            _error(
                "Structural elements",
                f"{len(missing_condition)} elements do not have condition category.",
                items=missing_condition[:10],
            )
        )

    missing_status = [element.name for element in elements if not element.inspection_status_dictionary_id and not element.visual_condition]
    if missing_status:
        errors.append(
            _error(
                "Structural elements",
                f"{len(missing_status)} elements do not have inspection status.",
                items=missing_status[:10],
            )
        )

    defects = list(project.defects.select_related("structural_element").all().order_by("created_at"))
    invalid_defects = []
    for defect in defects:
        defect_missing = []
        if not (defect.defect_type_dictionary_id or defect.defect_type):
            defect_missing.append("type")
        if not defect.description:
            defect_missing.append("description")
        if not (defect.recommendation_dictionary_id or defect.recommendation):
            defect_missing.append("recommendation")
        if not (
            defect.final_condition_category_dictionary_id
            or defect.preliminary_condition_category_dictionary_id
            or defect.final_condition_category
            or defect.preliminary_condition_category
        ):
            defect_missing.append("condition_category")
        if defect_missing:
            invalid_defects.append(f"{defect.title} ({', '.join(defect_missing)})")
    if invalid_defects:
        errors.append(
            _error(
                "Defects",
                f"{len(invalid_defects)} defects are incomplete.",
                items=invalid_defects[:10],
            )
        )

    element_defect_relation_issues = []
    for element in elements:
        if element.has_defects and not element.defects.exists():
            element_defect_relation_issues.append(element.name)
    if element_defect_relation_issues:
        errors.append(
            _error(
                "Structural elements",
                "Some elements are marked as defective but have no linked defect records.",
                items=element_defect_relation_issues[:10],
            )
        )

    orphan_measurements = [
        measurement.id
        for measurement in project.measurements.all()
        if not measurement.structural_element_id
    ]
    if orphan_measurements:
        errors.append(
            _error(
                "Measurements",
                "Some measurements are not linked to structural elements.",
                items=[str(item) for item in orphan_measurements[:10]],
            )
        )

    return errors


def validate_project_readiness(project):
    errors = collect_project_generation_errors(project)
    if errors:
        raise ValidationError(
            {
                "can_generate": False,
                "errors": errors,
                "summary": dict(Counter(item["section"] for item in errors)),
            }
        )
