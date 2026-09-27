from __future__ import annotations

import shutil
import tempfile
from io import BytesIO
from zipfile import ZipFile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.defects.models import Defect
from apps.elements.models import StructuralElement
from apps.files.models import InspectionFile
from apps.inspections.models import InspectionProject, TechnicalTask, WorkProgram
from apps.measurements.models import Measurement
from apps.objects.models import BuildingObject
from apps.reports.models import Report
from apps.users.models import User

TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="inspectionpro-report-tests-")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ReportGenerationPipelineTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.engineer = User.objects.create_user(
            email="engineer-report@example.com",
            password="Password123!",
            full_name="Engineer Report",
            role=User.Role.ENGINEER,
        )
        self.expert = User.objects.create_user(
            email="expert-report@example.com",
            password="Password123!",
            full_name="Expert Report",
            role=User.Role.EXPERT,
        )
        self.client_user = User.objects.create_user(
            email="client-report@example.com",
            password="Password123!",
            full_name="Client Report",
            role=User.Role.CLIENT,
        )
        self.building_object = BuildingObject.objects.create(
            name="Industrial Test Building",
            address="г. Екатеринбург, ул. Заводская, 7",
            object_type="Производственное здание",
            purpose="Производственный корпус",
            construction_year=2018,
            floors_count=2,
            area="2400.00",
            created_by=self.engineer,
        )
        self.project = InspectionProject.objects.create(
            building_object=self.building_object,
            customer_name="Factory Customer",
            contract_number="REP-2026-001",
            inspection_reason="Комплексное обследование перед ремонтом",
            inspection_goal="Проверка пайплайна отчётности",
            inspection_type="Комплексное обследование",
            start_date="2026-05-24",
            end_date="2026-05-31",
            responsible_engineer=self.engineer,
            status=InspectionProject.Status.APPROVED,
            final_condition_category="Ограниченно-работоспособное",
            created_by=self.engineer,
        )
        self.project.team.set([self.engineer, self.expert])
        TechnicalTask.objects.create(
            project=self.project,
            execution_basis="Договор REP-2026-001",
            survey_goal="Комплексное обследование объекта",
            building_parts="Фундаменты, колонны",
            engineering_systems="Электроснабжение",
            required_methods="Визуальное обследование, инструментальное измерение",
            result_requirements="Паспорт здания и отчёт",
        )
        WorkProgram.objects.create(
            project=self.project,
            structures="Фундаменты и колонны",
            zones="Подвал и 1 этаж",
            methods="Визуальное обследование и инструментальные измерения",
            tools_and_devices="Рулетка, трещиномер",
            measurements="Ширина раскрытия трещин",
            photo_requirements="Обзорные и детальные фото",
            responsible_executors="Инженер, эксперт",
        )
        self.foundation = StructuralElement.objects.create(
            project=self.project,
            building_object=self.building_object,
            element_type="Фундаменты",
            name="Фундаменты",
            location="Подвал",
            floor="Подвал",
            material="Монолитный железобетон",
            visual_condition="удовлетворительное",
            has_defects=False,
            no_defects_comment="Дефекты не выявлены",
            condition_category="Работоспособное",
            conclusion="Эксплуатация возможна",
        )
        self.column = StructuralElement.objects.create(
            project=self.project,
            building_object=self.building_object,
            element_type="Колонны",
            name="Колонна К1",
            location="1 этаж, ось А-1",
            floor="1 этаж",
            axes="А-1",
            material="Монолитный железобетон",
            visual_condition="локальные повреждения",
            has_defects=True,
            condition_category="Ограниченно-работоспособное",
            conclusion="Требуется локальный ремонт и наблюдение",
        )
        self.defect = Defect.objects.create(
            project=self.project,
            building_object=self.building_object,
            structural_element=self.column,
            defect_type="Трещина",
            title="Трещина в колонне",
            description="Выявлена трещина в защитном слое колонны",
            location="1 этаж",
            floor="1 этаж",
            size_value="0.4",
            size_unit="мм",
            severity="Умеренный",
            probable_cause="Усадочные процессы",
            influence_on_condition="Снижает долговечность конструкции",
            final_condition_category="Ограниченно-работоспособное",
            recommendation="Требуется наблюдение в динамике",
            status="Confirmed",
            created_by=self.engineer,
        )
        self.measurement = Measurement.objects.create(
            project=self.project,
            structural_element=self.column,
            defect=self.defect,
            measurement_type="Ширина раскрытия трещины",
            value="0.400",
            unit="мм",
            device="Трещиномер",
            method="Инструментальное измерение",
            location="1 этаж",
            measured_at=timezone.now(),
            engineer=self.engineer,
            comment="Контрольный замер",
        )
        self._create_file(category=InspectionFile.Category.OBJECT, caption="Обзорное фото объекта")
        self._create_file(category=InspectionFile.Category.ELEMENT, element=self.foundation, caption="Обзорное фото фундамента")
        self._create_file(category=InspectionFile.Category.DEFECT, element=self.column, defect=self.defect, caption="Фото дефекта колонны")
        self._create_file(
            category=InspectionFile.Category.PROJECT,
            caption="Техническое задание",
            appendix_type=InspectionFile.AppendixType.TECHNICAL_TASK,
            original_name="technical-task.pdf",
        )
        self._create_file(
            category=InspectionFile.Category.PROJECT,
            caption="Программа работ",
            appendix_type=InspectionFile.AppendixType.WORK_PROGRAM,
            original_name="work-program.pdf",
        )
        self._create_file(
            category=InspectionFile.Category.PROJECT,
            caption="Поверочные расчеты",
            appendix_type=InspectionFile.AppendixType.CALCULATION,
            original_name="calculation.pdf",
        )

    def _create_file(self, *, category, element=None, defect=None, measurement=None, caption="Фото", appendix_type="", original_name="photo.jpg"):
        uploaded = SimpleUploadedFile(original_name, b"fake-file-bytes", content_type="application/octet-stream")
        return InspectionFile.objects.create(
            file=uploaded,
            original_name=uploaded.name,
            content_type="application/octet-stream",
            size=uploaded.size,
            caption=caption,
            is_for_report=True,
            category=category,
            appendix_type=appendix_type,
            building_object=self.building_object,
            project=self.project,
            structural_element=element,
            defect=defect,
            measurement=measurement,
            uploaded_by=self.engineer,
        )

    def test_generates_docx_snapshot_and_client_can_download_only_after_approval(self):
        self.client.force_authenticate(self.engineer)
        generate_response = self.client.post(
            f"/api/projects/{self.project.id}/reports/generate/",
            {"file_format": "docx"},
            format="json",
        )
        self.assertEqual(generate_response.status_code, 200)
        report = Report.objects.get(id=generate_response.data["id"])
        self.assertEqual(report.status, Report.Status.GENERATED)
        self.assertTrue(bool(report.docx_file))
        self.assertTrue(bool(report.json_snapshot))
        self.assertEqual(report.json_snapshot["title_page"]["report_title"], "ТЕХНИЧЕСКИЙ ОТЧЕТ")
        self.assertEqual(len(report.json_snapshot["element_assessments"]), 2)
        self.assertEqual(report.json_snapshot["defect_register"][0]["title"], "Трещина в колонне")
        self.assertEqual(report.json_snapshot["measurements"][0]["value"], "0.400")
        self.assertTrue(bool(report.json_snapshot["technical_documentation_analysis"]["documents"]))
        self.assertTrue(bool(report.json_snapshot["appendices"]["groups"]))

        with ZipFile(BytesIO(report.docx_file.read()), "r") as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")
        self.assertIn("ТЕХНИЧЕСКИЙ ОТЧЕТ", document_xml)
        self.assertIn("Industrial Test Building", document_xml)
        self.assertIn("1. ВВЕДЕНИЕ", document_xml)
        self.assertIn("5. РЕЗУЛЬТАТЫ ПОВЕРОЧНЫХ РАСЧЕТОВ", document_xml)
        self.assertIn("Фундаменты", document_xml)
        self.assertIn("Колонна К1", document_xml)
        self.assertIn("Трещина в колонне", document_xml)
        self.assertIn("0.400 мм", document_xml)
        self.assertIn("technical-task.pdf", document_xml)
        self.assertIn("calculation.pdf", document_xml)

        self.client.force_authenticate(self.client_user)
        client_before_approval = self.client.get(f"/api/reports/{report.id}/")
        self.assertEqual(client_before_approval.status_code, 404)

        self.client.force_authenticate(self.expert)
        approve_response = self.client.post(f"/api/reports/{report.id}/approve/")
        self.assertEqual(approve_response.status_code, 200)
        report.refresh_from_db()
        self.assertEqual(report.status, Report.Status.APPROVED)

        self.client.force_authenticate(self.client_user)
        client_after_approval = self.client.get(f"/api/reports/{report.id}/")
        self.assertEqual(client_after_approval.status_code, 200)
        download_response = self.client.get(f"/api/reports/{report.id}/download-docx/")
        self.assertEqual(download_response.status_code, 200)

    def test_client_passport_uses_latest_approved_report_only(self):
        self.client.force_authenticate(self.engineer)
        approved_generate_response = self.client.post(
            f"/api/projects/{self.project.id}/reports/generate/",
            {"file_format": "docx"},
            format="json",
        )
        approved_report = Report.objects.get(id=approved_generate_response.data["id"])

        self.client.force_authenticate(self.expert)
        approve_response = self.client.post(f"/api/reports/{approved_report.id}/approve/")
        self.assertEqual(approve_response.status_code, 200)

        self.client.force_authenticate(self.engineer)
        generated_draft_response = self.client.post(
            f"/api/projects/{self.project.id}/reports/generate/",
            {"file_format": "docx"},
            format="json",
        )
        generated_report = Report.objects.get(id=generated_draft_response.data["id"])
        self.assertNotEqual(generated_report.id, approved_report.id)
        self.assertEqual(generated_report.status, Report.Status.GENERATED)

        self.client.force_authenticate(self.client_user)
        passport_response = self.client.get(f"/api/projects/{self.project.id}/passport/")
        self.assertEqual(passport_response.status_code, 200)
        self.assertEqual(
            passport_response.data["snapshot_meta"]["generated_from_data_at"],
            approved_report.json_snapshot["snapshot_meta"]["generated_from_data_at"],
        )

        generated_report_response = self.client.get(f"/api/reports/{generated_report.id}/")
        self.assertEqual(generated_report_response.status_code, 404)

    def test_pdf_generation_is_disabled_with_clear_error(self):
        self.client.force_authenticate(self.engineer)
        generate_response = self.client.post(
            f"/api/projects/{self.project.id}/reports/generate/",
            {"file_format": "pdf"},
            format="json",
        )
        self.assertEqual(generate_response.status_code, 400)
        self.assertIn("PDF export is temporarily unavailable", str(generate_response.data))
