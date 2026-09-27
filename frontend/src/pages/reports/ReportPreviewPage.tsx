import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  PDF_EXPORT_AVAILABLE,
  PDF_EXPORT_UNAVAILABLE_MESSAGE,
  downloadReportDocx,
  openReportPdf,
  useReportQuery,
} from "features/reports/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";

const LABEL_MAP: Record<string, string> = {
  basis_for_inspection: "Основание для проведения обследования",
  inspection_organization: "Организация, проводящая обследование",
  customer: "Заказчик",
  operating_organization: "Эксплуатирующая организация",
  name: "Наименование",
  address: "Адрес",
  object_type: "Тип объекта",
  purpose: "Назначение",
  construction_year: "Год постройки",
  floors_count: "Этажность",
  area: "Площадь",
  structural_system: "Конструктивная система",
  main_materials: "Основные материалы",
  inspection_type: "Вид обследования",
  responsible_engineer: "Ответственный инженер",
  expert: "Эксперт",
  inspection_start_date: "Дата начала обследования",
  inspection_end_date: "Дата окончания обследования",
  project_status: "Статус проекта",
  methods: "Методы обследования",
  final_condition_category: "Итоговая категория технического состояния",
  summary: "Вывод",
  restrictions: "Ограничения",
  need_for_monitoring: "Необходимость мониторинга",
  need_for_additional_inspection: "Необходимость дополнительного обследования",
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function asArray(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? (value as Array<Record<string, unknown>>) : [];
}

function formatLabel(value: string) {
  return LABEL_MAP[value] ?? value.split("_").join(" ");
}

function formatValue(value: unknown) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item ?? "—")).join(", ") || "—";
  }
  if (typeof value === "boolean") {
    return value ? "Да" : "Нет";
  }
  if (value && typeof value === "object") {
    return "—";
  }
  return String(value ?? "—");
}

function isImageFile(file: Record<string, unknown>) {
  const contentType = String(file.content_type ?? "");
  const originalName = String(file.original_name ?? "").toLowerCase();
  return (
    contentType.startsWith("image/") ||
    [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"].some((extension) => originalName.endsWith(extension))
  );
}

function PhotoGallery({ files }: { files: Array<Record<string, unknown>> }) {
  const imageFiles = files.filter(isImageFile);

  if (!imageFiles.length) {
    return null;
  }

  return (
    <div className="photo-grid">
      {imageFiles.map((item, index) => (
        <figure className="photo-card" key={String(item.id ?? index)}>
          <a href={String(item.url ?? "#")} target="_blank" rel="noreferrer">
            <img
              className="photo-preview"
              src={String(item.url ?? "")}
              alt={String(item.caption ?? item.original_name ?? "Фото")}
              loading="lazy"
            />
          </a>
          <figcaption className="muted">
            {String(item.caption ?? item.original_name ?? "Фото")}
          </figcaption>
        </figure>
      ))}
    </div>
  );
}

function FileTable({ files }: { files: Array<Record<string, unknown>> }) {
  if (!files.length) {
    return <span className="muted">Файлы не приложены.</span>;
  }

  return (
    <>
      <PhotoGallery files={files} />
      <table className="table">
        <thead>
          <tr>
            <th>Файл</th>
            <th>Подпись</th>
            <th>Тип</th>
          </tr>
        </thead>
        <tbody>
          {files.map((item, index) => (
            <tr key={String(item.id ?? index)}>
              <td>
                {item.url ? (
                  <a href={String(item.url)} target="_blank" rel="noreferrer">
                    {String(item.original_name ?? "—")}
                  </a>
                ) : (
                  String(item.original_name ?? "—")
                )}
              </td>
              <td>{String(item.caption ?? "—")}</td>
              <td>{String(item.appendix_type_display ?? "—")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

export function ReportPreviewPage() {
  const { reportId } = useParams();
  const reportQuery = useReportQuery(reportId ?? "");
  const [fileError, setFileError] = useState<string | null>(null);

  if (!reportId) {
    return <ErrorState message="Не найден идентификатор отчёта." />;
  }

  if (reportQuery.isLoading) {
    return <LoadingState />;
  }

  if (reportQuery.isError || !reportQuery.data) {
    return <ErrorState message="Не удалось загрузить снимок отчёта." />;
  }

  const report = reportQuery.data;
  const snapshot = (report.json_snapshot ?? {}) as Record<string, unknown>;
  const template = asRecord(snapshot.template);
  const titlePage = asRecord(snapshot.title_page);
  const toc = asArray(snapshot.table_of_contents);
  const introduction = asRecord(snapshot.introduction);
  const objectInformation = asRecord(snapshot.object_information);
  const inspectionInformation = asRecord(snapshot.inspection_type_and_methods);
  const technicalDocumentationAnalysis = asRecord(snapshot.technical_documentation_analysis);
  const surveyResults = asRecord(snapshot.survey_results);
  const briefCharacteristics = asRecord(surveyResults.brief_characteristics);
  const constructiveCharacteristics = asRecord(briefCharacteristics.constructive_characteristics);
  const visualControl = asRecord(surveyResults.visual_and_measurement_control);
  const detailedControl = asRecord(surveyResults.detailed_instrumental_control);
  const environmentalImpact = asRecord(surveyResults.environmental_impact_assessment);
  const calculations = asRecord(snapshot.verification_calculations);
  const resultAnalysis = asRecord(snapshot.result_analysis);
  const conclusions = asRecord(snapshot.conclusions);
  const recommendations = asRecord(snapshot.recommendations_section);
  const appendices = asRecord(snapshot.appendices);

  const objectPhotos = asArray(objectInformation.overview_photos);
  const documentationFiles = asArray(technicalDocumentationAnalysis.documents);
  const visualElements = asArray(visualControl.elements);
  const visualDefects = asArray(visualControl.defects);
  const visualMeasurements = asArray(visualControl.measurements);
  const detailedSections = asArray(detailedControl.sections);
  const environmentalFactors = asArray(environmentalImpact.factors);
  const calculationInputFiles = asArray(calculations.input_data);
  const calculationFiles = asArray(calculations.calculation_files);
  const appendixGroups = asArray(appendices.groups);
  const recommendationItems = Array.isArray(recommendations.items) ? recommendations.items : [];
  const templateBlocks = asArray(template.blocks);
  const templateBlockTitleMap = new Map(templateBlocks.map((item) => [String(item.block_type ?? ""), String(item.title ?? item.block_type_display ?? item.block_type ?? "")]));
  const blockTitle = (blockType: string, fallback: string) => templateBlockTitleMap.get(blockType) || fallback;

  return (
    <div className="page-grid">
      <PageIntro
        title={String(titlePage.report_title ?? report.title)}
        description="Предпросмотр строится из сохранённого JSON snapshot полного технического отчёта."
      />

      <div className="inline-actions">
        <Link className="button" to="/reports">
          К списку отчётов
        </Link>
        {report.project ? (
          <Link className="button" to={`/projects/${report.project}`}>
            К проекту
          </Link>
        ) : null}
        <button
          className="button"
          type="button"
          onClick={async () => {
            try {
              setFileError(null);
              await downloadReportDocx(report.download_docx_url);
            } catch (error) {
              setFileError(extractApiErrorMessage(error));
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
              setFileError(null);
              await openReportPdf(report.download_pdf_url);
            } catch (error) {
              setFileError(extractApiErrorMessage(error));
            }
          }}
          disabled={!PDF_EXPORT_AVAILABLE || !report.download_pdf_url}
          title={!PDF_EXPORT_AVAILABLE ? PDF_EXPORT_UNAVAILABLE_MESSAGE : undefined}
        >
          Открыть PDF
        </button>
      </div>

      {fileError ? <span className="error-text">{fileError}</span> : null}
      {!PDF_EXPORT_AVAILABLE ? <span className="muted">{PDF_EXPORT_UNAVAILABLE_MESSAGE}</span> : null}

      <section className="page-card glass-card">
        <h3 className="section-title">Шаблон отчёта</h3>
        <p className="muted">{String(template.name ?? "Системный шаблон")}</p>
        {templateBlocks.length ? (
          <ul className="list">
            {templateBlocks.map((item, index) => (
              <li className="list-item" key={String(item.id ?? index)}>
                {String(item.title ?? item.block_type_display ?? item.block_type ?? "Блок")}
              </li>
            ))}
          </ul>
        ) : null}
      </section>

      <section className="section-grid">
        <article className="page-card glass-card">
          <h3 className="section-title">{blockTitle("title_page", "Титульный лист")}</h3>
          <ul className="list">
            <li className="list-item">{String(titlePage.report_title ?? "—")}</li>
            <li className="list-item">{String(titlePage.report_subtitle ?? "—")}</li>
            <li className="list-item">{String(titlePage.object_name ?? "—")}</li>
            <li className="list-item">{`Адрес: ${String(titlePage.address ?? "—")}`}</li>
            <li className="list-item">{`Договор: ${String(titlePage.project_contract ?? "—")}`}</li>
          </ul>
        </article>

        <article className="page-card glass-card">
          <h3 className="section-title">{blockTitle("table_of_contents", "Содержание")}</h3>
          <ul className="list">
            {toc.map((item, index) => (
              <li className="list-item" key={String(item.number ?? index)}>
                {`${String(item.number ?? "—")} ${String(item.title ?? "—")}`}
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="section-grid">
        <article className="page-card glass-card">
          <h3 className="section-title">{blockTitle("introduction", "1. Введение")}</h3>
          <ul className="list">
            {Object.entries(introduction).map(([key, value]) => (
              <li className="list-item" key={key}>{`${formatLabel(key)}: ${formatValue(value)}`}</li>
            ))}
          </ul>
        </article>

        <article className="page-card glass-card">
          <h3 className="section-title">{blockTitle("object_information", "2. Сведения об объекте")}</h3>
          <ul className="list">
            {Object.entries(objectInformation)
              .filter(([key]) => key !== "overview_photos")
              .map(([key, value]) => (
                <li className="list-item" key={key}>{`${formatLabel(key)}: ${formatValue(value)}`}</li>
              ))}
          </ul>
        </article>
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">{blockTitle("inspection_information", "Сведения об обследовании")}</h3>
        <ul className="list">
          {Object.entries(inspectionInformation).map(([key, value]) => (
            <li className="list-item" key={key}>{`${formatLabel(key)}: ${formatValue(value)}`}</li>
          ))}
        </ul>
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">2.1 Фотоматериалы объекта</h3>
        <FileTable files={objectPhotos} />
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">{blockTitle("technical_documentation_analysis", "3. Анализ технической документации")}</h3>
        <p className="muted">{String(technicalDocumentationAnalysis.summary ?? "—")}</p>
        <FileTable files={documentationFiles} />
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">{blockTitle("brief_characteristics", "4.1 Краткая характеристика объекта")}</h3>
        <p className="muted">{String(briefCharacteristics.summary ?? "—")}</p>
        <table className="table">
          <thead>
            <tr>
              <th>Тип элемента</th>
              <th>Характеристики</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(constructiveCharacteristics).map(([elementType, value]) => {
              const items = Array.isArray(value) ? value : [];
              const characteristicsText = items
                .map((item) => {
                  const row = asRecord(item);
                  return `${String(row.name ?? "—")} (${String(row.location ?? "—")}, ${String(row.material ?? "—")})`;
                })
                .join("; ");
              return (
                <tr key={elementType}>
                  <td>{elementType}</td>
                  <td>{characteristicsText || "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">{blockTitle("visual_measurement_control", "4.2 Результаты визуального и измерительного контроля")}</h3>
        <p className="muted">{String(visualControl.summary ?? "—")}</p>

        <h4 className="section-title">Элементы</h4>
        <table className="table">
          <thead>
            <tr>
              <th>Тип</th>
              <th>Элемент</th>
              <th>Расположение</th>
              <th>Категория</th>
              <th>Дефекты</th>
              <th>Рекомендация</th>
            </tr>
          </thead>
          <tbody>
            {visualElements.map((item, index) => (
              <tr key={String(item.id ?? index)}>
                <td>{String(item.element_type ?? "—")}</td>
                <td>{String(item.element_name ?? "—")}</td>
                <td>{String(item.location ?? "—")}</td>
                <td>{String(item.condition_category ?? "—")}</td>
                <td>{String(item.defects_found ?? "—")}</td>
                <td>{String(item.recommendation ?? "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <h4 className="section-title">Дефекты</h4>
        <table className="table">
          <thead>
            <tr>
              <th>Элемент</th>
              <th>Тип</th>
              <th>Описание</th>
              <th>Категория</th>
            </tr>
          </thead>
          <tbody>
            {visualDefects.map((item, index) => (
              <tr key={String(item.id ?? index)}>
                <td>{String(item.related_element ?? "—")}</td>
                <td>{String(item.defect_type ?? "—")}</td>
                <td>{String(item.description ?? "—")}</td>
                <td>{String(item.condition_category ?? "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <h4 className="section-title">Измерения</h4>
        <table className="table">
          <thead>
            <tr>
              <th>Элемент</th>
              <th>Тип</th>
              <th>Значение</th>
              <th>Метод</th>
            </tr>
          </thead>
          <tbody>
            {visualMeasurements.map((item, index) => (
              <tr key={String(item.id ?? index)}>
                <td>{String(item.related_element ?? "—")}</td>
                <td>{String(item.measurement_type ?? "—")}</td>
                <td>{`${String(item.value ?? "—")} ${String(item.unit ?? "")}`}</td>
                <td>{String(item.method ?? "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">{blockTitle("detailed_instrumental_control", "4.3 Результаты детального инструментального контроля")}</h3>
        <p className="muted">{String(detailedControl.summary ?? "—")}</p>
        {detailedSections.map((section, index) => {
          const elements = asArray(section.elements);
          return (
            <article className="list-card" key={String(section.number ?? index)}>
              <h4 className="section-title">{`${String(section.number ?? "—")} ${String(section.title ?? "—")}`}</h4>
              <p className="muted">{String(section.summary ?? "—")}</p>
              <table className="table">
                <thead>
                  <tr>
                    <th>Элемент</th>
                    <th>Расположение</th>
                    <th>Категория</th>
                    <th>Вывод</th>
                  </tr>
                </thead>
                <tbody>
                  {elements.map((item, itemIndex) => (
                    <tr key={String(item.id ?? itemIndex)}>
                      <td>{String(item.element_name ?? "—")}</td>
                      <td>{String(item.location ?? "—")}</td>
                      <td>{String(item.condition_category ?? "—")}</td>
                      <td>{String(item.conclusion ?? "—")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </article>
          );
        })}
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">{blockTitle("environmental_impact", "4.4 Влияние внешних воздействий")}</h3>
        <p className="muted">{String(environmentalImpact.summary ?? "—")}</p>
        <table className="table">
          <thead>
            <tr>
              <th>Фактор</th>
              <th>Вывод</th>
            </tr>
          </thead>
          <tbody>
            {environmentalFactors.map((item, index) => (
              <tr key={String(item.code ?? index)}>
                <td>{String(item.title ?? "—")}</td>
                <td>{String(item.finding ?? "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="section-grid">
        <article className="page-card glass-card">
          <h3 className="section-title">{blockTitle("verification_calculations", "5. Результаты поверочных расчетов")}</h3>
          <p className="muted">{String(calculations.input_data_summary ?? "—")}</p>
          <FileTable files={calculationInputFiles} />
          <p className="muted" style={{ marginTop: 16 }}>{String(calculations.analysis ?? "—")}</p>
          <FileTable files={calculationFiles} />
        </article>

        <article className="page-card glass-card">
          <h3 className="section-title">{blockTitle("result_analysis", "6. Анализ результатов обследования")}</h3>
          <ul className="list">
            <li className="list-item">{`Визуальный анализ: ${String(resultAnalysis.visual_analysis ?? "—")}`}</li>
            <li className="list-item">{`Детальный анализ: ${String(resultAnalysis.detailed_analysis ?? "—")}`}</li>
          </ul>
        </article>
      </section>

      <section className="section-grid">
        <article className="page-card glass-card">
          <h3 className="section-title">{blockTitle("conclusions", "7. Выводы")}</h3>
          <ul className="list">
            {Object.entries(conclusions).map(([key, value]) => (
              <li className="list-item" key={key}>{`${formatLabel(key)}: ${formatValue(value)}`}</li>
            ))}
          </ul>
        </article>

        <article className="page-card glass-card">
          <h3 className="section-title">{blockTitle("recommendations", "8. Рекомендации")}</h3>
          <ul className="list">
            {recommendationItems.length ? (
              recommendationItems.map((item, index) => (
                <li className="list-item" key={`${String(item)}-${index}`}>
                  {String(item)}
                </li>
              ))
            ) : (
              <li className="list-item">Рекомендации отсутствуют.</li>
            )}
          </ul>
        </article>
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">{blockTitle("appendices", "9. Приложения")}</h3>
        <p className="muted">{String(appendices.summary ?? "—")}</p>
        {appendixGroups.length ? (
          appendixGroups.map((group, index) => (
            <article className="list-card" key={String(group.number ?? index)}>
              <h4 className="section-title">{`${String(group.number ?? "—")} ${String(group.title ?? "—")}`}</h4>
              <FileTable files={asArray(group.files)} />
            </article>
          ))
        ) : (
          <span className="muted">Приложения не приложены.</span>
        )}
      </section>
    </div>
  );
}
