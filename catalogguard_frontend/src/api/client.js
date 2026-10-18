const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  ?? (import.meta.env.PROD ? "" : "http://localhost:8000");
export const DEMO_MODE = String(import.meta.env.VITE_DEMO_MODE ?? "true") === "true";

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    const message = await response.text().catch(() => "");
    throw Object.assign(new Error(message || `API request failed (${response.status})`), { status: response.status });
  }
  if (response.status === 204) return null;
  const type = response.headers.get("content-type") || "";
  return type.includes("application/json") ? response.json() : response.blob();
}
