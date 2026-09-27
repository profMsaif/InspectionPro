import { useEffect, useState } from "react";

import { useDictionaryGroupsQuery } from "features/dictionaries/api";
import { useCreateObjectMutation, useUpdateObjectMutation, type BuildingObject } from "features/objects/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { DrawerPanel } from "shared/ui/DrawerPanel";

type ObjectCreateDrawerProps = {
  open: boolean;
  onClose: () => void;
  initialObject?: BuildingObject;
};

export function ObjectCreateDrawer({ open, onClose, initialObject }: ObjectCreateDrawerProps) {
  const dictionariesQuery = useDictionaryGroupsQuery(["object_type", "structural_system", "material"]);
  const [form, setForm] = useState({
    name: initialObject?.name ?? "",
    address: initialObject?.address ?? "",
    object_type: initialObject?.object_type ?? "",
    object_type_dictionary: initialObject?.object_type_dictionary ?? "",
    purpose: initialObject?.purpose ?? "",
    construction_year: initialObject?.construction_year ? String(initialObject.construction_year) : "",
    structural_system_dictionary: initialObject?.structural_system_dictionary ?? "",
    main_material_dictionary: initialObject?.main_material_dictionary ?? "",
  });
  const [error, setError] = useState<string | null>(null);
  const createObjectMutation = useCreateObjectMutation();
  const updateObjectMutation = useUpdateObjectMutation();
  const isEditMode = Boolean(initialObject);

  useEffect(() => {
    if (!open) {
      return;
    }
    setForm({
      name: initialObject?.name ?? "",
      address: initialObject?.address ?? "",
      object_type: initialObject?.object_type ?? "",
      object_type_dictionary: initialObject?.object_type_dictionary ?? "",
      purpose: initialObject?.purpose ?? "",
      construction_year: initialObject?.construction_year ? String(initialObject.construction_year) : "",
      structural_system_dictionary: initialObject?.structural_system_dictionary ?? "",
      main_material_dictionary: initialObject?.main_material_dictionary ?? "",
    });
    setError(null);
  }, [initialObject, open]);

  const updateField = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const reset = () => {
    setForm({
      name: initialObject?.name ?? "",
      address: initialObject?.address ?? "",
      object_type: initialObject?.object_type ?? "",
      object_type_dictionary: initialObject?.object_type_dictionary ?? "",
      purpose: initialObject?.purpose ?? "",
      construction_year: initialObject?.construction_year ? String(initialObject.construction_year) : "",
      structural_system_dictionary: initialObject?.structural_system_dictionary ?? "",
      main_material_dictionary: initialObject?.main_material_dictionary ?? "",
    });
    setError(null);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setError(null);
      if (isEditMode && initialObject) {
        await updateObjectMutation.mutateAsync({
          ...initialObject,
          name: form.name,
          address: form.address,
          object_type: form.object_type,
          object_type_dictionary: form.object_type_dictionary || null,
          purpose: form.purpose || undefined,
          construction_year: form.construction_year ? Number(form.construction_year) : null,
          structural_system_dictionary: form.structural_system_dictionary || null,
          main_material_dictionary: form.main_material_dictionary || null,
        });
      } else {
        await createObjectMutation.mutateAsync({
          name: form.name,
          address: form.address,
          object_type: form.object_type,
          object_type_dictionary: form.object_type_dictionary || null,
          purpose: form.purpose || undefined,
          construction_year: form.construction_year ? Number(form.construction_year) : null,
          structural_system_dictionary: form.structural_system_dictionary || null,
          main_material_dictionary: form.main_material_dictionary || null,
        });
      }
      handleClose();
    } catch (mutationError) {
      setError(extractApiErrorMessage(mutationError));
    }
  };

  return (
    <DrawerPanel
      open={open}
      onClose={handleClose}
      title={isEditMode ? "Редактировать объект" : "Создать объект"}
      description={
        isEditMode
          ? "Обновите карточку объекта, чтобы проектные данные и отчёты оставались актуальными."
          : "Шаг 1 для менеджера: зарегистрируйте объект, чтобы затем открыть по нему проект обследования."
      }
    >
      <form className="form-grid" onSubmit={handleSubmit}>
        <div className="field-grid">
          <div>
            <label className="label" htmlFor="object-name">
              Наименование
            </label>
            <input
              id="object-name"
              className="input"
              value={form.name}
              onChange={(event) => updateField("name", event.target.value)}
              required
            />
          </div>
          <div>
            <label className="label" htmlFor="object-type">
              Тип объекта
            </label>
            <select
              id="object-type"
              className="input"
              value={form.object_type_dictionary}
              onChange={(event) => {
                const selectedItem = dictionariesQuery.data.object_type.find((item) => item.id === event.target.value);
                updateField("object_type_dictionary", event.target.value);
                updateField("object_type", selectedItem?.name_ru ?? "");
              }}
              required
            >
              <option value="">Выберите тип объекта</option>
              {dictionariesQuery.data.object_type.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="label" htmlFor="object-address">
            Адрес
          </label>
          <input
            id="object-address"
            className="input"
            value={form.address}
            onChange={(event) => updateField("address", event.target.value)}
            required
          />
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="object-purpose">
              Назначение
            </label>
            <input
              id="object-purpose"
              className="input"
              value={form.purpose}
              onChange={(event) => updateField("purpose", event.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="object-structural-system">
              Конструктивная система
            </label>
            <select
              id="object-structural-system"
              className="input"
              value={form.structural_system_dictionary}
              onChange={(event) => updateField("structural_system_dictionary", event.target.value)}
            >
              <option value="">Выберите систему</option>
              {dictionariesQuery.data.structural_system.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="field-grid">
          <div>
            <label className="label" htmlFor="object-main-material">
              Основной материал
            </label>
            <select
              id="object-main-material"
              className="input"
              value={form.main_material_dictionary}
              onChange={(event) => updateField("main_material_dictionary", event.target.value)}
            >
              <option value="">Выберите материал</option>
              {dictionariesQuery.data.material.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name_ru}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="object-year">
              Год постройки
            </label>
            <input
              id="object-year"
              className="input"
              type="number"
              value={form.construction_year}
              onChange={(event) => updateField("construction_year", event.target.value)}
            />
          </div>
        </div>

        {error ? <span className="error-text">{error}</span> : null}

        <div className="drawer-actions">
          <button className="button" type="button" onClick={handleClose}>
            Отмена
          </button>
          <button className="button primary" type="submit" disabled={createObjectMutation.isPending || updateObjectMutation.isPending}>
            {createObjectMutation.isPending || updateObjectMutation.isPending
              ? "Сохраняем..."
              : isEditMode
                ? "Сохранить изменения"
                : "Создать объект"}
          </button>
        </div>
      </form>
    </DrawerPanel>
  );
}
