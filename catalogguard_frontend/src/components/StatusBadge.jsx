import React from "react";

export default function StatusBadge({ status = "pending" }) {
  const label = {
    pending: "Pending review", accepted: "Accepted", rejected: "Rejected",
    flagged: "Flagged", completed: "Completed", queued: "Queued", active: "Active"
  }[status] || status;
  return <span className={`status-badge status-${String(status).toLowerCase()}`}>{label}</span>;
}
