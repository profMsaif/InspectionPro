import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "shared/api/client";
import type { PaginatedResponse } from "shared/api/types";

export type StructuralElement = {
  id: string;
  project: string;
  building_object: string;
  building_object_name?: string;
  project_display?: string;
  element_type: string;
  element_type_dictionary?: string | null;
  element_type_dictionary_name?: string;
  name: string;
  location: string;
  material: string;
  material_dictionary?: string | null;
  material_dictionary_name?: string;
  has_defects: boolean;
  condition_category: string;
  condition_category_dictionary?: string | null;
  condition_category_dictionary_name?: string;
  inspection_status_dictionary?: string | null;
  inspection_status_dictionary_name?: string;
  recommendation_dictionary?: string | null;
  recommendation_dictionary_name?: string;
  recommendation: string;
};

export type CreateStructuralElementPayload = {
  project: string;
  building_object: string;
  element_type: string;
  element_type_dictionary?: string | null;
  name: string;
  location?: string;
  floor?: string;
  axes?: string;
  material?: string;
  material_dictionary?: string | null;
  description?: string;
  inspection_method?: string;
  inspection_method_dictionary?: string | null;
  visual_condition?: string;
  has_defects: boolean;
  no_defects_comment?: string;
  condition_category: string;
  condition_category_dictionary?: string | null;
  inspection_status_dictionary?: string | null;
  conclusion: string;
  recommendation: string;
  recommendation_dictionary?: string | null;
};

async function fetchElements() {
  const { data } = await apiClient.get<PaginatedResponse<StructuralElement>>("/elements/");
  return data;
}

async function createElement(payload: CreateStructuralElementPayload) {
  const { data } = await apiClient.post<StructuralElement>("/elements/", payload);
  return data;
}

export function useElementsQuery() {
  return useQuery({
    queryKey: ["elements"],
    queryFn: fetchElements,
  });
}

export function useCreateElementMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createElement,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["elements"] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
