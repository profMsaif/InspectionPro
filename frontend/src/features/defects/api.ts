import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "shared/api/client";
import type { PaginatedResponse } from "shared/api/types";

export type Defect = {
  id: string;
  title: string;
  defect_type: string;
  defect_type_dictionary?: string | null;
  defect_type_dictionary_name?: string;
  floor: string;
  location: string;
  final_condition_category: string;
  final_condition_category_dictionary?: string | null;
  final_condition_category_dictionary_name?: string;
  structural_element: string;
  structural_element_name?: string;
  project: string;
  project_display?: string;
  severity_dictionary?: string | null;
  severity_dictionary_name?: string;
  probable_cause_dictionary?: string | null;
  probable_cause_dictionary_name?: string;
  recommendation_dictionary?: string | null;
  recommendation_dictionary_name?: string;
};

async function fetchDefects() {
  const { data } = await apiClient.get<PaginatedResponse<Defect>>("/defects/");
  return data;
}

export type CreateDefectPayload = {
  project: string;
  building_object: string;
  structural_element: string;
  defect_type: string;
  defect_type_dictionary?: string | null;
  title: string;
  description: string;
  location?: string;
  floor?: string;
  severity?: string;
  severity_dictionary?: string | null;
  probable_cause?: string;
  probable_cause_dictionary?: string | null;
  preliminary_condition_category?: string;
  preliminary_condition_category_dictionary?: string | null;
  final_condition_category?: string;
  final_condition_category_dictionary?: string | null;
  recommendation?: string;
  recommendation_dictionary?: string | null;
  status?: string;
};

async function createDefect(payload: CreateDefectPayload) {
  const { data } = await apiClient.post<Defect>("/defects/", payload);
  return data;
}

export function useDefectsQuery() {
  return useQuery({
    queryKey: ["defects"],
    queryFn: fetchDefects,
  });
}

export function useCreateDefectMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createDefect,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["defects"] });
      queryClient.invalidateQueries({ queryKey: ["elements"] });
    },
  });
}
