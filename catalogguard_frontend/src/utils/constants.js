export const APP_NAME = "Duplicate Product Review Queue";

export const NAV_ITEMS = [
  { label: "Overview", path: "/dashboard", icon: "layout-dashboard" },
  { label: "Review queue", path: "/queue", icon: "git-compare", count: "12" },
  { label: "Catalogue", path: "/catalogue", icon: "package" },
  { label: "Scan history", path: "/scans", icon: "scan-search" },
  { label: "Evaluation", path: "/evaluation", icon: "chart-no-axes-combined" },
  { label: "Exports & reports", path: "/exports", icon: "file-down" }
];

export const REVIEW_STATUSES = {
  pending: "Pending review",
  accepted: "Accepted",
  rejected: "Rejected",
  flagged: "Flagged"
};
