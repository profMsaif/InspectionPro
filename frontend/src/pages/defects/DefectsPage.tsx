import { useMemo, useState } from "react";

import { useAuthStore } from "features/auth/authStore";
import { DefectCreateDrawer } from "features/defects/DefectCreateDrawer";
import { useDefectsQuery } from "features/defects/api";
import { useElementsQuery } from "features/elements/api";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";

export function DefectsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const defectsQuery = useDefectsQuery();
  const elementsQuery = useElementsQuery();
  const role = useAuthStore((state) => state.role);
  const canCreate = useMemo(() => ["Admin", "Manager", "Engineer"].includes(role ?? ""), [role]);
  const elementMap = useMemo(
    () => new Map((elementsQuery.data?.results ?? []).map((item) => [item.id, item.name])),
    [elementsQuery.data?.results],
  );

  if (defectsQuery.isLoading) {
    return <LoadingState />;
  }

  if (defectsQuery.isError) {
    return <ErrorState message="Не удалось загрузить дефекты." />;
  }

  return (
    <div className="page-grid">
      <PageIntro
        title="Реестр дефектов"
        description="Дефекты фиксируются как отдельные записи с привязкой к элементу, помещению, фотофиксации и категории состояния."
        actionLabel={canCreate ? "Добавить дефект" : undefined}
        actionNote={canCreate ? "Сначала заведите элемент, затем добавьте конкретный дефект к нужной конструкции." : undefined}
        onActionClick={() => setIsCreateOpen(true)}
      />

      <section className="page-card glass-card">
        <table className="table">
          <thead>
            <tr>
              <th>Дефект</th>
              <th>Элемент</th>
              <th>Этаж / зона</th>
              <th>Категория</th>
            </tr>
          </thead>
          <tbody>
            {defectsQuery.data?.results.map((defect) => (
              <tr key={defect.title}>
                <td>{defect.title}</td>
                <td>{defect.structural_element_name || elementMap.get(defect.structural_element) || defect.structural_element}</td>
                <td>{defect.floor || defect.location || "—"}</td>
                <td>
                  <span className={`status ${defect.final_condition_category.includes("Авар") ? "danger" : "warning"}`}>
                    {defect.final_condition_category || "—"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <DefectCreateDrawer open={isCreateOpen} onClose={() => setIsCreateOpen(false)} />
    </div>
  );
}
