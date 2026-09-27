import { useNavigate } from "react-router-dom";
import { useMemo, useState } from "react";

import { useAuthStore } from "features/auth/authStore";
import { useObjectsQuery } from "features/objects/api";
import { ProjectCreateDrawer } from "features/projects/ProjectCreateDrawer";
import { useProjectsQuery } from "features/projects/api";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";

export function ProjectsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const navigate = useNavigate();
  const projectsQuery = useProjectsQuery();
  const objectsQuery = useObjectsQuery();
  const role = useAuthStore((state) => state.role);
  const canCreate = useMemo(() => ["Admin", "Manager"].includes(role ?? ""), [role]);
  const objectMap = useMemo(
    () => new Map((objectsQuery.data?.results ?? []).map((item) => [item.id, item.name])),
    [objectsQuery.data?.results],
  );

  if (projectsQuery.isLoading) {
    return <LoadingState />;
  }

  if (projectsQuery.isError) {
    return <ErrorState message="Не удалось загрузить проекты обследования." />;
  }

  return (
    <div className="page-grid">
      <PageIntro
        title="Проекты обследования"
        description="Все обследования привязаны к объектам, командам и рабочим стадиям от черновика до утверждения."
        actionLabel={canCreate ? "Создать проект" : undefined}
        actionNote={canCreate ? "Менеджер открывает проект, после чего инженер переходит к элементам, дефектам и измерениям." : undefined}
        onActionClick={() => setIsCreateOpen(true)}
      />

      <section className="page-card glass-card">
        {!canCreate ? (
          <p className="muted">
            Создание проектов обследования выполняет менеджер. Инженер обычно получает уже открытый проект и дальше заполняет элементы, дефекты и измерения.
          </p>
        ) : null}
        <table className="table">
          <thead>
            <tr>
              <th>Объект</th>
              <th>Заказчик</th>
              <th>Статус</th>
              <th>Сроки</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            {projectsQuery.data?.results.map((project) => (
              <tr
                key={project.id}
                className="clickable-row"
                onClick={() => navigate(`/projects/${project.id}`)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    navigate(`/projects/${project.id}`);
                  }
                }}
                tabIndex={0}
              >
                <td>
                  {project.building_object_name || objectMap.get(project.building_object) || project.contract_number || project.id}
                </td>
                <td>{project.customer_name}</td>
                <td>
                  <span className={`status ${project.status === "Review" ? "warning" : "success"}`}>{project.status}</span>
                </td>
                <td>{`${project.start_date ?? "—"} - ${project.end_date ?? "—"}`}</td>
                <td>
                  <button
                    className="button"
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      navigate(`/projects/${project.id}`);
                    }}
                  >
                    Открыть
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {isCreateOpen ? <ProjectCreateDrawer open={isCreateOpen} onClose={() => setIsCreateOpen(false)} /> : null}
    </div>
  );
}
