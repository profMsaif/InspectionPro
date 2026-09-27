from django.core.management.base import BaseCommand

from apps.defects.models import Defect
from apps.dictionaries.constants import DICTIONARY_SEED_DATA
from apps.dictionaries.models import DictionaryItem
from apps.elements.models import StructuralElement
from apps.files.models import InspectionFile
from apps.inspections.models import InspectionProject, TechnicalTask, WorkProgram
from apps.measurements.models import Measurement
from apps.notifications.models import Notification
from apps.objects.models import BuildingObject
from apps.reports.models import Report
from apps.reports.services import build_report_snapshot, build_report_title
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed demo data for local smoke testing."

    def handle(self, *args, **options):
        users = self._create_users()
        self._create_dictionaries()
        building_object = self._create_building_object(users["manager"])
        project = self._create_project(building_object, users)
        self._create_project_documents(project)
        self._create_elements_with_relations(project, building_object, users["engineer"])
        self._create_report(project, users["expert"])
        self._create_notifications(users)
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def _create_users(self):
        password = "Password123!"
        users_config = [
            ("admin@example.com", "Admin User", User.Role.ADMIN),
            ("manager@example.com", "Manager User", User.Role.MANAGER),
            ("engineer@example.com", "Engineer User", User.Role.ENGINEER),
            ("expert@example.com", "Expert User", User.Role.EXPERT),
            ("client@example.com", "Client User", User.Role.CLIENT),
        ]

        users = {}
        for email, full_name, role in users_config:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": full_name,
                    "role": role,
                    "username": email,
                    "is_active": True,
                },
            )
            user.full_name = full_name
            user.role = role
            user.is_active = True
            user.is_blocked = False
            user.set_password(password)
            if role == User.Role.ADMIN:
                user.is_staff = True
                user.is_superuser = True
            user.save()
            users[role.lower()] = user
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created user {email}"))
        return users

    def _create_dictionaries(self):
        for dictionary_type, items in DICTIONARY_SEED_DATA.items():
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

    def _create_building_object(self, manager):
        object_type = DictionaryItem.objects.get(
            dictionary_type=DictionaryItem.DictionaryType.OBJECT_TYPE,
            code="residential_building",
        )
        structural_system = DictionaryItem.objects.get(
            dictionary_type=DictionaryItem.DictionaryType.STRUCTURAL_SYSTEM,
            code="monolithic_reinforced_concrete",
        )
        material = DictionaryItem.objects.get(
            dictionary_type=DictionaryItem.DictionaryType.MATERIAL,
            code="monolithic_reinforced_concrete",
        )
        building_object, _ = BuildingObject.objects.update_or_create(
            name="ЖК Северный квартал, корпус 1",
            defaults={
                "address": "г. Екатеринбург, ул. Инженерная, 25",
                "cadastral_number": "66:41:0000000:12345",
                "object_type": object_type.name_ru,
                "object_type_dictionary": object_type,
                "purpose": "Многоквартирный жилой дом",
                "construction_year": 2012,
                "floors_count": 16,
                "area": 12540.50,
                "volume": 48210.00,
                "structural_scheme": structural_system.name_ru,
                "structural_system_dictionary": structural_system,
                "main_material_dictionary": material,
                "foundation_material": material.name_ru,
                "wall_material": "Газобетон",
                "floor_material": material.name_ru,
                "roof_material": "Кровельный материал",
                "description": "Демо-объект для smoke test и проверки маршрутов обследования.",
                "owner_name": "ООО СеверСтрой",
                "created_by": manager,
            },
        )
        return building_object

    def _create_project(self, building_object, users):
        inspection_type = DictionaryItem.objects.get(
            dictionary_type=DictionaryItem.DictionaryType.INSPECTION_TYPE,
            code="periodic_inspection",
        )
        condition_category = DictionaryItem.objects.get(
            dictionary_type=DictionaryItem.DictionaryType.CONDITION_CATEGORY,
            code="serviceable",
        )
        project, _ = InspectionProject.objects.update_or_create(
            building_object=building_object,
            customer_name="ООО СеверСтрой",
            contract_number="IP-2026-001",
            defaults={
                "inspection_reason": "Плановое обследование перед капитальным ремонтом.",
                "inspection_goal": "Оценка технического состояния несущих и ограждающих конструкций.",
                "inspection_type": inspection_type.name_ru,
                "inspection_type_dictionary": inspection_type,
                "start_date": "2026-05-20",
                "end_date": "2026-05-31",
                "responsible_engineer": users["engineer"],
                "status": InspectionProject.Status.IN_PROGRESS,
                "final_condition_category": condition_category.name_ru,
                "final_condition_category_dictionary": condition_category,
                "created_by": users["manager"],
            },
        )
        project.team.set([users["manager"], users["engineer"], users["expert"]])
        return project

    def _create_project_documents(self, project):
        TechnicalTask.objects.update_or_create(
            project=project,
            defaults={
                "execution_basis": "Договор IP-2026-001",
                "survey_goal": "Определение категории технического состояния объекта",
                "building_parts": "Фундаменты, стены, колонны, перекрытия, кровля, лестницы, фасады",
                "engineering_systems": "Система водоотведения, отопление",
                "required_methods": "Визуальный осмотр, инструментальные замеры",
                "result_requirements": "Техническое заключение с приложениями",
                "deadlines": "До 31.05.2026",
                "output_documentation": "DOCX, PDF, фото-приложение, ведомость элементов",
            },
        )
        WorkProgram.objects.update_or_create(
            project=project,
            defaults={
                "structures": "Все основные несущие и ограждающие конструкции",
                "zones": "Подвал, 1-16 этажи, кровля, фасад",
                "methods": "Визуальный осмотр, измерение ширины трещин, фотофиксация",
                "tools_and_devices": "Рулетка, штангенциркуль, щуп, влагомер",
                "measurements": "Ширина раскрытия трещин, влажность",
                "photo_requirements": "Обзорные фото для каждого элемента, детальные фото дефектов",
                "responsible_executors": "Инженер-обследователь, эксперт",
                "completeness_checklist": [
                    "Заполнены карточки всех обязательных элементов",
                    "Привязаны фото бездефектных элементов",
                    "Добавлены дефекты и измерения",
                ],
            },
        )
        demo_project_files = [
            ("technical_task.pdf", "Копия технического задания", InspectionFile.AppendixType.TECHNICAL_TASK),
            ("work_program.pdf", "Программа проведения обследования", InspectionFile.AppendixType.WORK_PROGRAM),
            ("source_data.pdf", "Исходные данные", InspectionFile.AppendixType.SOURCE_DATA),
            ("calculation.pdf", "Поверочные расчеты", InspectionFile.AppendixType.CALCULATION),
        ]
        for filename, caption, appendix_type in demo_project_files:
            InspectionFile.objects.update_or_create(
                project=project,
                category=InspectionFile.Category.PROJECT,
                original_name=filename,
                defaults={
                    "file": f"uploads/demo/{filename}",
                    "content_type": "application/pdf",
                    "size": 1024,
                    "caption": caption,
                    "is_for_report": True,
                    "appendix_type": appendix_type,
                    "building_object": project.building_object,
                    "uploaded_by": project.responsible_engineer or project.created_by,
                },
            )

    def _create_elements_with_relations(self, project, building_object, engineer):
        element_types = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.ELEMENT_TYPE)
        }
        materials = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.MATERIAL)
        }
        methods = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.INSPECTION_METHOD)
        }
        conditions = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.CONDITION_CATEGORY)
        }
        statuses = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.ELEMENT_INSPECTION_STATUS)
        }
        recommendations = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.RECOMMENDATION_TYPE)
        }
        defect_types = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.DEFECT_TYPE)
        }
        severities = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.DEFECT_SEVERITY)
        }
        causes = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.DEFECT_CAUSE)
        }
        measurement_types = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.MEASUREMENT_TYPE)
        }
        units = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.MEASUREMENT_UNIT)
        }
        devices = {
            item.code: item
            for item in DictionaryItem.objects.filter(dictionary_type=DictionaryItem.DictionaryType.DEVICE)
        }
        element_specs = [
            ("foundations", "Фундаменты", "Подвал, оси А-Д", False),
            ("bearing_walls", "Несущие стены", "1-16 этажи", False),
            ("columns", "Колонны", "1 этаж, оси Б-Г/2-4", True),
            ("beams", "Балки", "Техэтаж", False),
            ("slabs", "Перекрытия", "2 этаж", False),
            ("coverings", "Покрытия", "Кровля", False),
            ("roof", "Кровля", "Кровля", False),
            ("stairs", "Лестницы", "Секции 1-3", False),
            ("facades", "Фасады", "Северный и восточный фасад", False),
            ("partitions", "Перегородки", "3-8 этажи", False),
            ("floors", "Полы", "Подвал и МОП", False),
        ]

        for index, (element_type_code, name, location, has_defects) in enumerate(element_specs, start=1):
            element_type = element_types[element_type_code]
            material = materials["brick"] if element_type_code == "bearing_walls" else materials["monolithic_reinforced_concrete"]
            inspection_method = methods["visual_inspection"]
            condition = conditions["limited_serviceable"] if has_defects else conditions["serviceable"]
            inspection_status = statuses["inspected_with_defects"] if has_defects else statuses["inspected_no_defects"]
            recommendation = recommendations["routine_repair"] if has_defects else recommendations["repair_not_required"]
            element, _ = StructuralElement.objects.update_or_create(
                project=project,
                name=name,
                defaults={
                    "building_object": building_object,
                    "element_type": element_type.name_ru,
                    "element_type_dictionary": element_type,
                    "location": location,
                    "floor": "various" if index != 3 else "1 этаж",
                    "axes": f"А-{chr(64 + min(index, 5))}",
                    "material": material.name_ru,
                    "material_dictionary": material,
                    "description": f"Демо-оценка элемента: {name}",
                    "is_accessible": True,
                    "inspection_method": inspection_method.name_ru,
                    "inspection_method_dictionary": inspection_method,
                    "visual_condition": "работоспособное",
                    "has_defects": has_defects,
                    "no_defects_comment": "" if has_defects else "Видимых дефектов и повреждений не выявлено",
                    "condition_category": condition.name_ru,
                    "condition_category_dictionary": condition,
                    "inspection_status_dictionary": inspection_status,
                    "conclusion": "Эксплуатация возможна" if not has_defects else "Требуется локальный ремонт и наблюдение",
                    "recommendation": StructuralElement.Recommendation.NOT_REQUIRED if not has_defects else StructuralElement.Recommendation.REPAIR,
                    "recommendation_dictionary": recommendation,
                },
            )

            if not has_defects:
                InspectionFile.objects.update_or_create(
                    project=project,
                    structural_element=element,
                    category=InspectionFile.Category.ELEMENT,
                    original_name=f"{name.lower().replace(' ', '_')}_overview.jpg",
                    defaults={
                        "file": f"uploads/demo/{name.lower().replace(' ', '_')}_overview.jpg",
                        "content_type": "image/jpeg",
                        "size": 1024,
                        "caption": f"Обзорное фото элемента: {name}",
                        "is_for_report": True,
                        "building_object": building_object,
                        "uploaded_by": engineer,
                    },
                )
                continue

            defect, _ = Defect.objects.update_or_create(
                project=project,
                structural_element=element,
                title="Трещины и сколы в защитном слое колонны",
                defaults={
                    "building_object": building_object,
                    "defect_type": defect_types["crack"].name_ru,
                    "defect_type_dictionary": defect_types["crack"],
                    "description": "Выявлены вертикальные трещины и локальные сколы защитного слоя бетона.",
                    "location": location,
                    "floor": "1 этаж",
                    "room": "Вестибюль",
                    "size_value": "2.3",
                    "size_unit": "мм",
                    "severity": severities["moderate"].name_ru,
                    "severity_dictionary": severities["moderate"],
                    "probable_cause": causes["shrinkage"].name_ru,
                    "probable_cause_dictionary": causes["shrinkage"],
                    "influence_on_condition": "Снижает долговечность и требует ремонта",
                    "preliminary_condition_category": conditions["limited_serviceable"].name_ru,
                    "preliminary_condition_category_dictionary": conditions["limited_serviceable"],
                    "final_condition_category": conditions["limited_serviceable"].name_ru,
                    "final_condition_category_dictionary": conditions["limited_serviceable"],
                    "recommendation": recommendations["monitoring"].name_ru,
                    "recommendation_dictionary": recommendations["monitoring"],
                    "status": "Confirmed",
                    "created_by": engineer,
                },
            )
            Measurement.objects.update_or_create(
                project=project,
                structural_element=element,
                defect=defect,
                measurement_type=measurement_types["crack_width"].name_ru,
                defaults={
                    "measurement_type_dictionary": measurement_types["crack_width"],
                    "value": "2.300",
                    "unit": units["mm"].name_ru,
                    "unit_dictionary": units["mm"],
                    "device": devices["feeler_gauge"].name_ru,
                    "device_dictionary": devices["feeler_gauge"],
                    "method": methods["instrumental_measurement"].name_ru,
                    "method_dictionary": methods["instrumental_measurement"],
                    "location": location,
                    "measured_at": "2026-05-22T10:30:00+05:00",
                    "engineer": engineer,
                    "comment": "Максимальная ширина раскрытия по колонне К-3",
                },
            )
            InspectionFile.objects.update_or_create(
                project=project,
                defect=defect,
                structural_element=element,
                category=InspectionFile.Category.DEFECT,
                original_name="column_defect_detail.jpg",
                defaults={
                    "file": "uploads/demo/column_defect_detail.jpg",
                    "content_type": "image/jpeg",
                    "size": 2048,
                    "caption": "Детальное фото дефекта колонны",
                    "is_for_report": True,
                    "building_object": building_object,
                    "uploaded_by": engineer,
                },
            )

    def _create_report(self, project, expert):
        snapshot = build_report_snapshot(project)
        Report.objects.update_or_create(
            project=project,
            version=1,
            defaults={
                "title": build_report_title(project),
                "summary": "Демо-версия отчёта для smoke test.",
                "status": Report.Status.APPROVED,
                "generated_by": expert,
                "generated_at": "2026-05-23T14:30:00+05:00",
                "approved_by": expert,
                "approved_at": "2026-05-23T15:00:00+05:00",
                "json_snapshot": snapshot,
            },
        )

    def _create_notifications(self, users):
        Notification.objects.update_or_create(
            user=users["engineer"],
            title="Назначение на проект",
            defaults={
                "message": "Вы назначены ответственным инженером по проекту IP-2026-001.",
                "is_read": False,
                "action_url": "/projects",
            },
        )
        Notification.objects.update_or_create(
            user=users["expert"],
            title="Проект готов к проверке",
            defaults={
                "message": "Проект IP-2026-001 подготовлен к экспертной проверке.",
                "is_read": False,
                "action_url": "/projects",
            },
        )
