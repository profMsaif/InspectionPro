import { useMemo, useState } from "react";

import { useAuthStore } from "features/auth/authStore";
import { useElementsQuery } from "features/elements/api";
import { MeasurementCreateDrawer } from "features/measurements/MeasurementCreateDrawer";
import { useMeasurementsQuery } from "features/measurements/api";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";

export function MeasurementsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const measurementsQuery = useMeasurementsQuery();
  const elementsQuery = useElementsQuery();
  const role = useAuthStore((state) => state.role);
  const canCreate = useMemo(() => ["Admin", "Manager", "Engineer"].includes(role ?? ""), [role]);
  const elementMap = useMemo(
    () => new Map((elementsQuery.data?.results ?? []).map((item) => [item.id, item.name])),
    [elementsQuery.data?.results],
  );

  if (measurementsQuery.isLoading) {
    return <LoadingState />;
  }

  if (measurementsQuery.isError) {
    return <ErrorState message="Не удалось загрузить измерения." />;
  }

  return (
    <div className="page-grid">
      <PageIntro
        title="Инструментальные измерения"
        description="Результаты измерений сохраняются в проекте и могут быть связаны с элементом или конкретным дефектом."
        actionLabel={canCreate ? "Добавить измерение" : undefined}
        actionNote={canCreate ? "Обычно инженер добавляет измерение после фиксации элемента и дефекта." : undefined}
        onActionClick={() => setIsCreateOpen(true)}
      />

      <section className="page-card glass-card">
        <table className="table">
          <thead>
            <tr>
              <th>Тип измерения</th>
              <th>Значение</th>
              <th>Элемент</th>
              <th>Место</th>
              <th>Инженер</th>
            </tr>
          </thead>
          <tbody>
            {measurementsQuery.data?.results.map((item) => (
              <tr key={item.id}>
                <td>{item.measurement_type}</td>
                <td>{`${item.value} ${item.unit}`}</td>
                <td>{item.structural_element_name || elementMap.get(item.structural_element) || item.structural_element}</td>
                <td>{item.location || "—"}</td>
                <td>{item.engineer_name || "Не указан"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <MeasurementCreateDrawer open={isCreateOpen} onClose={() => setIsCreateOpen(false)} />
    </div>
  );
}
