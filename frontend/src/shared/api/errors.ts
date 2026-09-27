import axios from "axios";

export function extractApiErrorMessage(error: unknown) {
  if (!axios.isAxiosError(error)) {
    return "Не удалось выполнить действие. Попробуйте ещё раз.";
  }

  const payload = error.response?.data;
  if (!payload) {
    return "Backend API недоступен или не вернул данные.";
  }

  if (typeof payload === "string") {
    return payload;
  }

  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  if (typeof payload === "object") {
    return Object.entries(payload)
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}: ${value.join(", ")}`;
        }
        if (typeof value === "object" && value !== null) {
          return `${key}: ${JSON.stringify(value)}`;
        }
        return `${key}: ${String(value)}`;
      })
      .join(" | ");
  }

  return "Не удалось выполнить действие. Попробуйте ещё раз.";
}

