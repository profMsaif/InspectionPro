import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "shared/api/client";
import type { PaginatedResponse } from "shared/api/types";

export type InspectionProject = {
  id: string;
  customer_name: string;
  contract_number: string;
  status: string;
  inspection_type: string;
  inspection_type_dictionary?: string | null;
  inspection_type_dictionary_name?: string;
  start_date: string | null;
  end_date: string | null;
  final_condition_category: string;
  final_condition_category_dictionary?: string | null;
  final_condition_category_dictionary_name?: string;
  building_object: string;
  building_object_name?: string;
  responsible_engineer_name?: string;
  report_template?: string | null;
  report_template_name?: string;
  technical_task?: TechnicalTask | null;
  work_program?: WorkProgram | null;
};

export type TechnicalTask = {
  id: string;
  project: string;
  execution_basis: string;
  survey_goal: string;
  building_parts: string;
  engineering_systems: string;
  required_methods: string;
  result_requirements: string;
  deadlines: string;
  output_documentation: string;
};

export type WorkProgram = {
  id: string;
  project: string;
  structures: string;
  zones: string;
  methods: string;
  tools_and_devices: string;
  measurements: string;
  photo_requirements: string;
  responsible_executors: string;
  completeness_checklist: string[];
};

async function fetchProjects() {
  const { data } = await apiClient.get<PaginatedResponse<InspectionProject>>("/projects/");
  return data;
}

async function fetchProject(projectId: string) {
  const { data } = await apiClient.get<InspectionProject>(`/projects/${projectId}/`);
  return data;
}

export type CreateInspectionProjectPayload = {
  building_object: string;
  customer_name: string;
  contract_number: string;
  inspection_reason: string;
  inspection_goal: string;
  inspection_type: string;
  inspection_type_dictionary?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  report_template?: string | null;
};

export type UpdateInspectionProjectPayload = Partial<CreateInspectionProjectPayload> & {
  id: string;
  final_condition_category_dictionary?: string | null;
  final_condition_category?: string;
};

export type ProjectPassport = {
  title_page: Record<string, unknown>;
  general_information: Record<string, unknown>;
  basis_and_purpose: Record<string, unknown>;
  inspection_type_and_methods: Record<string, unknown>;
  work_program: Record<string, unknown>;
  constructive_characteristics: Record<string, Array<Record<string, string>>>;
  element_assessments: Array<Record<string, unknown>>;
  defect_register: Array<Record<string, unknown>>;
  measurements: Array<Record<string, unknown>>;
  photo_appendix: Record<string, unknown>;
  technical_condition_assessment: Record<string, unknown>;
  final_conclusion: {
    final_condition_category: string;
    restrictions: string[] | string;
    recommendations: string[];
    need_for_monitoring: boolean;
    need_for_additional_inspection: boolean;
  };
};

async function createProject(payload: CreateInspectionProjectPayload) {
  const { data } = await apiClient.post<InspectionProject>("/projects/", payload);
  return data;
}

async function updateProject(payload: UpdateInspectionProjectPayload) {
  const { id, ...body } = payload;
  const { data } = await apiClient.patch<InspectionProject>(`/projects/${id}/`, body);
  return data;
}

async function setProjectReportTemplate(payload: { id: string; report_template: string | null }) {
  const { data } = await apiClient.post<InspectionProject>(`/projects/${payload.id}/set-report-template/`, {
    report_template: payload.report_template,
  });
  return data;
}

async function submitReview(projectId: string) {
  const { data } = await apiClient.post<{ status: string }>(`/projects/${projectId}/submit_review/`);
  return data;
}

async function approveProject(projectId: string) {
  const { data } = await apiClient.post<{ status: string }>(`/projects/${projectId}/approve/`);
  return data;
}

async function returnProjectForCorrection(projectId: string) {
  const { data } = await apiClient.post<{ status: string }>(`/projects/${projectId}/return_for_correction/`);
  return data;
}

async function saveTechnicalTask(payload: Omit<TechnicalTask, "id"> & { id?: string }) {
  if (payload.id) {
    const { data } = await apiClient.patch<TechnicalTask>(`/technical-tasks/${payload.id}/`, payload);
    return data;
  }
  const { data } = await apiClient.post<TechnicalTask>("/technical-tasks/", payload);
  return data;
}

async function saveWorkProgram(payload: Omit<WorkProgram, "id"> & { id?: string }) {
  if (payload.id) {
    const { data } = await apiClient.patch<WorkProgram>(`/work-programs/${payload.id}/`, payload);
    return data;
  }
  const { data } = await apiClient.post<WorkProgram>("/work-programs/", payload);
  return data;
}

async function fetchProjectPassport(projectId: string) {
  const { data } = await apiClient.get<ProjectPassport>(`/projects/${projectId}/passport/`);
  return data;
}

export function useProjectsQuery() {
  return useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });
}

export function useProjectQuery(projectId: string) {
  return useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => fetchProject(projectId),
    enabled: Boolean(projectId),
  });
}

export function useProjectPassportQuery(projectId: string) {
  return useQuery({
    queryKey: ["projects", projectId, "passport"],
    queryFn: () => fetchProjectPassport(projectId),
    enabled: Boolean(projectId),
  });
}

export function useCreateProjectMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useUpdateProjectMutation(projectId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateProject,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["projects", data.id] });
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
      }
    },
  });
}

export function useSetProjectReportTemplateMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { report_template: string | null }) => setProjectReportTemplate({ id: projectId, report_template: payload.report_template }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["projects", data.id] });
      queryClient.invalidateQueries({ queryKey: ["project-reports", data.id] });
    },
  });
}

export function useSubmitReviewMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => submitReview(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
    },
  });
}

export function useApproveProjectMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => approveProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
    },
  });
}

export function useReturnForCorrectionMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => returnProjectForCorrection(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
    },
  });
}

export function useSaveTechnicalTaskMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: saveTechnicalTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
    },
  });
}

export function useSaveWorkProgramMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: saveWorkProgram,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
    },
  });
}
