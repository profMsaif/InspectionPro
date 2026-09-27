import type { ReactNode } from "react";

type DrawerPanelProps = {
  open: boolean;
  title: string;
  description: string;
  onClose: () => void;
  children: ReactNode;
};

export function DrawerPanel({ open, title, description, onClose, children }: DrawerPanelProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <aside className="drawer-panel glass-card" onClick={(event) => event.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <h2 className="page-title">{title}</h2>
            <p className="muted">{description}</p>
          </div>
          <button className="button ghost" type="button" onClick={onClose}>
            Закрыть
          </button>
        </div>
        <div className="drawer-body">{children}</div>
      </aside>
    </div>
  );
}

