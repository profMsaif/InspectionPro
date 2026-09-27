import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ObjectCreateDrawer } from "features/objects/ObjectCreateDrawer";
import { useFilesQuery } from "features/files/api";
import { useProjectsQuery } from "features/projects/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { useDeleteObjectMutation, useObjectQuery } from "features/objects/api";

export function ObjectDetailPage() {
  const { objectId } = useParams();
  const navigate = useNavigate();
  const objectQuery = useObjectQuery(objectId ?? "");
  const projectsQuery = useProjectsQuery();
  const filesQuery = useFilesQuery({ buildingObjectId: objectId ?? "" });
  const deleteObjectMutation = useDeleteObjectMutation();
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  if (!objectId) {
    return <ErrorState message="Не найден идентификатор объекта." />;
  }

  if (objectQuery.isLoading || projectsQuery.isLoading || filesQuery.isLoading) {
    return <LoadingState />;
  }

  if (objectQuery.isError || !objectQuery.data || projectsQuery.isError || filesQuery.isError) {
    return <ErrorState message="Не удалось загрузить карточку объекта." />;
  }

  const objectData = objectQuery.data;
  const relatedProjects = (projectsQuery.data?.results ?? []).filter((project) => project.building_object === objectData.id);
  const relatedFiles = filesQuery.data?.results ?? [];

  const handleDelete = async () => {
    if (!window.confirm("Удалить объект и его карточку?")) {
      return;
    }
    try {
      setActionError(null);
      await deleteObjectMutation.mutateAsync(objectData.id);
      navigate("/objects");
    } catch (error) {
      setActionError(extractApiErrorMessage(error));
    }
  };

  return (
    <div className="page-grid">
      <header className="page-header">
        <div>
          <p className="pill">Object ID {objectData.id}</p>
          <h1 className="page-title">{objectData.name}</h1>
          <p className="muted">{objectData.address}</p>
        </div>
        <div className="page-actions">
          <button className="button" type="button" onClick={() => setIsEditOpen(true)}>
            Редактировать
          </button>
          <button className="button" type="button" onClick={handleDelete} disabled={deleteObjectMutation.isPending}>
            {deleteObjectMutation.isPending ? "Удаляем..." : "Удалить"}
          </button>
        </div>
      </header>

      <section className="section-grid">
        <article className="list-card glass-card">
          <h3 className="section-title">Основные сведения</h3>
          <ul className="list">
            <li className="list-item">Тип объекта: {objectData.object_type}</li>
            <li className="list-item">Назначение: {objectData.purpose || "—"}</li>
            <li className="list-item">Год постройки: {objectData.construction_year ?? "—"}</li>
            <li className="list-item">Кадастровый номер: {objectData.cadastral_number || "—"}</li>
            <li className="list-item">Этажность: {objectData.floors_count ?? "—"}</li>
          </ul>
        </article>

        <article className="list-card glass-card">
          <h3 className="section-title">Связанные проекты</h3>
          <ul className="list">
            {relatedProjects.map((project) => (
              <li key={project.id} className="list-item">
                <Link to={`/projects/${project.id}`}>{project.contract_number || project.id}</Link>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="page-card glass-card">
        <h3 className="section-title">Материалы объекта</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Файл</th>
              <th>Категория</th>
              <th>Подпись</th>
            </tr>
          </thead>
          <tbody>
            {relatedFiles.map((item) => (
              <tr key={item.id}>
                <td>{item.original_name}</td>
                <td>{item.category}</td>
                <td>{item.caption || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {actionError ? <span className="error-text">{actionError}</span> : null}

      <ObjectCreateDrawer open={isEditOpen} onClose={() => setIsEditOpen(false)} initialObject={objectData} />
    </div>
  );
}
