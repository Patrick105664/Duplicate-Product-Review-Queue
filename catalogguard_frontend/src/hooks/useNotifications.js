import { useCallback, useEffect, useState } from "react";
import { getNotificationFeed } from "../api/notifications";
import { getMetrics } from "../api/metrics";
import { getProducts } from "../api/products";
import { getReviewPairs } from "../api/reviews";
import { getScans } from "../api/scans";
import { formatCurrencyINR } from "../utils/formatters";
import { FALSE_MERGE_COST_CONFIG } from "../utils/constants";

const READ_NOTIFICATIONS_KEY = "catalogguard.notifications.read.v1";

function loadReadIds() {
  try {
    const value = JSON.parse(window.localStorage.getItem(READ_NOTIFICATIONS_KEY) || "[]");
    return Array.isArray(value) ? value.filter((id) => typeof id === "string") : [];
  } catch {
    return [];
  }
}

function persistReadIds(ids) {
  try {
    window.localStorage.setItem(READ_NOTIFICATIONS_KEY, JSON.stringify(ids));
  } catch {
    return;
  }
}

function relativeTime(value) {
  if (!value) return "Recently";
  const timestamp = new Date(value).getTime();
  if (!Number.isFinite(timestamp)) return "Recently";
  const minutes = Math.max(0, Math.floor((Date.now() - timestamp) / 60000));
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hr${hours === 1 ? "" : "s"} ago`;
  const days = Math.floor(hours / 24);
  return days === 1 ? "Yesterday" : `${days} days ago`;
}

function normalizeBackendNotifications(payload) {
  const values = Array.isArray(payload) ? payload : payload?.notifications;
  if (!Array.isArray(values)) return null;
  return values.map((item, index) => ({
    id: String(item.id || item.notificationId || `backend-${index}`),
    title: item.title || "Notification",
    description: item.description || item.message || "",
    time: relativeTime(item.createdAt || item.timestamp),
    timestamp: item.createdAt || item.timestamp || "",
    href: typeof (item.href || item.link || item.path) === "string" && (item.href || item.link || item.path).startsWith("/") && !(item.href || item.link || item.path).startsWith("//")
      ? item.href || item.link || item.path
      : "/queue",
    icon: item.icon || "review",
    unread: item.unread !== false && item.read !== true
  }));
}

function deriveNotifications({ pairs, products, scans, metrics }) {
  const productById = new Map(products.map((product) => [product.product_id || product.id, product]));
  const pending = pairs.filter((pair) => pair.status === "pending");
  const now = new Date().toISOString();
  const notifications = [];

  if (pending.length) {
    notifications.push({
      id: "pending-pairs",
      title: "Pairs waiting for review",
      description: `${pending.length} ${pending.length === 1 ? "pair is" : "pairs are"} waiting for your decision.`,
      timestamp: now,
      href: "/queue",
      icon: "review"
    });
  }

  for (const pair of pending) {
    const score = Number(pair.score);
    const percent = score <= 1 ? Math.round(score * 100) : Math.round(score);
    if (Number.isFinite(percent) && percent >= 90) {
      notifications.push({
        id: `high-confidence-${pair.id}`,
        title: "High-confidence match",
        description: `${pair.id} has a ${percent}% match score and is awaiting review.`,
        timestamp: pair.createdAt || now,
        href: `/compare/${encodeURIComponent(pair.id)}`,
        icon: "match"
      });
    }

    const left = productById.get(pair.leftId);
    const right = productById.get(pair.rightId);
    if (left && right && Number(left.pack_quantity ?? left.packQuantity ?? 1) !== Number(right.pack_quantity ?? right.packQuantity ?? 1)) {
      notifications.push({
        id: `pack-mismatch-${pair.id}`,
        title: "Pack quantity mismatch",
        description: `${pair.id} has different pack quantities, indicating a likely false merge.`,
        timestamp: pair.createdAt || now,
        href: `/compare/${encodeURIComponent(pair.id)}`,
        icon: "pack"
      });
    }
  }

  const latestScan = [...scans].sort((a, b) => new Date(b.startedAt || b.createdAt || 0) - new Date(a.startedAt || a.createdAt || 0))[0];
  if (latestScan) {
    notifications.push({
      id: `latest-scan-${latestScan.id}`,
      title: latestScan.status === "completed" ? "Scan completed" : "Latest scan update",
      description: `${latestScan.id} ${latestScan.status === "completed" ? "finished" : `is ${latestScan.status || "being processed"}`} with ${latestScan.pairs ?? 0} suggested pairs.`,
      timestamp: latestScan.startedAt || latestScan.createdAt || now,
      href: "/scan-history",
      icon: "scan"
    });
  }

  const costPerMerge = Number.isFinite(metrics?.falseMergeCostPerMerge)
    ? metrics.falseMergeCostPerMerge
    : Math.round((FALSE_MERGE_COST_CONFIG.labourMinutes / 60) * FALSE_MERGE_COST_CONFIG.labourRatePerHour + FALSE_MERGE_COST_CONFIG.downstreamLoss + FALSE_MERGE_COST_CONFIG.remediationCost);
  const falseMergeCount = Number.isFinite(metrics?.falseMergeCount) ? metrics.falseMergeCount : 0;
  const exposure = Number.isFinite(metrics?.falseMergeExposure) ? metrics.falseMergeExposure : costPerMerge * falseMergeCount;
  notifications.push({
    id: "false-merge-cost-reminder",
    title: "False merge cost reminder",
    description: `${formatCurrencyINR(costPerMerge)} per false merge · ${formatCurrencyINR(exposure)} estimated exposure.`,
    timestamp: now,
    href: "/evaluation",
    icon: "cost"
  });

  return notifications.map((notification) => ({ ...notification, time: relativeTime(notification.timestamp) }));
}

export function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [readIds, setReadIds] = useState(loadReadIds);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      const results = await Promise.allSettled([
        getNotificationFeed(),
        getReviewPairs(),
        getProducts(),
        getScans(),
        getMetrics()
      ]);
      if (!active) return;
      const [backend, pairsResult, productsResult, scansResult, metricsResult] = results;
      const failures = results.filter((result) => result.status === "rejected");
      const pairsPayload = pairsResult.status === "fulfilled" ? pairsResult.value : [];
      const pairs = Array.isArray(pairsPayload) ? pairsPayload : pairsPayload?.pairs || [];
      const products = productsResult.status === "fulfilled" ? productsResult.value || [] : [];
      const scans = scansResult.status === "fulfilled" ? scansResult.value || [] : [];
      const metrics = metricsResult.status === "fulfilled" ? metricsResult.value : null;
      const backendItems = backend.status === "fulfilled"
        ? normalizeBackendNotifications(backend.value) || normalizeBackendNotifications(pairsPayload?.notifications)
        : normalizeBackendNotifications(pairsPayload?.notifications);
      setNotifications(backendItems ?? deriveNotifications({ pairs, products, scans, metrics }));
      setError(failures.length ? "Some notification data could not be loaded. Available updates are shown." : "");
      setLoading(false);
    }
    load();
    return () => { active = false; };
  }, []);

  const markRead = useCallback((id) => {
    setReadIds((current) => {
      const next = current.includes(id) ? current : [...current, id];
      persistReadIds(next);
      return next;
    });
  }, []);

  const markAllAsRead = useCallback(() => {
    setReadIds((current) => {
      const next = [...new Set([...current, ...notifications.map((item) => item.id)])];
      persistReadIds(next);
      return next;
    });
  }, [notifications]);

  const items = notifications.map((item) => ({ ...item, unread: item.unread !== false && !readIds.includes(item.id) }));
  return {
    notifications: items,
    unreadCount: items.filter((item) => item.unread).length,
    loading,
    error,
    markRead,
    markAllAsRead
  };
}
