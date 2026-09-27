import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppLayout } from "shared/layouts/AppLayout";
import { LoginPage } from "pages/auth/LoginPage";
import { DashboardPage } from "pages/dashboard/DashboardPage";
import { ElementsPage } from "pages/elements/ElementsPage";
import { ObjectDetailPage } from "pages/objects/ObjectDetailPage";
import { ObjectsPage } from "pages/objects/ObjectsPage";
import { ProjectsPage } from "pages/projects/ProjectsPage";
import { DefectsPage } from "pages/defects/DefectsPage";
import { MeasurementsPage } from "pages/measurements/MeasurementsPage";
import { ReportsPage } from "pages/reports/ReportsPage";
import { ReportPreviewPage } from "pages/reports/ReportPreviewPage";
import { ProjectDetailPage } from "pages/projects/ProjectDetailPage";
import { DictionariesPage } from "pages/dictionaries/DictionariesPage";
import { PassportPage } from "pages/projects/PassportPage";
import { ReportTemplatesPage } from "pages/reports/ReportTemplatesPage";
import { useAuthStore } from "features/auth/authStore";

function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? <AppLayout /> : <Navigate to="/login" replace />;
}

function GuestRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />;
}

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <GuestRoute />,
  },
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "objects", element: <ObjectsPage /> },
      { path: "objects/:objectId", element: <ObjectDetailPage /> },
      { path: "projects", element: <ProjectsPage /> },
      { path: "elements", element: <ElementsPage /> },
      { path: "projects/:projectId", element: <ProjectDetailPage /> },
      { path: "projects/:projectId/passport", element: <PassportPage /> },
      { path: "defects", element: <DefectsPage /> },
      { path: "measurements", element: <MeasurementsPage /> },
      { path: "reports", element: <ReportsPage /> },
      { path: "reports/:reportId", element: <ReportPreviewPage /> },
      { path: "report-templates", element: <ReportTemplatesPage /> },
      { path: "dictionaries", element: <DictionariesPage /> },
    ],
  },
]);
