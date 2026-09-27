import { Outlet } from "react-router-dom";

import { AppSidebar } from "widgets/navigation/AppSidebar";
import { TopBar } from "widgets/navigation/TopBar";

export function AppLayout() {
  return (
    <div className="app-shell">
      <AppSidebar />
      <div className="app-main">
        <TopBar />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

