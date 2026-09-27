import { Link } from "react-router-dom";

import {
  PDF_EXPORT_AVAILABLE,
  PDF_EXPORT_UNAVAILABLE_MESSAGE,
  downloadReportDocx,
  openReportPdf,
  useApproveReportMutation,
  useReportsQuery,
} from "features/reports/api";
import { useAuthStore } from "features/auth/authStore";
import { extractApiErrorMessage } from "shared/api/errors";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";
import { useState } from "react";

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

export function ReportsPage() {
  const role = useAuthStore((state) => state.role);
  const reportsQuery = useReportsQuery();
  const approveReportMutation = useApproveReportMutation();
  const [error, setError] = useState<string | null>(null);

  if (reportsQuery.isLoading) {
    return <LoadingState />;
  }

  if (reportsQuery.isError) {
    return <ErrorState message="Не удалось загрузить технические заключения." />;
  }

  return (
    <div className="page-grid">
      <PageIntro
        title="Технические заключения"
        description="Здесь видны все версии полного технического отчёта. Генерация и выпуск выполняются из карточки проекта."
      />

      <article className="page-card glass-card">
        <h3 className="section-title">Версии отчётов</h3>
        {reportsQuery.data?.results.length ? (
          <table className="table">
            <thead>
              <tr>
                <th>Объект</th>
                <th>Проект</th>
                <th>Версия</th>
                <th>Статус</th>
                <th>Сформирован</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {reportsQuery.data?.results.map((report) => (
                <tr key={report.id}>
                  <td>{report.object_name || "—"}</td>
                  <td>{report.project_display || report.title}</td>
                  <td>{`v${report.version}`}</td>
                  <td>
                    <span className={`status ${report.status === "approved" ? "success" : report.status === "generated" ? "warning" : ""}`}>
                      {formatReportStatus(report.status)}
                    </span>
                  </td>
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
                            setError(null);
                            await downloadReportDocx(report.download_docx_url);
                          } catch (fileError) {
                            setError(extractApiErrorMessage(fileError));
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
                            setError(null);
                            await openReportPdf(report.download_pdf_url);
                          } catch (fileError) {
                            setError(extractApiErrorMessage(fileError));
                          }
                        }}
                        disabled={!PDF_EXPORT_AVAILABLE || !report.download_pdf_url}
                        title={!PDF_EXPORT_AVAILABLE ? PDF_EXPORT_UNAVAILABLE_MESSAGE : undefined}
                      >
                        Открыть PDF
                      </button>
                      {(role === "Admin" || role === "Expert") && report.status !== "approved" ? (
                        <button
                          className="button"
                          type="button"
                          onClick={async () => {
                            try {
                              setError(null);
                              await approveReportMutation.mutateAsync(report.id);
                            } catch (mutationError) {
                              setError(extractApiErrorMessage(mutationError));
                            }
                          }}
                        >
                          Approve
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="form-grid">
            <span className="muted">Отчёт ещё не сформирован.</span>
            <Link className="button primary" to="/projects">
              Сформировать отчёт
            </Link>
          </div>
        )}
        {error ? <span className="error-text">{error}</span> : null}
        {!PDF_EXPORT_AVAILABLE ? <span className="muted">{PDF_EXPORT_UNAVAILABLE_MESSAGE}</span> : null}
      </article>

      <article className="page-card glass-card">
        <h3 className="section-title">Перед выпуском отчёта</h3>
        <ul className="list">
          <li className="list-item">Проверить обязательные оценки элементов без дефектов.</li>
          <li className="list-item">Подтвердить итоговые категории технического состояния экспертом.</li>
          <li className="list-item">Отметить приложения и фотографии для финального пакета.</li>
        </ul>
      </article>
    </div>
  );
}
