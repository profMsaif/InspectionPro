import { apiClient } from "shared/api/client";
import type { MeResponse } from "./types";

type LoginPayload = {
  email: string;
  password: string;
};

export type LoginResponse = {
  access: string;
  refresh: string;
};

export async function login(payload: LoginPayload) {
  const { data } = await apiClient.post<LoginResponse>("/auth/login/", payload);
  return data;
}

export async function getMe(accessToken?: string) {
  const { data } = await apiClient.get<MeResponse>("/auth/me/", {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
  });
  return data;
}
