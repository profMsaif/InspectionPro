import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { useAuthStore } from "features/auth/authStore";
import { ObjectCreateDrawer } from "features/objects/ObjectCreateDrawer";
import { PageIntro } from "shared/ui/PageIntro";
import { useObjectsQuery } from "features/objects/api";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";

export function ObjectsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const objectsQuery = useObjectsQuery();
  const role = useAuthStore((state) => state.role);
  const canCreate = useMemo(() => ["Admin", "Manager"].includes(role ?? ""), [role]);

  if (objectsQuery.isLoading) {
    return <LoadingState />;
  }

  if (objectsQuery.isError) {
    return <ErrorState message="Не удалось загрузить список объектов." />;
  }

  return (
    <div className="page-grid">
      <PageIntro
        title="Объекты недвижимости"
        description="Карточки зданий и сооружений с историей обследований, документами и привязанными материалами."
        actionLabel={canCreate ? "Создать объект" : undefined}
        actionNote={canCreate ? "После сохранения объект появится в списке и станет доступен для проекта обследования." : undefined}
        onActionClick={() => setIsCreateOpen(true)}
      />

      <section className="page-card glass-card">
        {!canCreate ? (
          <p className="muted">
            Создание карточек объектов выполняет менеджер или администратор. Для инженера рабочий маршрут обычно начинается с проекта, элементов и дефектов.
          </p>
        ) : null}
        <table className="table">
          <thead>
            <tr>
              <th>Наименование</th>
              <th>Адрес</th>
              <th>Тип</th>
              <th>Год постройки</th>
            </tr>
          </thead>
          <tbody>
            {objectsQuery.data?.results.map((item) => (
              <tr key={item.name}>
                <td>
                  <Link to={`/objects/${item.id}`}>{item.name}</Link>
                </td>
                <td>{item.address}</td>
                <td>{item.object_type}</td>
                <td>{item.construction_year ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <ObjectCreateDrawer open={isCreateOpen} onClose={() => setIsCreateOpen(false)} />
    </div>
  );
}
