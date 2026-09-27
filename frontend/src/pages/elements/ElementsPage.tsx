import { useMemo, useState } from "react";

import { useAuthStore } from "features/auth/authStore";
import { ElementCreateDrawer } from "features/elements/ElementCreateDrawer";
import { useElementsQuery } from "features/elements/api";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";

export function ElementsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const elementsQuery = useElementsQuery();
  const role = useAuthStore((state) => state.role);
  const canCreate = useMemo(() => ["Admin", "Manager", "Engineer"].includes(role ?? ""), [role]);

  if (elementsQuery.isLoading) {
    return <LoadingState />;
  }

  if (elementsQuery.isError) {
    return <ErrorState message="Не удалось загрузить конструктивные элементы." />;
  }

  return (
    <div className="page-grid">
      <PageIntro
        title="Конструктивные элементы"
        description="Это главный рабочий слой инженера: здесь нужно оценить каждый основной элемент здания, даже если видимых дефектов нет."
        actionLabel={canCreate ? "Добавить элемент" : undefined}
        actionNote={canCreate ? "Сначала оцените элемент, потом при необходимости добавьте дефект и измерения." : undefined}
        onActionClick={() => setIsCreateOpen(true)}
      />

      <section className="page-card glass-card">
        <table className="table">
          <thead>
            <tr>
              <th>Элемент</th>
              <th>Проект</th>
              <th>Расположение</th>
              <th>Состояние</th>
              <th>Дефекты</th>
            </tr>
          </thead>
          <tbody>
            {elementsQuery.data?.results.map((element) => (
              <tr key={element.id}>
                <td>{element.name}</td>
                <td>{element.project_display || element.project}</td>
                <td>{element.location || "—"}</td>
                <td>{element.condition_category || "—"}</td>
                <td>{element.has_defects ? "Да" : "Нет"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <ElementCreateDrawer open={isCreateOpen} onClose={() => setIsCreateOpen(false)} />
    </div>
  );
}

