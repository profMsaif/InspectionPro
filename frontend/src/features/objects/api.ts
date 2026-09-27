import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "shared/api/client";
import type { PaginatedResponse } from "shared/api/types";

export type BuildingObject = {
  id: string;
  name: string;
  address: string;
  object_type: string;
  object_type_dictionary?: string | null;
  object_type_dictionary_name?: string;
  construction_year: number | null;
  purpose?: string;
  cadastral_number?: string;
  floors_count?: number | null;
  structural_system_dictionary?: string | null;
  structural_system_dictionary_name?: string;
  main_material_dictionary?: string | null;
  main_material_dictionary_name?: string;
};

async function fetchObjects() {
  const { data } = await apiClient.get<PaginatedResponse<BuildingObject>>("/objects/");
  return data;
}

async function fetchObject(objectId: string) {
  const { data } = await apiClient.get<BuildingObject>(`/objects/${objectId}/`);
  return data;
}

export type CreateBuildingObjectPayload = {
  name: string;
  address: string;
  object_type: string;
  object_type_dictionary?: string | null;
  purpose?: string;
  construction_year?: number | null;
  structural_system_dictionary?: string | null;
  main_material_dictionary?: string | null;
};

async function createObject(payload: CreateBuildingObjectPayload) {
  const { data } = await apiClient.post<BuildingObject>("/objects/", payload);
  return data;
}

async function updateObject(payload: BuildingObject) {
  const { data } = await apiClient.patch<BuildingObject>(`/objects/${payload.id}/`, payload);
  return data;
}

async function deleteObject(objectId: string) {
  await apiClient.delete(`/objects/${objectId}/`);
}

export function useObjectsQuery() {
  return useQuery({
    queryKey: ["objects"],
    queryFn: fetchObjects,
  });
}

export function useObjectQuery(objectId: string) {
  return useQuery({
    queryKey: ["objects", objectId],
    queryFn: () => fetchObject(objectId),
    enabled: Boolean(objectId),
  });
}

export function useCreateObjectMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createObject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["objects"] });
    },
  });
}

export function useUpdateObjectMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateObject,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["objects"] });
      queryClient.invalidateQueries({ queryKey: ["objects", data.id] });
    },
  });
}

export function useDeleteObjectMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteObject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["objects"] });
    },
  });
}
