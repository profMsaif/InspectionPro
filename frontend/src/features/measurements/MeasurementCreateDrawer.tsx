import { useMemo, useState } from "react";

import { useDictionaryGroupsQuery } from "features/dictionaries/api";
import { useElementsQuery } from "features/elements/api";
import { useCreateMeasurementMutation } from "features/measurements/api";
import { useProjectsQuery } from "features/projects/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { DrawerPanel } from "shared/ui/DrawerPanel";

type MeasurementCreateDrawerProps = {
  open: boolean;
  onClose: () => void;
};

function defaultMeasuredAt() {
  const now = new Date();
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
}

export function MeasurementCreateDrawer({ open, onClose }: MeasurementCreateDrawerProps) {
  const projectsQuery = useProjectsQuery();
  const elementsQuery = useElementsQuery();
  const dictionariesQuery = useDictionaryGroupsQuery([
    "measurement_type",
    "measurement_unit",
    "inspection_method",
    "device",
  ]);
  const createMeasurementMutation = useCreateMeasurementMutation();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    project: "",
    structural_element: "",
    measurement_type: "",
    measurement_type_dictionary: "",
    value: "",
    unit: "",
    unit_dictionary: "",
    location: "",
    measured_at: defaultMeasuredAt(),
    method: "",
    method_dictionary: "",
    device: "",
    device_dictionary: "",
    comment: "",
  });

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
      measurement_type: "",
      measurement_type_dictionary: "",
      value: "",
      unit: "",
      unit_dictionary: "",
      location: "",
      measured_at: defaultMeasuredAt(),
      method: "",
      method_dictionary: "",
      device: "",
      device_dictionary: "",
      comment: "",
    });
    onClose();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setError(null);
      await createMeasurementMutation.mutateAsync({
        project: form.project,
        structural_element: form.structural_element,
        measurement_type: form.measurement_type,
        measurement_type_dictionary: form.measurement_type_dictionary || null,
        value: form.value,
        unit: form.unit,
        unit_dictionary: form.unit_dictionary || null,
        location: form.location,
        measured_at: form.measured_at,
        method: form.method,
        method_dictionary: form.method_dictionary || null,
        device: form.device,
        device_dictionary: form.device_dictionary || null,
        comment: form.comment,
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
      title="Добавить измерение"
      description="Шаг 5: зафиксируйте инструментальные замеры после осмотра элемента или дефекта."
    >
      <form className="form-grid" onSubmit={handleSubmit}>
        <div className="field-grid">
          <div>
            <label className="label" htmlFor="measurement-project">
              Проект
            </label>
            <select
              id="measurement-project"
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
            <label className="label" htmlFor="measurement-element">
              Элемент
            </label>
            <select
              id="measurement-element"
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
            <label className="label" htmlFor="measurement-type">
              Тип измерения
            </label>
            <select
              id="measurement-type"
              className="input"
              value={form.measurement_type_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.measurement_type.find((item) => item.id === event.target.value);
                updateField("measurement_type_dictionary", event.target.value);
                updateField("measurement_type", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите тип измерения</option>
              {dictionariesQuery.data.measurement_type.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="measurement-value">
              Значение
            </label>
            <input
              id="measurement-value"
              className="input"
              value={form.value}
              onChange={(event) => updateField("value", event.target.value)}
              required
            />
          </div>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="measurement-unit">
              Единица
            </label>
            <select
              id="measurement-unit"
              className="input"
              value={form.unit_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.measurement_unit.find((item) => item.id === event.target.value);
                updateField("unit_dictionary", event.target.value);
                updateField("unit", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите единицу</option>
              {dictionariesQuery.data.measurement_unit.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="measurement-date">
              Дата и время
            </label>
            <input
              id="measurement-date"
              className="input"
              type="datetime-local"
              value={form.measured_at}
              onChange={(event) => updateField("measured_at", event.target.value)}
              required
            />
          </div>
        </div>

        <div>
          <label className="label" htmlFor="measurement-location">
            Место измерения
          </label>
          <input
            id="measurement-location"
            className="input"
            value={form.location}
            onChange={(event) => updateField("location", event.target.value)}
          />
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="measurement-method">
              Метод обследования
            </label>
            <select
              id="measurement-method"
              className="input"
              value={form.method_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.inspection_method.find((item) => item.id === event.target.value);
                updateField("method_dictionary", event.target.value);
                updateField("method", selectedItem?.name_ru ?? "");
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
          <div>
            <label className="label" htmlFor="measurement-device">
              Прибор
            </label>
            <select
              id="measurement-device"
              className="input"
              value={form.device_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.device.find((item) => item.id === event.target.value);
                updateField("device_dictionary", event.target.value);
                updateField("device", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите прибор</option>
              {dictionariesQuery.data.device.map((item) => (
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
          <button className="button primary" type="submit" disabled={createMeasurementMutation.isPending}>
            {createMeasurementMutation.isPending ? "Сохраняем..." : "Добавить измерение"}
          </button>
        </div>
      </form>
    </DrawerPanel>
  );
}
