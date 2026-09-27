import { useEffect, useMemo, useState } from "react";
import { Navigate } from "react-router-dom";

import { useAuthStore } from "features/auth/authStore";
import {
  type ReportTemplate,
  type ReportTemplateBlock,
  useCreateReportTemplateMutation,
  useReportTemplatesQuery,
  useUpdateReportTemplateBlockMutation,
  useUpdateReportTemplateMutation,
} from "features/reports/api";
import { extractApiErrorMessage } from "shared/api/errors";
import { ErrorState } from "shared/ui/ErrorState";
import { LoadingState } from "shared/ui/LoadingState";
import { PageIntro } from "shared/ui/PageIntro";

type TemplateFormState = {
  id?: string;
  code: string;
  name: string;
  description: string;
  is_active: boolean;
  is_default: boolean;
};

function buildTemplateForm(template?: ReportTemplate): TemplateFormState {
  return {
    id: template?.id,
    code: template?.code ?? "",
    name: template?.name ?? "",
    description: template?.description ?? "",
    is_active: template?.is_active ?? true,
    is_default: template?.is_default ?? false,
  };
}

export function ReportTemplatesPage() {
  const role = useAuthStore((state) => state.role);
  const templatesQuery = useReportTemplatesQuery();
  const createTemplateMutation = useCreateReportTemplateMutation();
  const updateTemplateMutation = useUpdateReportTemplateMutation();
  const updateBlockMutation = useUpdateReportTemplateBlockMutation();
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [draggingBlockId, setDraggingBlockId] = useState<string | null>(null);
  const [form, setForm] = useState<TemplateFormState>(buildTemplateForm());
  const [error, setError] = useState<string | null>(null);

  const templates = templatesQuery.data?.results ?? [];
  const selectedTemplate = useMemo(() => {
    const fallback = templates[0] ?? null;
    return templates.find((item) => item.id === selectedTemplateId) ?? fallback;
  }, [selectedTemplateId, templates]);

  const blocks = useMemo(
    () => [...(selectedTemplate?.blocks ?? [])].sort((left, right) => left.sort_order - right.sort_order),
    [selectedTemplate?.blocks],
  );

  useEffect(() => {
    if (selectedTemplate && !form.id && !isCreatingNew) {
      setForm(buildTemplateForm(selectedTemplate));
      setSelectedTemplateId(selectedTemplate.id);
    }
  }, [form.id, isCreatingNew, selectedTemplate]);

  if (role !== "Admin" && role !== "Expert") {
    return <Navigate to="/" replace />;
  }

  if (templatesQuery.isLoading) {
    return <LoadingState />;
  }

  if (templatesQuery.isError) {
    return <ErrorState message="Не удалось загрузить шаблоны отчётов." />;
  }

  const openTemplate = (template: ReportTemplate) => {
    setIsCreatingNew(false);
    setSelectedTemplateId(template.id);
    setForm(buildTemplateForm(template));
    setError(null);
  };

  const resetTemplateForm = () => {
    setIsCreatingNew(true);
    setSelectedTemplateId(null);
    setForm(buildTemplateForm());
    setError(null);
  };

  const handleTemplateSave = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setError(null);
      if (form.id) {
        await updateTemplateMutation.mutateAsync(form);
      } else {
        const created = await createTemplateMutation.mutateAsync(form);
        setIsCreatingNew(false);
        setSelectedTemplateId(created.id);
      }
    } catch (mutationError) {
      setError(extractApiErrorMessage(mutationError));
    }
  };

  const updateBlock = async (block: ReportTemplateBlock, patch: Partial<ReportTemplateBlock>) => {
    try {
      setError(null);
      await updateBlockMutation.mutateAsync({
        id: block.id,
        ...patch,
      });
    } catch (mutationError) {
      setError(extractApiErrorMessage(mutationError));
    }
  };

  const handleDrop = async (targetBlock: ReportTemplateBlock) => {
    if (!selectedTemplate || !draggingBlockId || draggingBlockId === targetBlock.id) {
      setDraggingBlockId(null);
      return;
    }

    const reordered = [...blocks];
    const sourceIndex = reordered.findIndex((item) => item.id === draggingBlockId);
    const targetIndex = reordered.findIndex((item) => item.id === targetBlock.id);
    if (sourceIndex === -1 || targetIndex === -1) {
      setDraggingBlockId(null);
      return;
    }

    const [moved] = reordered.splice(sourceIndex, 1);
    reordered.splice(targetIndex, 0, moved);

    try {
      setError(null);
      for (const [index, item] of reordered.entries()) {
        if (item.sort_order !== index + 1) {
          await updateBlockMutation.mutateAsync({
            id: item.id,
            sort_order: index + 1,
          });
        }
      }
    } catch (mutationError) {
      setError(extractApiErrorMessage(mutationError));
    } finally {
      setDraggingBlockId(null);
    }
  };

  return (
    <div className="page-grid">
      <PageIntro
        title="Шаблоны отчётов"
        description="Эксперт настраивает состав и порядок блоков технического отчёта. Генерация проекта затем использует выбранный шаблон."
      />

      <section className="section-grid">
        <article className="page-card glass-card">
          <div className="section-header">
            <h3 className="section-title">Шаблоны</h3>
            <button className="button primary" type="button" onClick={resetTemplateForm}>
              Новый шаблон
            </button>
          </div>
          <div className="list">
            {templates.map((template) => (
              <button
                key={template.id}
                className={`list-item template-item ${selectedTemplate?.id === template.id ? "template-item-active" : ""}`}
                type="button"
                onClick={() => openTemplate(template)}
              >
                <strong>{template.name}</strong>
                <span className="muted">{template.description || "Без описания"}</span>
              </button>
            ))}
          </div>
        </article>

        <article className="page-card glass-card">
          <h3 className="section-title">{form.id ? "Настройки шаблона" : "Создать шаблон"}</h3>
          <form className="form-grid" onSubmit={handleTemplateSave}>
            <div className="field-grid">
              <div>
                <label className="label">Код</label>
                <input className="input" value={form.code} onChange={(event) => setForm((current) => ({ ...current, code: event.target.value }))} required />
              </div>
              <div>
                <label className="label">Наименование</label>
                <input className="input" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} required />
              </div>
            </div>
            <div>
              <label className="label">Описание</label>
              <textarea className="textarea" rows={3} value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} />
            </div>
            <label className="checkbox-row">
              <input type="checkbox" checked={form.is_active} onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.checked }))} />
              Активный шаблон
            </label>
            <label className="checkbox-row">
              <input type="checkbox" checked={form.is_default} onChange={(event) => setForm((current) => ({ ...current, is_default: event.target.checked }))} />
              Использовать по умолчанию
            </label>
            <div className="drawer-actions">
              <button className="button primary" type="submit" disabled={createTemplateMutation.isPending || updateTemplateMutation.isPending}>
                {form.id ? "Сохранить шаблон" : "Создать шаблон"}
              </button>
            </div>
          </form>
        </article>
      </section>

      <section className="page-card glass-card">
        <div className="section-header">
          <h3 className="section-title">Блоки шаблона</h3>
          <span className="muted">Перетаскивайте блоки, чтобы менять порядок разделов.</span>
        </div>
        {!selectedTemplate ? (
          <span className="muted">Выберите или создайте шаблон, затем настройте порядок и состав блоков.</span>
        ) : (
          <div className="template-block-list">
            {blocks.map((block) => (
              <div
                key={block.id}
                className="template-block-card"
                draggable
                onDragStart={() => setDraggingBlockId(block.id)}
                onDragOver={(event) => event.preventDefault()}
                onDrop={() => void handleDrop(block)}
              >
                <div className="template-block-header">
                  <strong>{block.block_type_display || block.block_type}</strong>
                  <span className="muted">{`Порядок: ${block.sort_order}`}</span>
                </div>
                <div className="field-grid">
                  <div>
                    <label className="label">Заголовок блока</label>
                    <input
                      className="input"
                      defaultValue={block.title_override}
                      onBlur={(event) => {
                        if (event.target.value !== block.title_override) {
                          void updateBlock(block, { title_override: event.target.value });
                        }
                      }}
                    />
                  </div>
                  <div className="form-grid">
                    <label className="checkbox-row">
                      <input
                        type="checkbox"
                        checked={block.is_enabled}
                        onChange={(event) => void updateBlock(block, { is_enabled: event.target.checked })}
                        disabled={block.is_required}
                      />
                      Включить в отчёт
                    </label>
                    <label className="checkbox-row">
                      <input type="checkbox" checked={block.is_required} disabled />
                      Обязательный блок
                    </label>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        {error ? <span className="error-text">{error}</span> : null}
      </section>
    </div>
  );
}
