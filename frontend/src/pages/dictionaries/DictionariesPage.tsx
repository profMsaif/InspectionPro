import { useMemo, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  type DictionaryItem,
  type DictionaryType,
  useCreateDictionaryItemMutation,
  useDictionaryItemsQuery,
  useUpdateDictionaryItemMutation,
} from "features/dictionaries/api";
import { useAuthStore } from "features/auth/authStore";
import { extractApiErrorMessage } from "shared/api/errors";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";

const dictionaryConfig: Array<{ type: DictionaryType; label: string }> = [
  { type: "object_type", label: "Типы объектов" },
  { type: "inspection_type", label: "Виды обследования" },
  { type: "element_type", label: "Типы элементов" },
  { type: "structural_system", label: "Конструктивные системы" },
  { type: "material", label: "Материалы" },
  { type: "condition_category", label: "Категории состояния" },
  { type: "defect_type", label: "Типы дефектов" },
  { type: "defect_severity", label: "Степени дефекта" },
  { type: "defect_cause", label: "Причины дефекта" },
  { type: "recommendation_type", label: "Рекомендации" },
  { type: "inspection_method", label: "Методы обследования" },
  { type: "measurement_type", label: "Типы измерений" },
  { type: "measurement_unit", label: "Единицы измерения" },
  { type: "device", label: "Приборы и оборудование" },
  { type: "element_inspection_status", label: "Статусы обследования элемента" },
];

type FormState = {
  id?: string;
  code: string;
  name_ru: string;
  name_en: string;
  description: string;
  sort_order: string;
  is_active: boolean;
};

function buildFormState(item?: DictionaryItem): FormState {
  return {
    id: item?.id,
    code: item?.code ?? "",
    name_ru: item?.name_ru ?? "",
    name_en: item?.name_en ?? "",
    description: item?.description ?? "",
    sort_order: item?.sort_order ? String(item.sort_order) : "",
    is_active: item?.is_active ?? true,
  };
}

export function DictionariesPage() {
  const role = useAuthStore((state) => state.role);
  const [selectedType, setSelectedType] = useState<DictionaryType>("object_type");
  const [editingItem, setEditingItem] = useState<DictionaryItem | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [form, setForm] = useState<FormState>(buildFormState());
  const [error, setError] = useState<string | null>(null);
  const dictionaryQuery = useDictionaryItemsQuery(selectedType, true);
  const createMutation = useCreateDictionaryItemMutation();
  const updateMutation = useUpdateDictionaryItemMutation();

  const items = useMemo(() => dictionaryQuery.data?.results ?? [], [dictionaryQuery.data?.results]);

  if (role !== "Admin" && role !== "Expert") {
    return <Navigate to="/" replace />;
  }

  if (dictionaryQuery.isLoading) {
    return <LoadingState />;
  }

  if (dictionaryQuery.isError) {
    return <ErrorState message="Не удалось загрузить экспертные справочники." />;
  }

  const resetForm = () => {
    setEditingItem(null);
    setForm(buildFormState());
    setIsFormOpen(false);
    setError(null);
  };

  const openCreateForm = () => {
    setEditingItem(null);
    setForm(buildFormState());
    setIsFormOpen(true);
    setError(null);
  };

  const openEditForm = (item: DictionaryItem) => {
    setEditingItem(item);
    setForm(buildFormState(item));
    setIsFormOpen(true);
    setError(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setError(null);
      const payload = {
        dictionary_type: selectedType,
        code: form.code,
        name_ru: form.name_ru,
        name_en: form.name_en,
        description: form.description,
        sort_order: form.sort_order ? Number(form.sort_order) : items.length + 1,
        is_active: form.is_active,
      };
      if (editingItem) {
        await updateMutation.mutateAsync({ id: editingItem.id, ...payload });
      } else {
        await createMutation.mutateAsync(payload);
      }
      resetForm();
    } catch (mutationError) {
      setError(extractApiErrorMessage(mutationError));
    }
  };

  const handleActiveToggle = async (item: DictionaryItem, isActive: boolean) => {
    try {
      setError(null);
      await updateMutation.mutateAsync({
        id: item.id,
        dictionary_type: item.dictionary_type,
        code: item.code,
        name_ru: item.name_ru,
        name_en: item.name_en,
        description: item.description,
        sort_order: item.sort_order,
        is_active: isActive,
      });
    } catch (mutationError) {
      setError(extractApiErrorMessage(mutationError));
    }
  };

  return (
    <div className="page-grid">
      <PageIntro
        title="Экспертная панель справочников"
        description="Эксперт и администратор управляют эталонными значениями, которые затем используются в формах инженеров и в паспорте объекта."
      />

      <section className="section-grid">
        <article className="page-card glass-card">
          <h3 className="section-title">Тип справочника</h3>
          <select className="input" value={selectedType} onChange={(event) => { setSelectedType(event.target.value as DictionaryType); resetForm(); }}>
            {dictionaryConfig.map((item) => (
              <option key={item.type} value={item.type}>
                {item.label}
              </option>
            ))}
          </select>
        </article>
      </section>

      <section className="page-card glass-card">
        {isFormOpen ? (
          <>
            <div className="section-header">
              <h3 className="section-title">{editingItem ? "Редактирование значения" : "Новое значение"}</h3>
              <button className="button" type="button" onClick={resetForm}>
                Назад к списку
              </button>
            </div>
            <form className="form-grid" onSubmit={handleSubmit}>
              <div className="field-grid">
                <div>
                  <label className="label">Код</label>
                  <input className="input" value={form.code} onChange={(event) => setForm((current) => ({ ...current, code: event.target.value }))} required />
                </div>
                <div>
                  <label className="label">Порядок</label>
                  <input className="input" type="number" value={form.sort_order} onChange={(event) => setForm((current) => ({ ...current, sort_order: event.target.value }))} />
                </div>
              </div>
              <div>
                <label className="label">Наименование</label>
                <input className="input" value={form.name_ru} onChange={(event) => setForm((current) => ({ ...current, name_ru: event.target.value }))} required />
              </div>
              <div>
                <label className="label">English name</label>
                <input className="input" value={form.name_en} onChange={(event) => setForm((current) => ({ ...current, name_en: event.target.value }))} />
              </div>
              <div>
                <label className="label">Описание</label>
                <textarea className="textarea" rows={3} value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} />
              </div>
              <label className="checkbox-row">
                <input type="checkbox" checked={form.is_active} onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.checked }))} />
                Активно для новых форм
              </label>
              {error ? <span className="error-text">{error}</span> : null}
              <div className="drawer-actions">
                <button className="button" type="button" onClick={resetForm}>
                  Отмена
                </button>
                <button className="button primary" type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                  {editingItem ? "Сохранить" : "Создать"}
                </button>
              </div>
            </form>
          </>
        ) : (
          <>
            <div className="section-header">
              <h3 className="section-title">Значения справочника</h3>
              <button className="button primary" type="button" onClick={openCreateForm}>
                Создать значение
              </button>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>Порядок</th>
                  <th>Код</th>
                  <th>Наименование</th>
                  <th>Активно</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.sort_order}</td>
                    <td>{item.code}</td>
                    <td>{item.name_ru}</td>
                    <td>
                      <input
                        type="checkbox"
                        checked={item.is_active}
                        onChange={(event) => handleActiveToggle(item, event.target.checked)}
                        disabled={updateMutation.isPending}
                      />
                    </td>
                    <td>
                      <div className="inline-actions">
                        <button className="button" type="button" onClick={() => openEditForm(item)}>
                          Изменить
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </section>
    </div>
  );
}
