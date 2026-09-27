import { Link, useParams } from "react-router-dom";

import { useProjectPassportQuery } from "features/projects/api";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";

export function PassportPage() {
  const { projectId } = useParams();
  const passportQuery = useProjectPassportQuery(projectId ?? "");

  if (!projectId) {
    return <ErrorState message="Не найден идентификатор проекта для паспорта." />;
  }

  if (passportQuery.isLoading) {
    return <LoadingState />;
  }

  if (passportQuery.isError || !passportQuery.data) {
    return <ErrorState message="Не удалось сформировать структурированный паспорт объекта." />;
  }

  const passport = passportQuery.data;
  const inspectionInformation = passport.inspection_type_and_methods ?? {};

  return (
    <div className="page-grid">
      <PageIntro
        title="Паспорт здания / сооружения"
        description="Компактный паспорт собирается по утверждённым данным проекта. Полный технический отчёт формируется отдельно в разделе отчётов."
      />

      <Link className="button" to={`/projects/${projectId}`}>
        Вернуться к проекту
      </Link>

      <section className="section-grid">
        <article className="page-card glass-card">
          <h3 className="section-title">Общие сведения</h3>
          <ul className="list">
            {Object.entries(passport.general_information).map(([key, value]) => (
              <li className="list-item" key={key}>{`${key}: ${value ?? "—"}`}</li>
            ))}
          </ul>
        </article>

        <article className="page-card glass-card">
          <h3 className="section-title">Сведения об обследовании</h3>
          <ul className="list">
            {Object.entries(inspectionInformation).map(([key, value]) => (
              <li className="list-item" key={key}>{`${key}: ${value ?? "—"}`}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">Полная таблица оценки элементов</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Элемент</th>
              <th>Тип</th>
              <th>Расположение</th>
              <th>Материал</th>
              <th>Статус</th>
              <th>Категория</th>
              <th>Дефекты</th>
              <th>Рекомендация</th>
            </tr>
          </thead>
          <tbody>
            {passport.element_assessments.map((item, index) => (
              <tr key={`${String(item.id ?? index)}`}>
                <td>{String(item.element_name ?? "—")}</td>
                <td>{String(item.element_type ?? "—")}</td>
                <td>{String(item.location ?? "—")}</td>
                <td>{String(item.material ?? "—")}</td>
                <td>{String(item.inspection_status ?? "—")}</td>
                <td>{String(item.condition_category ?? "—")}</td>
                <td>{String(item.defects_found ?? "—")}</td>
                <td>{String(item.recommendation ?? "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">Реестр дефектов</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Элемент</th>
              <th>Тип дефекта</th>
              <th>Степень</th>
              <th>Причина</th>
              <th>Рекомендация</th>
              <th>Категория</th>
            </tr>
          </thead>
          <tbody>
            {passport.defect_register.map((item, index) => (
              <tr key={`${String(item.id ?? index)}`}>
                <td>{String(item.related_element ?? "—")}</td>
                <td>{String(item.defect_type ?? "—")}</td>
                <td>{String(item.severity ?? "—")}</td>
                <td>{String(item.probable_cause ?? "—")}</td>
                <td>{String(item.recommendation ?? "—")}</td>
                <td>{String(item.condition_category ?? "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
