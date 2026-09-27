import { NavLink } from "react-router-dom";
import { useAuthStore } from "features/auth/authStore";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/objects", label: "Объекты" },
  { to: "/projects", label: "Проекты" },
  { to: "/elements", label: "Элементы" },
  { to: "/defects", label: "Дефекты" },
  { to: "/measurements", label: "Измерения" },
  { to: "/reports", label: "Отчёты" },
];

export function AppSidebar() {
  const role = useAuthStore((state) => state.role);
  const visibleItems = [...navItems];
  if (role === "Admin" || role === "Expert") {
    visibleItems.push({ to: "/dictionaries", label: "Справочники" });
    visibleItems.push({ to: "/report-templates", label: "Шаблоны отчётов" });
  }

  return (
    <aside className="sidebar">
      <div className="brand-block">
        <p className="pill">ГОСТ 31937-2024</p>
        <h1 className="brand-title">InspectionPro</h1>
        <p className="brand-caption">
          Единое рабочее пространство для обследования зданий, фиксации дефектов и подготовки технических заключений.
        </p>
      </div>

      <nav className="nav-list">
        {visibleItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
