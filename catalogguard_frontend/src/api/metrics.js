import { apiRequest, DEMO_MODE } from "./client";

export async function getMetrics() {
  if (DEMO_MODE) return {
    totalProducts: 20, pendingReviews: 12, acceptedThisWeek: 28, scansThisMonth: 9,
    precision: 92, precisionCorrect: 23, precisionReviewed: 25,
    recall: 86, recallFound: 12, recallExpected: 14,
    avgReviewTimeSeconds: 42, falseMergeRate: 0,
    note: "Illustrative demo metrics — replace with measured values from the labelled fixture and backend."
  };
  return apiRequest("/api/metrics");
}
