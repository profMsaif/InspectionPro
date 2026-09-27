import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "shared/api/client";

export type InspectionFile = {
  id: string;
  original_name: string;
  caption: string;
  category: string;
  is_for_report: boolean;
  appendix_type: string | null;
  appendix_type_display?: string;
  project: string | null;
  building_object: string | null;
  structural_element: string | null;
  defect: string | null;
  measurement: string | null;
  created_at: string;
};

export type UploadInspectionFilePayload = {
  file: File;
  category: string;
  appendix_type?: string;
  project?: string;
  building_object?: string;
  structural_element?: string;
  defect?: string;
  measurement?: string;
  caption?: string;
  is_for_report?: boolean;
};

type FileQueryFilters = {
  projectId?: string;
  buildingObjectId?: string;
};

export const appendixTypeOptions = [
  { value: "technical_documentation", label: "Техническая документация" },
  { value: "sro_certificate", label: "Свидетельства СРО" },
  { value: "specialist_qualification", label: "Квалификация специалистов" },
  { value: "device_calibration", label: "Поверка приборов и оборудования" },
  { value: "technical_task", label: "Техническое задание" },
  { value: "work_program", label: "Программа работ" },
  { value: "source_data", label: "Исходные данные" },
  { value: "survey_protocol", label: "Протоколы обследования" },
  { value: "calculation", label: "Поверочные расчеты" },
  { value: "survey_act", label: "Акты обследования" },
  { value: "normative_reference", label: "Нормативные ссылки" },
  { value: "terms_definitions", label: "Термины и определения" },
  { value: "abbreviations", label: "Обозначения и сокращения" },
  { value: "graphic_material", label: "Графические материалы" },
  { value: "other_appendix", label: "Прочие приложения" },
] as const;

async function fetchFiles(filters?: FileQueryFilters) {
  const params = new URLSearchParams();
  if (filters?.projectId) params.set("project", filters.projectId);
  if (filters?.buildingObjectId) params.set("building_object", filters.buildingObjectId);
  const query = params.toString() ? `?${params.toString()}` : "";
  const { data } = await apiClient.get<{ count: number; next: string | null; previous: string | null; results: InspectionFile[] }>(
    `/files/${query}`,
  );
  return data;
}

async function uploadFile(payload: UploadInspectionFilePayload) {
  const formData = new FormData();
  formData.append("file", payload.file);
  formData.append("category", payload.category);
  if (payload.appendix_type) formData.append("appendix_type", payload.appendix_type);
  if (payload.project) formData.append("project", payload.project);
  if (payload.building_object) formData.append("building_object", payload.building_object);
  if (payload.structural_element) formData.append("structural_element", payload.structural_element);
  if (payload.defect) formData.append("defect", payload.defect);
  if (payload.measurement) formData.append("measurement", payload.measurement);
  if (payload.caption) formData.append("caption", payload.caption);
  formData.append("is_for_report", payload.is_for_report ? "true" : "false");
  const { data } = await apiClient.post<InspectionFile>("/files/", formData, {
    headers: {},
  });
  return data;
}

export function useFilesQuery(filters?: FileQueryFilters) {
  return useQuery({
    queryKey: ["files", filters?.projectId ?? "all", filters?.buildingObjectId ?? "all"],
    queryFn: () => fetchFiles(filters),
  });
}

export function useUploadInspectionFileMutation(projectId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: uploadFile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files", projectId ?? "all"] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ["project-reports", projectId] });
      }
    },
  });
}
