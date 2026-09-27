import { useLocation } from "react-router-dom";

import { useAuthStore } from "features/auth/authStore";

const pageTitles: Record<string, string> = {
  "/": "Оперативный обзор",
  "/objects": "Карточки объектов",
  "/projects": "Проекты обследования",
  "/elements": "Оценка элементов",
  "/defects": "Реестр дефектов",
  "/measurements": "Инструментальные измерения",
  "/reports": "Технические заключения",
  "/dictionaries": "Экспертные справочники",
};

function resolvePageTitle(pathname: string) {
  if (pathname.startsWith("/projects/")) {
    return "Карточка проекта";
  }
  if (pathname.startsWith("/reports/")) {
    return "Предпросмотр отчёта";
  }

  return pageTitles[pathname] ?? "InspectionPro";
}

export function TopBar() {
  const location = useLocation();
  const fullName = useAuthStore((state) => state.fullName);
  const role = useAuthStore((state) => state.role);
  const logout = useAuthStore((state) => state.logout);

  return (
    <header className="topbar">
      <div>
        <p className="pill">{role ?? "Engineer"}</p>
        <h2 className="headline">{resolvePageTitle(location.pathname)}</h2>
      </div>
      <div className="topbar-actions">
        <div className="glass-card" style={{ padding: "14px 18px" }}>
          <strong>{fullName ?? "Demo Engineer"}</strong>
          <div className="muted">Проектный режим: MVP foundation</div>
        </div>
        <button className="button ghost" type="button" onClick={logout}>
          Выйти
        </button>
      </div>
    </header>
  );
}
