import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "shared/api/client";
import type { PaginatedResponse } from "shared/api/types";

export type DictionaryType =
  | "object_type"
  | "inspection_type"
  | "element_type"
  | "structural_system"
  | "material"
  | "condition_category"
  | "defect_type"
  | "defect_severity"
  | "defect_cause"
  | "recommendation_type"
  | "inspection_method"
  | "measurement_type"
  | "measurement_unit"
  | "device"
  | "element_inspection_status";

export type DictionaryItem = {
  id: string;
  dictionary_type: DictionaryType;
  dictionary_type_display: string;
  code: string;
  name_ru: string;
  name_en: string;
  description: string;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
};

export type DictionaryItemPayload = {
  dictionary_type: DictionaryType;
  code: string;
  name_ru: string;
  name_en?: string;
  description?: string;
  is_active?: boolean;
  sort_order?: number;
};

async function fetchDictionaryItems(dictionaryType: DictionaryType, includeInactive = false) {
  const { data } = await apiClient.get<PaginatedResponse<DictionaryItem>>("/dictionaries/items/", {
    params: {
      dictionary_type: dictionaryType,
      ...(includeInactive ? {} : { is_active: true }),
    },
  });
  return data;
}

async function createDictionaryItem(payload: DictionaryItemPayload) {
  const { data } = await apiClient.post<DictionaryItem>("/dictionaries/items/", payload);
  return data;
}

async function updateDictionaryItem(payload: Partial<DictionaryItemPayload> & { id: string }) {
  const { data } = await apiClient.patch<DictionaryItem>(`/dictionaries/items/${payload.id}/`, payload);
  return data;
}

async function deactivateDictionaryItem(itemId: string) {
  await apiClient.delete(`/dictionaries/items/${itemId}/`);
}

async function reorderDictionaryItems(items: string[]) {
  const { data } = await apiClient.post<DictionaryItem[]>("/dictionaries/items/reorder/", { items });
  return data;
}

export function useDictionaryItemsQuery(dictionaryType: DictionaryType, includeInactive = false) {
  return useQuery({
    queryKey: ["dictionary-items", dictionaryType, includeInactive],
    queryFn: () => fetchDictionaryItems(dictionaryType, includeInactive),
  });
}

export function useDictionaryGroupsQuery(dictionaryTypes: DictionaryType[], includeInactive = false) {
  const queries = useQueries({
    queries: dictionaryTypes.map((dictionaryType) => ({
      queryKey: ["dictionary-items", dictionaryType, includeInactive],
      queryFn: () => fetchDictionaryItems(dictionaryType, includeInactive),
    })),
  });

  const data = dictionaryTypes.reduce<Record<string, DictionaryItem[]>>((accumulator, dictionaryType, index) => {
    accumulator[dictionaryType] = queries[index].data?.results ?? [];
    return accumulator;
  }, {});

  return {
    data,
    isLoading: queries.some((query) => query.isLoading),
    isError: queries.some((query) => query.isError),
  };
}

export function useCreateDictionaryItemMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createDictionaryItem,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["dictionary-items", variables.dictionary_type] });
    },
  });
}

export function useUpdateDictionaryItemMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateDictionaryItem,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["dictionary-items", data.dictionary_type] });
    },
  });
}

export function useDeactivateDictionaryItemMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deactivateDictionaryItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dictionary-items"] });
    },
  });
}

export function useReorderDictionaryItemsMutation(dictionaryType: DictionaryType) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: reorderDictionaryItems,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dictionary-items", dictionaryType] });
    },
  });
}
