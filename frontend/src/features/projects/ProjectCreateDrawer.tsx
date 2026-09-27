import { useMemo, useState } from "react";

import { useDictionaryItemsQuery } from "features/dictionaries/api";
import { useObjectsQuery } from "features/objects/api";
import { useCreateProjectMutation } from "features/projects/api";
import { useReportTemplatesQuery } from "features/reports/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { DrawerPanel } from "shared/ui/DrawerPanel";

type ProjectCreateDrawerProps = {
  open: boolean;
  onClose: () => void;
};

export function ProjectCreateDrawer({ open, onClose }: ProjectCreateDrawerProps) {
  const objectsQuery = useObjectsQuery();
  const inspectionTypesQuery = useDictionaryItemsQuery("inspection_type");
  const reportTemplatesQuery = useReportTemplatesQuery();
  const createProjectMutation = useCreateProjectMutation();
  const [error, setError] = useState<string | null>(null);
  const availableObjects = objectsQuery.data?.results ?? [];
  const [form, setForm] = useState({
    building_object: "",
    customer_name: "",
    contract_number: "",
    inspection_reason: "",
    inspection_goal: "",
    inspection_type: "",
    inspection_type_dictionary: "",
    start_date: "",
    end_date: "",
    report_template: "",
  });

  const canSubmit = useMemo(
    () => Boolean(form.building_object && form.customer_name && form.inspection_reason && form.inspection_goal && form.inspection_type_dictionary),
    [form],
  );

  const updateField = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleClose = () => {
    setError(null);
    setForm({
      building_object: "",
      customer_name: "",
      contract_number: "",
      inspection_reason: "",
      inspection_goal: "",
      inspection_type: "",
      inspection_type_dictionary: "",
      start_date: "",
      end_date: "",
      report_template: "",
    });
    onClose();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setError(null);
      await createProjectMutation.mutateAsync({
        building_object: form.building_object,
        customer_name: form.customer_name,
        contract_number: form.contract_number,
        inspection_reason: form.inspection_reason,
        inspection_goal: form.inspection_goal,
        inspection_type: form.inspection_type,
        inspection_type_dictionary: form.inspection_type_dictionary || null,
        start_date: form.start_date || null,
        end_date: form.end_date || null,
        report_template: form.report_template || null,
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
      title="Создать проект обследования"
      description="Шаг 2: выберите объект, зафиксируйте заказчика и основание работ. После этого инженер сможет вести обследование."
    >
      <form className="form-grid" onSubmit={handleSubmit}>
        <div>
          <label className="label" htmlFor="project-object">
            Объект
          </label>
          <select
            id="project-object"
            className="input"
            value={form.building_object}
            onChange={(event) => updateField("building_object", event.target.value)}
            required
          >
            <option value="">Выберите объект</option>
            {availableObjects.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="project-customer">
              Заказчик
            </label>
            <input
              id="project-customer"
              className="input"
              value={form.customer_name}
              onChange={(event) => updateField("customer_name", event.target.value)}
              required
            />
          </div>
          <div>
            <label className="label" htmlFor="project-contract">
              Номер договора
            </label>
            <input
              id="project-contract"
              className="input"
              value={form.contract_number}
              onChange={(event) => updateField("contract_number", event.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="label" htmlFor="project-reason">
            Основание обследования
          </label>
          <textarea
            id="project-reason"
            className="textarea"
            rows={3}
            value={form.inspection_reason}
            onChange={(event) => updateField("inspection_reason", event.target.value)}
            required
          />
        </div>

        <div>
          <label className="label" htmlFor="project-goal">
            Цель обследования
          </label>
          <textarea
            id="project-goal"
            className="textarea"
            rows={3}
            value={form.inspection_goal}
            onChange={(event) => updateField("inspection_goal", event.target.value)}
            required
          />
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="project-type">
              Вид обследования
            </label>
            <select
              id="project-type"
              className="input"
              value={form.inspection_type_dictionary}
              onChange={(event) => {
                const selectedItem = inspectionTypesQuery.data?.results.find((item) => item.id === event.target.value);
                updateField("inspection_type_dictionary", event.target.value);
                updateField("inspection_type", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите вид обследования</option>
              {(inspectionTypesQuery.data?.results ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="project-start">
              Дата начала
            </label>
            <input
              id="project-start"
              className="input"
              type="date"
              value={form.start_date}
              onChange={(event) => updateField("start_date", event.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="label" htmlFor="project-template">
            Шаблон отчёта
          </label>
          <select
            id="project-template"
            className="input"
            value={form.report_template}
            onChange={(event) => updateField("report_template", event.target.value)}
          >
            <option value="">Шаблон по умолчанию</option>
            {(reportTemplatesQuery.data?.results ?? [])
              .filter((item) => item.is_active)
              .map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
          </select>
        </div>

        <div>
          <label className="label" htmlFor="project-end">
            Дата окончания
          </label>
          <input
            id="project-end"
            className="input"
            type="date"
            value={form.end_date}
            onChange={(event) => updateField("end_date", event.target.value)}
          />
        </div>

        {availableObjects.length === 0 ? <span className="error-text">Сначала создайте объект, затем можно открыть проект.</span> : null}
        {error ? <span className="error-text">{error}</span> : null}

        <div className="drawer-actions">
          <button className="button" type="button" onClick={handleClose}>
            Отмена
          </button>
          <button className="button primary" type="submit" disabled={!canSubmit || createProjectMutation.isPending}>
            {createProjectMutation.isPending ? "Сохраняем..." : "Создать проект"}
          </button>
        </div>
      </form>
    </DrawerPanel>
  );
}
