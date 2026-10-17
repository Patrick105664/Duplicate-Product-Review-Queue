import { apiRequest, DEMO_MODE } from "./client";
import { FALSE_MERGE_COST_CONFIG } from "../utils/constants";

function withFalseMergeCost(metrics = {}) {
  const finiteOr = (value, fallback) => Number.isFinite(value) ? value : fallback;
  const labourMinutes = finiteOr(metrics.labourMinutes, FALSE_MERGE_COST_CONFIG.labourMinutes);
  const labourRatePerHour = finiteOr(metrics.labourRatePerHour, FALSE_MERGE_COST_CONFIG.labourRatePerHour);
  const downstreamLoss = finiteOr(metrics.downstreamLoss, FALSE_MERGE_COST_CONFIG.downstreamLoss);
  const remediationCost = finiteOr(metrics.remediationCost, FALSE_MERGE_COST_CONFIG.remediationCost);
  const falseMergeCount = finiteOr(
    metrics.falseMergeCount,
    Number.isFinite(metrics.precisionReviewed) && Number.isFinite(metrics.precisionCorrect)
      ? Math.max(0, metrics.precisionReviewed - metrics.precisionCorrect)
      : 0
  );
  const calculatedCost = Math.round((labourMinutes / 60) * labourRatePerHour + downstreamLoss + remediationCost);
  const falseMergeCostPerMerge = finiteOr(metrics.falseMergeCostPerMerge, calculatedCost);
  const falseMergeExposure = finiteOr(metrics.falseMergeExposure, falseMergeCount * falseMergeCostPerMerge);

  return {
    ...metrics,
    labourMinutes,
    labourRatePerHour,
    downstreamLoss,
    remediationCost,
    falseMergeCount,
    falseMergeCostPerMerge,
    falseMergeExposure
  };
}

export async function getMetrics() {
  if (DEMO_MODE) return withFalseMergeCost({
    totalProducts: 20, pendingReviews: 12, acceptedThisWeek: 28, scansThisMonth: 9,
    precision: 92, precisionCorrect: 23, precisionReviewed: 25,
    recall: 86, recallFound: 12, recallExpected: 14,
    accuracy: 94, accuracyCorrect: 47, accuracyTotal: 50,
    avgReviewTimeSeconds: 42, falseMergeRate: 0,
    note: "Illustrative demo metrics — replace with measured values from the labelled fixture and backend."
  });
  const metrics = await apiRequest("/api/metrics");
  const accuracyFromCounts = Number.isFinite(metrics?.accuracyCorrect) &&
    Number.isFinite(metrics?.accuracyTotal) && metrics.accuracyTotal > 0
    ? Math.round((metrics.accuracyCorrect / metrics.accuracyTotal) * 100)
    : null;
  return withFalseMergeCost({ ...metrics, accuracy: metrics?.accuracy ?? accuracyFromCounts });
}
