import { WorkflowGuide } from "shared/ui/WorkflowGuide";
import { useDashboardData } from "features/dashboard/useDashboardData";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";

export function DashboardPage() {
  const { isLoading, isError, summary } = useDashboardData();

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError) {
    return <ErrorState message="Не удалось собрать обзор dashboard из backend API." />;
  }

  const activeProjects = summary.projects.slice(0, 3);
  const reviewQueue = [
    `Проектов на проверке: ${summary.projects.filter((project) => project.status === "Review").length}`,
    `Всего измерений в системе: ${summary.measurementsCount}`,
    `Всего зарегистрированных дефектов: ${summary.defectsCount}`,
  ];

  return (
    <div className="page-grid">
      <section className="hero-grid">
        <article className="hero-card glass-card">
          <p className="pill">MVP Control Center</p>
          <h1 className="headline">Единый обзор проектов обследования и технического состояния</h1>
          <p className="muted">
            Dashboard помогает менеджеру и эксперту быстро увидеть перегруженные этапы: активные проекты, дефекты повышенного риска, незавершенные оценки элементов и отчёты на согласовании.
          </p>
        </article>

        <article className="list-card glass-card">
          <h3 className="section-title">Очередь экспертной проверки</h3>
          <ul className="list">
            {reviewQueue.map((item) => (
              <li key={item} className="list-item">
                {item}
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="stat-grid">
        <article className="stat-card glass-card">
          <div className="muted">Активные проекты</div>
          <div className="stat-value">{summary.projectsCount}</div>
        </article>
        <article className="stat-card glass-card">
          <div className="muted">Объекты в системе</div>
          <div className="stat-value">{summary.objectsCount}</div>
        </article>
        <article className="stat-card glass-card">
          <div className="muted">Дефекты с риском</div>
          <div className="stat-value">{summary.defectsCount}</div>
        </article>
        <article className="stat-card glass-card">
          <div className="muted">Отчёты на согласовании</div>
          <div className="stat-value">{summary.reportsReviewCount}</div>
        </article>
      </section>

      <section className="section-grid">
        <article className="list-card glass-card">
          <h3 className="section-title">Текущие проекты</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Проект</th>
                <th>Статус</th>
                <th>Ответственный</th>
              </tr>
            </thead>
            <tbody>
              {activeProjects.map((project) => (
                <tr key={project.id}>
                  <td>{project.contract_number || project.id}</td>
                  <td>
                    <span className={`status ${project.status === "Review" ? "warning" : "success"}`}>{project.status}</span>
                  </td>
                  <td>{project.customer_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="list-card glass-card">
          <h3 className="section-title">Контроль полноты обследования</h3>
          <ul className="list">
            <li className="list-item">Этот блок уже считает данные из API и готов для расширения реальной аналитикой полноты обследования.</li>
            <li className="list-item">Следующим шагом сюда стоит добавить проверку обязательных оценок элементов без дефектов.</li>
            <li className="list-item">После наполнения базы здесь можно вывести реальные просрочки, ревью и готовность отчётов.</li>
          </ul>
        </article>
      </section>

      <WorkflowGuide
        title="Как инженер работает в системе"
        intro="Интерфейс теперь выстроен как последовательный рабочий маршрут. Не нужно прыгать между случайными разделами."
        steps={[
          {
            step: "01",
            title: "Менеджер создаёт объект",
            description: "Карточка объекта нужна как базовая точка хранения всех будущих обследований.",
            to: "/objects",
            ctaLabel: "Открыть объекты",
          },
          {
            step: "02",
            title: "Менеджер открывает проект обследования",
            description: "В проекте фиксируются заказчик, основание, цели и весь жизненный цикл обследования.",
            to: "/projects",
            ctaLabel: "Открыть проекты",
          },
          {
            step: "03",
            title: "Инженер оценивает все элементы",
            description: "Даже без дефектов элемент должен быть отражён в системе и в отчёте.",
            to: "/elements",
            ctaLabel: "Открыть элементы",
          },
          {
            step: "04",
            title: "Инженер фиксирует дефекты и измерения",
            description: "Проблемные места записываются отдельно и связываются с нужным элементом и проектом.",
            to: "/defects",
            ctaLabel: "Открыть дефекты",
          },
          {
            step: "05",
            title: "Эксперт проверяет и утверждает проект",
            description: "После заполнения элементов, дефектов и измерений проект отправляется на проверку.",
            to: "/reports",
            ctaLabel: "Открыть отчёты",
          },
        ]}
      />
    </div>
  );
}
