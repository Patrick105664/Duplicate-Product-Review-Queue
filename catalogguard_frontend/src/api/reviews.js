import { apiRequest, DEMO_MODE } from "./client";

let decisions = {};
export const demoPairs = [
  { id: "PAIR-0081", leftId: "P-1042", rightId: "P-1043", score: 0.97, status: "pending", reason: "Same brand and model number; title wording differs.", signals: ["Brand match", "Model match", "Title similarity 94%", "Price match"], createdAt: "2026-10-16T10:30:00Z", label: "Likely duplicate" },
  { id: "PAIR-0082", leftId: "P-2081", rightId: "P-2082", score: 0.91, status: "pending", reason: "Similar title and brand, but quantity differs: single bottle vs set of 2.", signals: ["Brand match", "Title similarity 89%", "Pack quantity conflict"], createdAt: "2026-10-16T09:15:00Z", label: "Needs careful review" },
  { id: "PAIR-0083", leftId: "P-3107", rightId: "P-3108", score: 0.84, status: "pending", reason: "Related product family but model suffix and price differ.", signals: ["Brand match", "Title similarity 82%", "Model mismatch", "Price differs"], createdAt: "2026-10-15T15:20:00Z", label: "Possible variant" },
  { id: "PAIR-0084", leftId: "P-1042", rightId: "P-2081", score: 0.18, status: "pending", reason: "Low-confidence hard negative included for reviewer validation.", signals: ["Brand mismatch", "Category mismatch", "Title similarity 12%"], createdAt: "2026-10-15T12:00:00Z", label: "Likely distinct" }
];

export async function getReviewPairs() {
  if (!DEMO_MODE) return apiRequest("/api/pairs");
  return demoPairs.map((pair) => ({ ...pair, status: decisions[pair.id]?.decision || pair.status, decisionNote: decisions[pair.id]?.note || "" }));
}

export async function getReviewPair(id) {
  if (!DEMO_MODE) return apiRequest(`/api/pairs/${id}`);
  const pair = demoPairs.find((item) => item.id === id);
  return pair ? { ...pair, status: decisions[id]?.decision || pair.status, decisionNote: decisions[id]?.note || "" } : null;
}

export async function submitDecision(id, decision, note = "") {
  if (!DEMO_MODE) return apiRequest(`/api/pairs/${id}/decision`, {
    method: "POST", body: JSON.stringify({ decision, note, reviewer: "Demo Reviewer" })
  });
  decisions[id] = { decision, note, decidedAt: new Date().toISOString() };
  return { ok: true, pairId: id, decision, note, decidedAt: decisions[id].decidedAt, demo: true };
}
