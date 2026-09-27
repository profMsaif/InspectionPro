import { create } from "zustand";

type UserRole = "Admin" | "Manager" | "Engineer" | "Expert" | "Client";

const AUTH_STORAGE_KEY = "inspectionpro-auth";

type PersistedAuthState = {
  accessToken: string;
  refreshToken: string;
  fullName: string;
  role: UserRole;
};

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  fullName: string | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  login: (payload: { accessToken: string; refreshToken: string; fullName: string; role: UserRole }) => void;
  logout: () => void;
};

function readStoredAuth(): PersistedAuthState | null {
  const storedValue = window.localStorage.getItem(AUTH_STORAGE_KEY);
  if (!storedValue) {
    return null;
  }

  try {
    return JSON.parse(storedValue) as PersistedAuthState;
  } catch {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
  }
}

function persistAuth(payload: PersistedAuthState) {
  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(payload));
}

export function clearStoredAuth() {
  window.localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function getAccessToken() {
  return readStoredAuth()?.accessToken ?? null;
}

export function logoutFromStore() {
  useAuthStore.getState().logout();
}

const storedAuth = typeof window !== "undefined" ? readStoredAuth() : null;

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: storedAuth?.accessToken ?? null,
  refreshToken: storedAuth?.refreshToken ?? null,
  fullName: storedAuth?.fullName ?? null,
  role: storedAuth?.role ?? null,
  isAuthenticated: Boolean(storedAuth?.accessToken),
  login: ({ accessToken, refreshToken, fullName, role }) =>
    set(() => {
      persistAuth({ accessToken, refreshToken, fullName, role });
      return {
        accessToken,
        refreshToken,
        fullName,
        role,
        isAuthenticated: true,
      };
    }),
  logout: () =>
    set(() => {
      clearStoredAuth();
      return {
        accessToken: null,
        refreshToken: null,
        fullName: null,
        role: null,
        isAuthenticated: false,
      };
    }),
}));
