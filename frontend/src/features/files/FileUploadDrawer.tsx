import { useMemo, useState } from "react";

import { appendixTypeOptions, useUploadInspectionFileMutation } from "features/files/api";
import type { Defect } from "features/defects/api";
import type { StructuralElement } from "features/elements/api";
import type { Measurement } from "features/measurements/api";
import type { InspectionProject } from "features/projects/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { DrawerPanel } from "shared/ui/DrawerPanel";

type FileUploadDrawerProps = {
  open: boolean;
  onClose: () => void;
  project: InspectionProject;
  elements: StructuralElement[];
  defects: Defect[];
  measurements: Measurement[];
};

export function FileUploadDrawer({ open, onClose, project, elements, defects, measurements }: FileUploadDrawerProps) {
  const uploadMutation = useUploadInspectionFileMutation(project.id);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    category: "element",
    appendix_type: "",
    structural_element: "",
    defect: "",
    measurement: "",
    caption: "",
    is_for_report: true,
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const filteredDefects = useMemo(
    () => defects.filter((item) => !form.structural_element || item.structural_element === form.structural_element),
    [defects, form.structural_element],
  );
  const filteredMeasurements = useMemo(
    () => measurements.filter((item) => !form.structural_element || item.structural_element === form.structural_element),
    [measurements, form.structural_element],
  );

  const reset = () => {
    setForm({
      category: "element",
      appendix_type: "",
      structural_element: "",
      defect: "",
      measurement: "",
      caption: "",
      is_for_report: true,
    });
    setSelectedFile(null);
    setError(null);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const updateField = (field: keyof typeof form, value: string | boolean) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) {
      setError("Выберите файл или фотографию.");
      return;
    }

    try {
      setError(null);
      await uploadMutation.mutateAsync({
        file: selectedFile,
        category: form.category,
        appendix_type: form.category === "project" ? form.appendix_type || undefined : undefined,
        project: project.id,
        building_object: project.building_object,
        structural_element: form.category === "element" || form.category === "defect" || form.category === "measurement" ? form.structural_element || undefined : undefined,
        defect: form.category === "defect" ? form.defect || undefined : undefined,
        measurement: form.category === "measurement" ? form.measurement || undefined : undefined,
        caption: form.caption,
        is_for_report: form.is_for_report,
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
      title="Загрузить фото или файл"
      description="Привяжите материал к проекту, элементу, дефекту или измерению и отметьте, нужно ли включать его в отчёт."
    >
      <form className="form-grid" onSubmit={handleSubmit}>
        <div className="field-grid">
          <div>
            <label className="label" htmlFor="file-category">
              Категория
            </label>
            <select
              id="file-category"
              className="input"
              value={form.category}
              onChange={(event) => {
                updateField("category", event.target.value);
                if (event.target.value !== "project") {
                  updateField("appendix_type", "");
                }
              }}
            >
              <option value="object">Объект</option>
              <option value="project">Проект</option>
              <option value="element">Элемент</option>
              <option value="defect">Дефект</option>
              <option value="measurement">Измерение</option>
            </select>
          </div>
          <div>
            <label className="label" htmlFor="file-upload">
              Файл
            </label>
            <input id="file-upload" className="input" type="file" onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} required />
          </div>
        </div>

        {form.category === "project" ? (
          <div>
            <label className="label" htmlFor="file-appendix-type">
              Тип приложения
            </label>
            <select
              id="file-appendix-type"
              className="input"
              value={form.appendix_type}
              onChange={(event) => updateField("appendix_type", event.target.value)}
            >
              <option value="">Без отдельного типа</option>
              {appendixTypeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        ) : null}

        {(form.category === "element" || form.category === "defect" || form.category === "measurement") ? (
          <div>
            <label className="label" htmlFor="file-element">
              Элемент
            </label>
            <select
              id="file-element"
              className="input"
              value={form.structural_element}
              onChange={(event) => {
                updateField("structural_element", event.target.value);
                updateField("defect", "");
                updateField("measurement", "");
              }}
              required
            >
              <option value="">Выберите элемент</option>
              {elements.map((element) => (
                <option key={element.id} value={element.id}>
                  {element.name}
                </option>
              ))}
            </select>
          </div>
        ) : null}

        {form.category === "defect" ? (
          <div>
            <label className="label" htmlFor="file-defect">
              Дефект
            </label>
            <select
              id="file-defect"
              className="input"
              value={form.defect}
              onChange={(event) => updateField("defect", event.target.value)}
              required
            >
              <option value="">Выберите дефект</option>
              {filteredDefects.map((defect) => (
                <option key={defect.id} value={defect.id}>
                  {defect.title}
                </option>
              ))}
            </select>
          </div>
        ) : null}

        {form.category === "measurement" ? (
          <div>
            <label className="label" htmlFor="file-measurement">
              Измерение
            </label>
            <select
              id="file-measurement"
              className="input"
              value={form.measurement}
              onChange={(event) => updateField("measurement", event.target.value)}
              required
            >
              <option value="">Выберите измерение</option>
              {filteredMeasurements.map((measurement) => (
                <option key={measurement.id} value={measurement.id}>
                  {measurement.measurement_type} ({measurement.value} {measurement.unit})
                </option>
              ))}
            </select>
          </div>
        ) : null}

        <div>
          <label className="label" htmlFor="file-caption">
            Подпись
          </label>
          <input
            id="file-caption"
            className="input"
            value={form.caption}
            onChange={(event) => updateField("caption", event.target.value)}
          />
        </div>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.is_for_report}
            onChange={(event) => updateField("is_for_report", event.target.checked)}
          />
          <span>Включать в отчёт</span>
        </label>

        {error ? <span className="error-text">{error}</span> : null}

        <div className="drawer-actions">
          <button className="button" type="button" onClick={handleClose}>
            Отмена
          </button>
          <button className="button primary" type="submit" disabled={uploadMutation.isPending}>
            {uploadMutation.isPending ? "Загружаем..." : "Загрузить"}
          </button>
        </div>
      </form>
    </DrawerPanel>
  );
}
