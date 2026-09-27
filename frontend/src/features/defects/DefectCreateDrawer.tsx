import { useMemo, useState } from "react";

import { useDictionaryGroupsQuery } from "features/dictionaries/api";
import { useCreateDefectMutation } from "features/defects/api";
import { useElementsQuery } from "features/elements/api";
import { useProjectsQuery } from "features/projects/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { DrawerPanel } from "shared/ui/DrawerPanel";

type DefectCreateDrawerProps = {
  open: boolean;
  onClose: () => void;
};

export function DefectCreateDrawer({ open, onClose }: DefectCreateDrawerProps) {
  const projectsQuery = useProjectsQuery();
  const elementsQuery = useElementsQuery();
  const dictionariesQuery = useDictionaryGroupsQuery([
    "defect_type",
    "defect_severity",
    "defect_cause",
    "condition_category",
    "recommendation_type",
  ]);
  const createDefectMutation = useCreateDefectMutation();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    project: "",
    structural_element: "",
    defect_type: "",
    defect_type_dictionary: "",
    title: "",
    description: "",
    location: "",
    floor: "",
    severity: "",
    severity_dictionary: "",
    probable_cause: "",
    probable_cause_dictionary: "",
    preliminary_condition_category: "",
    preliminary_condition_category_dictionary: "",
    final_condition_category: "",
    final_condition_category_dictionary: "",
    recommendation: "",
    recommendation_dictionary: "",
  });

  const selectedProject = useMemo(
    () => projectsQuery.data?.results.find((project) => project.id === form.project),
    [form.project, projectsQuery.data?.results],
  );

  const availableElements = useMemo(
    () => (elementsQuery.data?.results ?? []).filter((element) => element.project === form.project),
    [elementsQuery.data?.results, form.project],
  );

  const updateField = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleClose = () => {
    setError(null);
    setForm({
      project: "",
      structural_element: "",
      defect_type: "",
      defect_type_dictionary: "",
      title: "",
      description: "",
      location: "",
      floor: "",
      severity: "",
      severity_dictionary: "",
      probable_cause: "",
      probable_cause_dictionary: "",
      preliminary_condition_category: "",
      preliminary_condition_category_dictionary: "",
      final_condition_category: "",
      final_condition_category_dictionary: "",
      recommendation: "",
      recommendation_dictionary: "",
    });
    onClose();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedProject) {
      setError("Выберите проект обследования.");
      return;
    }

    try {
      setError(null);
      await createDefectMutation.mutateAsync({
        project: selectedProject.id,
        building_object: selectedProject.building_object,
        structural_element: form.structural_element,
        defect_type: form.defect_type,
        defect_type_dictionary: form.defect_type_dictionary || null,
        title: form.title,
        description: form.description,
        location: form.location,
        floor: form.floor,
        severity: form.severity,
        severity_dictionary: form.severity_dictionary || null,
        probable_cause: form.probable_cause,
        probable_cause_dictionary: form.probable_cause_dictionary || null,
        preliminary_condition_category: form.preliminary_condition_category,
        preliminary_condition_category_dictionary: form.preliminary_condition_category_dictionary || null,
        final_condition_category: form.final_condition_category,
        final_condition_category_dictionary: form.final_condition_category_dictionary || null,
        recommendation: form.recommendation,
        recommendation_dictionary: form.recommendation_dictionary || null,
        status: "Confirmed",
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
      title="Добавить дефект"
      description="Шаг 4: после оценки элемента зафиксируйте дефект отдельной записью и привяжите его к нужной конструкции."
    >
      <form className="form-grid" onSubmit={handleSubmit}>
        <div className="field-grid">
          <div>
            <label className="label" htmlFor="defect-project">
              Проект
            </label>
            <select
              id="defect-project"
              className="input"
              value={form.project}
              onChange={(event) => {
                updateField("project", event.target.value);
                updateField("structural_element", "");
              }}
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
          <div>
            <label className="label" htmlFor="defect-element">
              Элемент
            </label>
            <select
              id="defect-element"
              className="input"
              value={form.structural_element}
              onChange={(event) => updateField("structural_element", event.target.value)}
              required
            >
              <option value="">Выберите элемент</option>
              {availableElements.map((element) => (
                <option key={element.id} value={element.id}>
                  {element.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="defect-title">
              Заголовок дефекта
            </label>
            <input
              id="defect-title"
              className="input"
              value={form.title}
              onChange={(event) => updateField("title", event.target.value)}
              required
            />
          </div>
          <div>
            <label className="label" htmlFor="defect-type">
              Тип дефекта
            </label>
            <select
              id="defect-type"
              className="input"
              value={form.defect_type_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.defect_type.find((item) => item.id === event.target.value);
                updateField("defect_type_dictionary", event.target.value);
                updateField("defect_type", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите тип дефекта</option>
              {dictionariesQuery.data.defect_type.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="label" htmlFor="defect-description">
            Описание
          </label>
          <textarea
            id="defect-description"
            className="textarea"
            rows={3}
            value={form.description}
            onChange={(event) => updateField("description", event.target.value)}
            required
          />
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="defect-severity">
              Степень дефекта
            </label>
            <select
              id="defect-severity"
              className="input"
              value={form.severity_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.defect_severity.find((item) => item.id === event.target.value);
                updateField("severity_dictionary", event.target.value);
                updateField("severity", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите степень</option>
              {dictionariesQuery.data.defect_severity.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="defect-location">
              Расположение
            </label>
            <input
              id="defect-location"
              className="input"
              value={form.location}
              onChange={(event) => updateField("location", event.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="defect-floor">
              Этаж / зона
            </label>
            <input
              id="defect-floor"
              className="input"
              value={form.floor}
              onChange={(event) => updateField("floor", event.target.value)}
            />
          </div>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="defect-cause">
              Вероятная причина
            </label>
            <select
              id="defect-cause"
              className="input"
              value={form.probable_cause_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.defect_cause.find((item) => item.id === event.target.value);
                updateField("probable_cause_dictionary", event.target.value);
                updateField("probable_cause", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите причину</option>
              {dictionariesQuery.data.defect_cause.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="defect-category">
              Категория состояния
            </label>
            <select
              id="defect-category"
              className="input"
              value={form.final_condition_category_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.condition_category.find((item) => item.id === event.target.value);
                updateField("final_condition_category_dictionary", event.target.value);
                updateField("preliminary_condition_category_dictionary", event.target.value);
                updateField("final_condition_category", selectedItem?.name_ru ?? "");
                updateField("preliminary_condition_category", selectedItem?.name_ru ?? "");
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
            <label className="label" htmlFor="defect-recommendation">
              Рекомендация
            </label>
            <select
              id="defect-recommendation"
              className="input"
              value={form.recommendation_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.recommendation_type.find((item) => item.id === event.target.value);
                updateField("recommendation_dictionary", event.target.value);
                updateField("recommendation", selectedItem?.name_ru ?? "");
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
        </div>

        {error ? <span className="error-text">{error}</span> : null}

        <div className="drawer-actions">
          <button className="button" type="button" onClick={handleClose}>
            Отмена
          </button>
          <button className="button primary" type="submit" disabled={createDefectMutation.isPending}>
            {createDefectMutation.isPending ? "Сохраняем..." : "Добавить дефект"}
          </button>
        </div>
      </form>
    </DrawerPanel>
  );
}
