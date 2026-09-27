import { useDefectsQuery } from "features/defects/api";
import { useMeasurementsQuery } from "features/measurements/api";
import { useObjectsQuery } from "features/objects/api";
import { useProjectsQuery } from "features/projects/api";
import { useReportsQuery } from "features/reports/api";

export function useDashboardData() {
  const objectsQuery = useObjectsQuery();
  const projectsQuery = useProjectsQuery();
  const defectsQuery = useDefectsQuery();
  const measurementsQuery = useMeasurementsQuery();
  const reportsQuery = useReportsQuery();

  const isLoading =
    objectsQuery.isLoading ||
    projectsQuery.isLoading ||
    defectsQuery.isLoading ||
    measurementsQuery.isLoading ||
    reportsQuery.isLoading;

  const isError =
    objectsQuery.isError ||
    projectsQuery.isError ||
    defectsQuery.isError ||
    measurementsQuery.isError ||
    reportsQuery.isError;

  const projects = projectsQuery.data?.results ?? [];
  const reports = reportsQuery.data?.results ?? [];
  const reviewProjects = projects.filter((project) => project.status === "Review").length;

  const summary = {
    objectsCount: objectsQuery.data?.count ?? 0,
    projectsCount: projectsQuery.data?.count ?? 0,
    defectsCount: defectsQuery.data?.count ?? 0,
    measurementsCount: measurementsQuery.data?.count ?? 0,
    reportsReviewCount: reports.filter((report) => report.status === "generated").length + reviewProjects,
    projects,
  };

  return {
    isLoading,
    isError,
    summary,
  };
}
