import { apiRequest, DEMO_MODE } from "./client";
import { getProducts } from "./products";
import { getReviewPairs } from "./reviews";

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url; link.download = filename; link.click();
  URL.revokeObjectURL(url);
}

export async function exportData(format = "csv", kind = "reviews") {
  if (!DEMO_MODE) {
    const result = await apiRequest(`/api/exports?format=${format}&type=${kind}`);
    if (result instanceof Blob) downloadBlob(result, `catalogguard-${kind}.${format}`);
    return result;
  }
  const rows = kind === "products" ? await getProducts() : await getReviewPairs();
  if (format === "json") {
    downloadBlob(new Blob([JSON.stringify(rows, null, 2)], { type: "application/json" }), `catalogguard-${kind}.json`);
    return;
  }
  const columns = rows.length ? Object.keys(rows[0]) : [];
  const escape = (v) => `"${String(typeof v === "object" ? JSON.stringify(v) : v ?? "").replaceAll('"', '""')}"`;
  const csv = [columns.join(","), ...rows.map((row) => columns.map((key) => escape(row[key])).join(","))].join("\n");
  downloadBlob(new Blob([csv], { type: "text/csv;charset=utf-8" }), `catalogguard-${kind}.csv`);
}
