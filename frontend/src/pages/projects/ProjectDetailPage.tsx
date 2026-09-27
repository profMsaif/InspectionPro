import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axios from "axios";

import { useDefectsQuery } from "features/defects/api";
import { useElementsQuery } from "features/elements/api";
import { FileUploadDrawer } from "features/files/FileUploadDrawer";
import { useFilesQuery } from "features/files/api";
import { useMeasurementsQuery } from "features/measurements/api";
import {
  useApproveProjectMutation,
  useProjectQuery,
  useReturnForCorrectionMutation,
  useSaveTechnicalTaskMutation,
  useSaveWorkProgramMutation,
  useSetProjectReportTemplateMutation,
  useSubmitReviewMutation,
} from "features/projects/api";
import {
  PDF_EXPORT_AVAILABLE,
  PDF_EXPORT_UNAVAILABLE_MESSAGE,
  downloadReportDocx,
  openReportPdf,
  useApproveReportMutation,
  useGenerateProjectDocxMutation,
  useGenerateProjectPdfMutation,
  useProjectReportsQuery,
  useReportTemplatesQuery,
} from "features/reports/api";
import { useAuthStore } from "features/auth/authStore";
import { extractApiErrorMessage } from "shared/api/errors";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";

type TaskFormState = {
  id?: string;
  execution_basis: string;
  survey_goal: string;
  building_parts: string;
  engineering_systems: string;
  required_methods: string;
  result_requirements: string;
  deadlines: string;
  output_documentation: string;
};

type ProgramFormState = {
  id?: string;
  structures: string;
  zones: string;
  methods: string;
  tools_and_devices: string;
  measurements: string;
  photo_requirements: string;
  responsible_executors: string;
  completeness_checklist: string;
};

function createTaskState(project: NonNullable<ReturnType<typeof useProjectQuery>["data"]>): TaskFormState {
  return {
    id: project.technical_task?.id,
    execution_basis: project.technical_task?.execution_basis ?? "",
    survey_goal: project.technical_task?.survey_goal ?? "",
    building_parts: project.technical_task?.building_parts ?? "",
    engineering_systems: project.technical_task?.engineering_systems ?? "",
    required_methods: project.technical_task?.required_methods ?? "",
    result_requirements: project.technical_task?.result_requirements ?? "",
    deadlines: project.technical_task?.deadlines ?? "",
    output_documentation: project.technical_task?.output_documentation ?? "",
  };
}

function createProgramState(project: NonNullable<ReturnType<typeof useProjectQuery>["data"]>): ProgramFormState {
  return {
    id: project.work_program?.id,
    structures: project.work_program?.structures ?? "",
    zones: project.work_program?.zones ?? "",
    methods: project.work_program?.methods ?? "",
    tools_and_devices: project.work_program?.tools_and_devices ?? "",
    measurements: project.work_program?.measurements ?? "",
    photo_requirements: project.work_program?.photo_requirements ?? "",
    responsible_executors: project.work_program?.responsible_executors ?? "",
    completeness_checklist: (project.work_program?.completeness_checklist ?? []).join("\n"),
  };
}

function formatReportGenerationError(error: unknown) {
  if (axios.isAxiosError(error)) {
    const payload = error.response?.data as { can_generate?: boolean; errors?: Array<{ section?: string; message?: string }> } | undefined;
    if (payload?.can_generate === false && Array.isArray(payload.errors)) {
      return payload.errors.map((item) => `${item.section ?? "Validation"}: ${item.message ?? "Generation requirement is not satisfied."}`).join(" | ");
    }
  }
  return extractApiErrorMessage(error);
}

function formatReportStatus(status: string) {
  switch (status) {
    case "draft":
      return "Черновик";
    case "generated":
      return "Сформирован";
    case "approved":
      return "Утверждён";
    case "archived":
      return "Архив";
    default:
      return status;
  }
}

export function ProjectDetailPage() {
  const { projectId } = useParams();
  const role = useAuthStore((state) => state.role);
  const projectQuery = useProjectQuery(projectId ?? "");
  const elementsQuery = useElementsQuery();
  const defectsQuery = useDefectsQuery();
  const measurementsQuery = useMeasurementsQuery();
  const filesQuery = useFilesQuery({ projectId: projectId ?? "" });
  const reportsQuery = useProjectReportsQuery(projectId ?? "");
  const submitReviewMutation = useSubmitReviewMutation(projectId ?? "");
  const approveProjectMutation = useApproveProjectMutation(projectId ?? "");
  const returnForCorrectionMutation = useReturnForCorrectionMutation(projectId ?? "");
  const saveTechnicalTaskMutation = useSaveTechnicalTaskMutation(projectId ?? "");
  const saveWorkProgramMutation = useSaveWorkProgramMutation(projectId ?? "");
  const setReportTemplateMutation = useSetProjectReportTemplateMutation(projectId ?? "");
  const generateDocxMutation = useGenerateProjectDocxMutation(projectId ?? "");
  const generatePdfMutation = useGenerateProjectPdfMutation(projectId ?? "");
  const approveReportMutation = useApproveReportMutation(projectId ?? "");
  const reportTemplatesQuery = useReportTemplatesQuery();
  const [actionError, setActionError] = useState<string | null>(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [taskForm, setTaskForm] = useState<TaskFormState | null>(null);
  const [programForm, setProgramForm] = useState<ProgramFormState | null>(null);

  useEffect(() => {
    if (projectQuery.data) {
      setTaskForm(createTaskState(projectQuery.data));
      setProgramForm(createProgramState(projectQuery.data));
    }
  }, [projectQuery.data]);

  const project = projectQuery.data;
  const projectElements = useMemo(() => {
    if (!project) {
      return [];
    }
    return (elementsQuery.data?.results ?? []).filter((element) => element.project === project.id);
  }, [elementsQuery.data?.results, project]);
  const projectDefects = useMemo(() => {
    if (!project) {
      return [];
    }
    return (defectsQuery.data?.results ?? []).filter((defect) => defect.project === project.id);
  }, [defectsQuery.data?.results, project]);
  const projectMeasurements = useMemo(() => {
    return (measurementsQuery.data?.results ?? []).filter((measurement) => {
      return projectElements.some((element) => element.id === measurement.structural_element);
    });
  }, [measurementsQuery.data?.results, projectElements]);
  const projectFiles = filesQuery.data?.results ?? [];
  const reports = reportsQuery.data ?? [];
  const latestReport = reports[0];
  const noDefectElements = useMemo(() => projectElements.filter((element) => !element.has_defects).length, [projectElements]);
  const defectElements = projectElements.length - noDefectElements;

  if (!projectId) {
    return <ErrorState message="Не найден идентификатор проекта." />;
  }

  if (
    projectQuery.isLoading ||
    elementsQuery.isLoading ||
    defectsQuery.isLoading ||
    measurementsQuery.isLoading ||
    filesQuery.isLoading ||
    reportsQuery.isLoading
  ) {
    return <LoadingState />;
  }

  if (
    projectQuery.isError ||
    !projectQuery.data ||
    elementsQuery.isError ||
    defectsQuery.isError ||
    measurementsQuery.isError ||
    filesQuery.isError ||
    reportsQuery.isError
  ) {
    return <ErrorState message="Не удалось загрузить карточку проекта и связанные данные." />;
  }

  const canSubmitReview = ["Admin", "Manager", "Engineer"].includes(role ?? "") && project.status === "In Progress";
  const canApproveProject = ["Admin", "Expert"].includes(role ?? "") && project.status === "Review";
  const canReturnForCorrection = ["Admin", "Expert"].includes(role ?? "") && project.status === "Review";
  const canManageProjectDocs = ["Admin", "Manager", "Engineer"].includes(role ?? "");
  const canManageTemplate = ["Admin", "Manager", "Expert"].includes(role ?? "");
  const canGenerateReport = ["Admin", "Manager", "Engineer", "Expert"].includes(role ?? "");
  const canApproveReport = ["Admin", "Expert"].includes(role ?? "") && Boolean(latestReport) && latestReport?.status !== "approved";

  const handleSubmitReview = async () => {
    try {
      setActionError(null);
      await submitReviewMutation.mutateAsync();
    } catch (error) {
      setActionError(extractApiErrorMessage(error));
    }
  };

  const handleApproveProject = async () => {
    try {
      setActionError(null);
      await approveProjectMutation.mutateAsync();
    } catch (error) {
      setActionError(extractApiErrorMessage(error));
    }
  };

  const handleReturnForCorrection = async () => {
    try {
      setActionError(null);
      await returnForCorrectionMutation.mutateAsync();
    } catch (error) {
      setActionError(extractApiErrorMessage(error));
    }
  };

  const handleSaveTechnicalTask = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!taskForm) return;
    try {
      setActionError(null);
      await saveTechnicalTaskMutation.mutateAsync({
        id: taskForm.id,
        project: project.id,
        execution_basis: taskForm.execution_basis,
        survey_goal: taskForm.survey_goal,
        building_parts: taskForm.building_parts,
        engineering_systems: taskForm.engineering_systems,
        required_methods: taskForm.required_methods,
        result_requirements: taskForm.result_requirements,
        deadlines: taskForm.deadlines,
        output_documentation: taskForm.output_documentation,
      });
    } catch (error) {
      setActionError(extractApiErrorMessage(error));
    }
  };

  const handleSaveWorkProgram = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!programForm) return;
    try {
      setActionError(null);
      await saveWorkProgramMutation.mutateAsync({
        id: programForm.id,
        project: project.id,
        structures: programForm.structures,
        zones: programForm.zones,
        methods: programForm.methods,
        tools_and_devices: programForm.tools_and_devices,
        measurements: programForm.measurements,
        photo_requirements: programForm.photo_requirements,
        responsible_executors: programForm.responsible_executors,
        completeness_checklist: programForm.completeness_checklist
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean),
      });
    } catch (error) {
      setActionError(extractApiErrorMessage(error));
    }
  };

  const handleGenerateDocx = async () => {
    try {
      setActionError(null);
      const report = await generateDocxMutation.mutateAsync();
      await downloadReportDocx(report.download_docx_url);
    } catch (error) {
      setActionError(formatReportGenerationError(error));
    }
  };

  const handleGeneratePdf = async () => {
    if (!PDF_EXPORT_AVAILABLE) {
      setActionError(PDF_EXPORT_UNAVAILABLE_MESSAGE);
      return;
    }
    try {
      setActionError(null);
      const report = await generatePdfMutation.mutateAsync();
      await openReportPdf(report.download_pdf_url);
    } catch (error) {
      setActionError(formatReportGenerationError(error));
    }
  };

  const handleApproveReport = async () => {
    if (!latestReport) return;
    try {
      setActionError(null);
      await approveReportMutation.mutateAsync(latestReport.id);
    } catch (error) {
      setActionError(extractApiErrorMessage(error));
    }
  };

  return (
    <div className="page-grid">
      <header className="page-header">
        <div>
          <p className="pill">Project ID {projectId}</p>
          <h1 className="page-title">Карточка проекта обследования</h1>
          <p className="muted">{project.building_object_name || project.customer_name}</p>
        </div>
        <div className="page-actions">
          {canSubmitReview ? (
            <button className="button" type="button" onClick={handleSubmitReview} disabled={submitReviewMutation.isPending}>
              {submitReviewMutation.isPending ? "Отправляем..." : "Отправить на проверку"}
            </button>
          ) : null}
          {canReturnForCorrection ? (
            <button className="button" type="button" onClick={handleReturnForCorrection} disabled={returnForCorrectionMutation.isPending}>
              {returnForCorrectionMutation.isPending ? "Возвращаем..." : "Вернуть на доработку"}
            </button>
          ) : null}
          {canApproveProject ? (
            <button className="button primary" type="button" onClick={handleApproveProject} disabled={approveProjectMutation.isPending}>
              {approveProjectMutation.isPending ? "Утверждаем..." : "Утвердить проект"}
            </button>
          ) : null}
        </div>
      </header>

      <section className="kpi-row">
        <article className="kpi-item">
          <div className="muted">Статус проекта</div>
          <div className="stat-value">{project.status}</div>
        </article>
        <article className="kpi-item">
          <div className="muted">Элементы без дефектов</div>
          <div className="stat-value">{noDefectElements}</div>
        </article>
        <article className="kpi-item">
          <div className="muted">Элементы с дефектами</div>
          <div className="stat-value">{defectElements}</div>
        </article>
        <article className="kpi-item">
          <div className="muted">Материалы для отчёта</div>
          <div className="stat-value">{projectFiles.filter((item) => item.is_for_report).length}</div>
        </article>
      </section>

      <section className="section-grid">
        <article className="list-card glass-card">
          <h3 className="section-title">Ход проекта</h3>
          <ul className="list">
            <li className="list-item">Объект: {project.building_object_name || project.building_object}</li>
            <li className="list-item">Заказчик: {project.customer_name}</li>
            <li className="list-item">Договор: {project.contract_number || "—"}</li>
            <li className="list-item">Вид обследования: {project.inspection_type}</li>
            <li className="list-item">Сроки: {project.start_date ?? "—"} - {project.end_date ?? "—"}</li>
            <li className="list-item">Ответственный инженер: {project.responsible_engineer_name || "—"}</li>
          </ul>
        </article>

        <article className="list-card glass-card">
          <h3 className="section-title">Рабочий маршрут</h3>
          <div className="inline-actions">
            <Link className="button" to="/elements">
              Элементы
            </Link>
            <Link className="button" to="/defects">
              Дефекты
            </Link>
            <Link className="button" to="/measurements">
              Измерения
            </Link>
            <button className="button" type="button" onClick={() => setIsUploadOpen(true)}>
              Фото и файлы
            </button>
            {project.status === "Approved" ? (
              <Link className="button" to={`/projects/${project.id}/passport`}>
                Паспорт объекта
              </Link>
            ) : null}
          </div>
          <p className="muted" style={{ marginTop: 16 }}>
            По PRD проект нельзя отправить на проверку, пока не заполнены все обязательные элементы и не загружены обзорные фото для бездефектных элементов.
          </p>
        </article>
      </section>

      <section className="section-grid">
        <article className="page-card glass-card">
          <h3 className="section-title">Шаблон отчёта</h3>
          <p className="muted">Проект может использовать системный шаблон по умолчанию или экспертный шаблон с собственным порядком блоков.</p>
          <select
            className="input"
            value={project.report_template ?? ""}
            onChange={async (event) => {
              try {
                setActionError(null);
                await setReportTemplateMutation.mutateAsync({
                  report_template: event.target.value || null,
                });
              } catch (error) {
                setActionError(extractApiErrorMessage(error));
              }
            }}
            disabled={!canManageTemplate || setReportTemplateMutation.isPending}
          >
            <option value="">Системный шаблон по умолчанию</option>
            {(reportTemplatesQuery.data?.results ?? [])
              .filter((item) => item.is_active)
              .map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
          </select>
          <p className="muted" style={{ marginTop: 12 }}>
            {project.report_template_name ? `Выбран шаблон: ${project.report_template_name}` : "Используется шаблон по умолчанию."}
          </p>
        </article>
      </section>

      <section className="section-grid">
        <article className="page-card glass-card">
          <h3 className="section-title">Техническое задание</h3>
          <form className="form-grid" onSubmit={handleSaveTechnicalTask}>
            <div>
              <label className="label">Основание выполнения работ</label>
              <textarea
                className="textarea"
                rows={2}
                value={taskForm?.execution_basis ?? ""}
                onChange={(event) => setTaskForm((current) => (current ? { ...current, execution_basis: event.target.value } : current))}
              />
            </div>
            <div>
              <label className="label">Цель обследования</label>
              <textarea
                className="textarea"
                rows={2}
                value={taskForm?.survey_goal ?? ""}
                onChange={(event) => setTaskForm((current) => (current ? { ...current, survey_goal: event.target.value } : current))}
              />
            </div>
            <div className="field-grid">
              <div>
                <label className="label">Обследуемые части здания</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={taskForm?.building_parts ?? ""}
                  onChange={(event) => setTaskForm((current) => (current ? { ...current, building_parts: event.target.value } : current))}
                />
              </div>
              <div>
                <label className="label">Инженерные системы</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={taskForm?.engineering_systems ?? ""}
                  onChange={(event) => setTaskForm((current) => (current ? { ...current, engineering_systems: event.target.value } : current))}
                />
              </div>
            </div>
            <div className="field-grid">
              <div>
                <label className="label">Требуемые методы</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={taskForm?.required_methods ?? ""}
                  onChange={(event) => setTaskForm((current) => (current ? { ...current, required_methods: event.target.value } : current))}
                />
              </div>
              <div>
                <label className="label">Требования к результатам</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={taskForm?.result_requirements ?? ""}
                  onChange={(event) => setTaskForm((current) => (current ? { ...current, result_requirements: event.target.value } : current))}
                />
              </div>
            </div>
            <div className="field-grid">
              <div>
                <label className="label">Сроки</label>
                <input
                  className="input"
                  value={taskForm?.deadlines ?? ""}
                  onChange={(event) => setTaskForm((current) => (current ? { ...current, deadlines: event.target.value } : current))}
                />
              </div>
              <div>
                <label className="label">Выходная документация</label>
                <input
                  className="input"
                  value={taskForm?.output_documentation ?? ""}
                  onChange={(event) => setTaskForm((current) => (current ? { ...current, output_documentation: event.target.value } : current))}
                />
              </div>
            </div>
            {canManageProjectDocs ? (
              <div className="drawer-actions">
                <button className="button primary" type="submit" disabled={saveTechnicalTaskMutation.isPending}>
                  {saveTechnicalTaskMutation.isPending ? "Сохраняем..." : "Сохранить техзадание"}
                </button>
              </div>
            ) : null}
          </form>
        </article>

        <article className="page-card glass-card">
          <h3 className="section-title">Программа работ</h3>
          <form className="form-grid" onSubmit={handleSaveWorkProgram}>
            <div className="field-grid">
              <div>
                <label className="label">Конструкции</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={programForm?.structures ?? ""}
                  onChange={(event) => setProgramForm((current) => (current ? { ...current, structures: event.target.value } : current))}
                />
              </div>
              <div>
                <label className="label">Зоны</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={programForm?.zones ?? ""}
                  onChange={(event) => setProgramForm((current) => (current ? { ...current, zones: event.target.value } : current))}
                />
              </div>
            </div>
            <div className="field-grid">
              <div>
                <label className="label">Методы</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={programForm?.methods ?? ""}
                  onChange={(event) => setProgramForm((current) => (current ? { ...current, methods: event.target.value } : current))}
                />
              </div>
              <div>
                <label className="label">Инструменты и приборы</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={programForm?.tools_and_devices ?? ""}
                  onChange={(event) => setProgramForm((current) => (current ? { ...current, tools_and_devices: event.target.value } : current))}
                />
              </div>
            </div>
            <div className="field-grid">
              <div>
                <label className="label">Измерения</label>
                <textarea
                  className="textarea"
                  rows={2}
                  value={programForm?.measurements ?? ""}
                  onChange={(event) => setProgramForm((current) => (current ? { ...current, measurements: event.target.value } : current))}
                />
              </div>
              <div>
                <label className="label">Требования к фотофиксации</label>
                <textarea
                  className="textarea"
                  rows={2}
                  value={programForm?.photo_requirements ?? ""}
                  onChange={(event) => setProgramForm((current) => (current ? { ...current, photo_requirements: event.target.value } : current))}
                />
              </div>
            </div>
            <div className="field-grid">
              <div>
                <label className="label">Ответственные исполнители</label>
                <input
                  className="input"
                  value={programForm?.responsible_executors ?? ""}
                  onChange={(event) => setProgramForm((current) => (current ? { ...current, responsible_executors: event.target.value } : current))}
                />
              </div>
              <div>
                <label className="label">Чек-лист полноты</label>
                <textarea
                  className="textarea"
                  rows={4}
                  value={programForm?.completeness_checklist ?? ""}
                  onChange={(event) => setProgramForm((current) => (current ? { ...current, completeness_checklist: event.target.value } : current))}
                />
              </div>
            </div>
            {canManageProjectDocs ? (
              <div className="drawer-actions">
                <button className="button primary" type="submit" disabled={saveWorkProgramMutation.isPending}>
                  {saveWorkProgramMutation.isPending ? "Сохраняем..." : "Сохранить программу работ"}
                </button>
              </div>
            ) : null}
          </form>
        </article>
      </section>

      <section className="section-grid">
        <article className="page-card glass-card">
          <div className="section-header">
            <h3 className="section-title">Фото и файлы проекта</h3>
            <button className="button" type="button" onClick={() => setIsUploadOpen(true)}>
              Загрузить материал
            </button>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Файл</th>
                <th>Категория</th>
                <th>Тип приложения</th>
                <th>Подпись</th>
                <th>В отчёт</th>
              </tr>
            </thead>
            <tbody>
              {projectFiles.map((item) => (
                <tr key={item.id}>
                  <td>{item.original_name}</td>
                  <td>{item.category}</td>
                  <td>{item.appendix_type_display || "—"}</td>
                  <td>{item.caption || "—"}</td>
                  <td>{item.is_for_report ? "Да" : "Нет"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="page-card glass-card">
          <div className="section-header">
            <h3 className="section-title">Отчёты по проекту</h3>
            <div className="inline-actions">
              {canGenerateReport ? (
                <>
                  <button className="button" type="button" onClick={handleGenerateDocx} disabled={generateDocxMutation.isPending}>
                    {generateDocxMutation.isPending ? "Генерируем DOCX..." : "Сформировать DOCX"}
                  </button>
                  <button
                    className="button"
                    type="button"
                    onClick={handleGeneratePdf}
                    disabled={!PDF_EXPORT_AVAILABLE || generatePdfMutation.isPending}
                    title={!PDF_EXPORT_AVAILABLE ? PDF_EXPORT_UNAVAILABLE_MESSAGE : undefined}
                  >
                    {generatePdfMutation.isPending ? "Генерируем PDF..." : "Сформировать PDF"}
                  </button>
                </>
              ) : null}
              {canApproveReport ? (
                <button className="button primary" type="button" onClick={handleApproveReport} disabled={approveReportMutation.isPending}>
                  {approveReportMutation.isPending ? "Утверждаем..." : "Утвердить отчёт"}
                </button>
              ) : null}
            </div>
          </div>
          {!PDF_EXPORT_AVAILABLE ? <p className="muted">{PDF_EXPORT_UNAVAILABLE_MESSAGE}</p> : null}
          {reports.length === 0 ? (
            <div className="form-grid">
              <span className="muted">Отчёт ещё не сформирован.</span>
              {canGenerateReport ? (
                  <button className="button primary" type="button" onClick={handleGenerateDocx} disabled={generateDocxMutation.isPending}>
                    {generateDocxMutation.isPending ? "Генерируем DOCX..." : "Сформировать отчёт"}
                  </button>
              ) : null}
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Наименование</th>
                  <th>Версия</th>
                  <th>Статус</th>
                  <th>Сформирован</th>
                  <th>Файлы</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td>{report.title}</td>
                    <td>v{report.version}</td>
                    <td>{formatReportStatus(report.status)}</td>
                    <td>{report.generated_at ? new Date(report.generated_at).toLocaleString() : "—"}</td>
                    <td>
                      <div className="inline-actions">
                        {report.preview_available ? (
                          <Link className="button" to={`/reports/${report.id}`}>
                            Preview
                          </Link>
                        ) : null}
                        <button
                          className="button"
                          type="button"
                          onClick={async () => {
                            try {
                              setActionError(null);
                              await downloadReportDocx(report.download_docx_url);
                            } catch (error) {
                              setActionError(extractApiErrorMessage(error));
                            }
                          }}
                          disabled={!report.download_docx_url}
                        >
                          Скачать DOCX
                        </button>
                        <button
                          className="button"
                          type="button"
                          onClick={async () => {
                            try {
                              setActionError(null);
                              await openReportPdf(report.download_pdf_url);
                            } catch (error) {
                              setActionError(extractApiErrorMessage(error));
                            }
                          }}
                          disabled={!PDF_EXPORT_AVAILABLE || !report.download_pdf_url}
                          title={!PDF_EXPORT_AVAILABLE ? PDF_EXPORT_UNAVAILABLE_MESSAGE : undefined}
                        >
                          Открыть PDF
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </article>
      </section>

      {actionError ? <span className="error-text">{actionError}</span> : null}

      <FileUploadDrawer
        open={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        project={project}
        elements={projectElements}
        defects={projectDefects}
        measurements={projectMeasurements}
      />
    </div>
  );
}
