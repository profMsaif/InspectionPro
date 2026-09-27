import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "shared/api/client";
import type { PaginatedResponse } from "shared/api/types";

export type Measurement = {
  id: string;
  project: string;
  measurement_type: string;
  measurement_type_dictionary?: string | null;
  measurement_type_dictionary_name?: string;
  value: string;
  unit: string;
  unit_dictionary?: string | null;
  unit_dictionary_name?: string;
  location: string;
  measured_at: string;
  engineer: string | null;
  engineer_name?: string;
  structural_element: string;
  structural_element_name?: string;
  defect?: string | null;
  device_dictionary?: string | null;
  device_dictionary_name?: string;
  method_dictionary?: string | null;
  method_dictionary_name?: string;
};

async function fetchMeasurements() {
  const { data } = await apiClient.get<PaginatedResponse<Measurement>>("/measurements/");
  return data;
}

export type CreateMeasurementPayload = {
  project: string;
  structural_element: string;
  defect?: string | null;
  measurement_type: string;
  measurement_type_dictionary?: string | null;
  value: string;
  unit: string;
  unit_dictionary?: string | null;
  location?: string;
  measured_at: string;
  method?: string;
  method_dictionary?: string | null;
  device?: string;
  device_dictionary?: string | null;
  comment?: string;
};

async function createMeasurement(payload: CreateMeasurementPayload) {
  const { data } = await apiClient.post<Measurement>("/measurements/", payload);
  return data;
}

export function useMeasurementsQuery() {
  return useQuery({
    queryKey: ["measurements"],
    queryFn: fetchMeasurements,
  });
}

export function useCreateMeasurementMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createMeasurement,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["measurements"] });
    },
  });
}
