import { useMemo, useState } from "react";

import { useDictionaryGroupsQuery } from "features/dictionaries/api";
import { useCreateElementMutation } from "features/elements/api";
import { useProjectsQuery } from "features/projects/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { DrawerPanel } from "shared/ui/DrawerPanel";

type ElementCreateDrawerProps = {
  open: boolean;
  onClose: () => void;
};

export function ElementCreateDrawer({ open, onClose }: ElementCreateDrawerProps) {
  const projectsQuery = useProjectsQuery();
  const dictionariesQuery = useDictionaryGroupsQuery([
    "element_type",
    "material",
    "inspection_method",
    "condition_category",
    "element_inspection_status",
    "recommendation_type",
  ]);
  const createElementMutation = useCreateElementMutation();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    project: "",
    element_type: "",
    element_type_dictionary: "",
    name: "",
    location: "",
    material: "",
    material_dictionary: "",
    inspection_method: "",
    inspection_method_dictionary: "",
    visual_condition: "работоспособное",
    has_defects: "no",
    no_defects_comment: "Видимых дефектов и повреждений не выявлено",
    condition_category: "",
    condition_category_dictionary: "",
    inspection_status_dictionary: "",
    conclusion: "Эксплуатация возможна",
    recommendation: "not_required",
    recommendation_dictionary: "",
  });

  const selectedProject = useMemo(
    () => projectsQuery.data?.results.find((project) => project.id === form.project),
    [form.project, projectsQuery.data?.results],
  );

  const updateField = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleClose = () => {
    setError(null);
    setForm({
      project: "",
      element_type: "",
      element_type_dictionary: "",
      name: "",
      location: "",
      material: "",
      material_dictionary: "",
      inspection_method: "",
      inspection_method_dictionary: "",
      visual_condition: "работоспособное",
      has_defects: "no",
      no_defects_comment: "Видимых дефектов и повреждений не выявлено",
      condition_category: "",
      condition_category_dictionary: "",
      inspection_status_dictionary: "",
      conclusion: "Эксплуатация возможна",
      recommendation: "not_required",
      recommendation_dictionary: "",
    });
    onClose();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedProject) {
      setError("Сначала выберите проект обследования.");
      return;
    }

    try {
      setError(null);
      await createElementMutation.mutateAsync({
        project: selectedProject.id,
        building_object: selectedProject.building_object,
        element_type: form.element_type,
        element_type_dictionary: form.element_type_dictionary || null,
        name: form.name,
        location: form.location,
        material: form.material,
        material_dictionary: form.material_dictionary || null,
        inspection_method: form.inspection_method,
        inspection_method_dictionary: form.inspection_method_dictionary || null,
        visual_condition: form.visual_condition,
        has_defects: form.has_defects === "yes",
        no_defects_comment: form.has_defects === "yes" ? "" : form.no_defects_comment,
        condition_category: form.condition_category,
        condition_category_dictionary: form.condition_category_dictionary || null,
        inspection_status_dictionary: form.inspection_status_dictionary || null,
        conclusion: form.conclusion,
        recommendation: form.recommendation,
        recommendation_dictionary: form.recommendation_dictionary || null,
      });
      handleClose();
    } catch (mutationError) {
      setError(extractApiErrorMessage(mutationError));
    }
  };

  return (
    <DrawerPanel
      open={open}
      onClose={handleClose}
      title="Добавить конструктивный элемент"
      description="Шаг 3 для инженера: заведите элемент в составе проекта даже в том случае, если видимых дефектов нет."
    >
      <form className="form-grid" onSubmit={handleSubmit}>
        <div>
          <label className="label" htmlFor="element-project">
            Проект обследования
          </label>
          <select
            id="element-project"
            className="input"
            value={form.project}
            onChange={(event) => updateField("project", event.target.value)}
            required
          >
            <option value="">Выберите проект</option>
            {(projectsQuery.data?.results ?? []).map((project) => (
              <option key={project.id} value={project.id}>
                {project.contract_number || project.building_object_name || project.id}
              </option>
            ))}
          </select>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="element-type">
              Тип элемента
            </label>
            <select
              id="element-type"
              className="input"
              value={form.element_type_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.element_type.find((item) => item.id === event.target.value);
                updateField("element_type_dictionary", event.target.value);
                updateField("element_type", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите тип элемента</option>
              {dictionariesQuery.data.element_type.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="element-name">
              Наименование
            </label>
            <input
              id="element-name"
              className="input"
              value={form.name}
              onChange={(event) => updateField("name", event.target.value)}
              required
            />
          </div>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="element-location">
              Расположение
            </label>
            <input
              id="element-location"
              className="input"
              value={form.location}
              onChange={(event) => updateField("location", event.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="element-material">
              Материал
            </label>
            <select
              id="element-material"
              className="input"
              value={form.material_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.material.find((item) => item.id === event.target.value);
                updateField("material_dictionary", event.target.value);
                updateField("material", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите материал</option>
              {dictionariesQuery.data.material.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="element-defects">
              Дефекты выявлены
            </label>
            <select
              id="element-defects"
              className="input"
              value={form.has_defects}
              onChange={(event) => updateField("has_defects", event.target.value)}
            >
              <option value="no">Нет</option>
              <option value="yes">Да</option>
            </select>
          </div>
          <div>
            <label className="label" htmlFor="element-category">
              Категория состояния
            </label>
            <select
              id="element-category"
              className="input"
              value={form.condition_category_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.condition_category.find((item) => item.id === event.target.value);
                updateField("condition_category_dictionary", event.target.value);
                updateField("condition_category", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите категорию</option>
              {dictionariesQuery.data.condition_category.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="element-inspection-status">
              Статус обследования
            </label>
            <select
              id="element-inspection-status"
              className="input"
              value={form.inspection_status_dictionary}
              onChange={(event) => updateField("inspection_status_dictionary", event.target.value)}
              required
            >
              <option value="">Выберите статус</option>
              {dictionariesQuery.data.element_inspection_status.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="element-method">
              Метод обследования
            </label>
            <select
              id="element-method"
              className="input"
              value={form.inspection_method_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.inspection_method.find((item) => item.id === event.target.value);
                updateField("inspection_method_dictionary", event.target.value);
                updateField("inspection_method", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите метод</option>
              {dictionariesQuery.data.inspection_method.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
        </div>

        {form.has_defects === "no" ? (
          <div>
            <label className="label" htmlFor="element-no-defects">
              Комментарий при отсутствии дефектов
            </label>
            <textarea
              id="element-no-defects"
              className="textarea"
              rows={2}
              value={form.no_defects_comment}
              onChange={(event) => updateField("no_defects_comment", event.target.value)}
            />
          </div>
        ) : null}

        <div>
          <label className="label" htmlFor="element-conclusion">
            Вывод по элементу
          </label>
          <textarea
            id="element-conclusion"
            className="textarea"
            rows={3}
            value={form.conclusion}
            onChange={(event) => updateField("conclusion", event.target.value)}
          />
        </div>

        <div>
          <label className="label" htmlFor="element-recommendation">
            Рекомендация
          </label>
          <select
            id="element-recommendation"
            className="input"
            value={form.recommendation_dictionary}
            onChange={(event) => {
              const selectedItem = dictionariesQuery.data.recommendation_type.find((item) => item.id === event.target.value);
              updateField("recommendation_dictionary", event.target.value);
              updateField("conclusion", selectedItem?.name_ru ?? form.conclusion);
            }}
            required
          >
            <option value="">Выберите рекомендацию</option>
            {dictionariesQuery.data.recommendation_type.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name_ru}
              </option>
            ))}
          </select>
        </div>

        {error ? <span className="error-text">{error}</span> : null}

        <div className="drawer-actions">
          <button className="button" type="button" onClick={handleClose}>
            Отмена
          </button>
          <button className="button primary" type="submit" disabled={createElementMutation.isPending}>
            {createElementMutation.isPending ? "Сохраняем..." : "Добавить элемент"}
          </button>
        </div>
      </form>
    </DrawerPanel>
  );
}
