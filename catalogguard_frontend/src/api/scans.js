import { apiRequest, DEMO_MODE } from "./client";

const demoScans = [
  { id: "SCAN-240", startedAt: "2026-10-16T10:30:00Z", source: "fixture.json", products: 20, pairs: 14, status: "completed", duration: "00:00:18" },
  { id: "SCAN-239", startedAt: "2026-10-15T14:05:00Z", source: "supplier-feed-oct.csv", products: 1240, pairs: 86, status: "completed", duration: "00:01:42" },
  { id: "SCAN-238", startedAt: "2026-10-14T11:20:00Z", source: "fixture.json", products: 20, pairs: 13, status: "completed", duration: "00:00:16" }
];

export async function getScans() {
  if (DEMO_MODE) return demoScans;
  return apiRequest("/api/scans");
}

export async function startRescan(payload = {}) {
  if (DEMO_MODE) return { id: `SCAN-${Date.now().toString().slice(-3)}`, status: "queued", message: "Demo scan queued. Connect the backend to run a real scan." };
  return apiRequest("/api/rescan", { method: "POST", body: JSON.stringify(payload) });
}
