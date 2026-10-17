import React, { useState } from "react";
import { Download, FileJson, FileSpreadsheet, Package, GitCompare, ShieldCheck } from "lucide-react";
import { exportData } from "../api/exports";

export default function Exports() {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState("");
  async function download(kind, format) {
    const key = `${kind}-${format}`; setBusy(key); setMessage("");
    try { await exportData(format, kind); setMessage(`Your ${kind} ${format.toUpperCase()} export has been prepared.`); }
    catch (e) { setMessage(`Export failed: ${e.message}`); }
    finally { setBusy(""); }
  }
  return <div className="page-content">
    <div className="page-toolbar"><div><div className="overline">DATA & REPORTING</div><h2>Exports & reports</h2><p>Download review decisions and catalogue snapshots for offline analysis.</p></div></div>
    {message && <div className="toast-message">{message}<button onClick={() => setMessage("")}>Dismiss</button></div>}
    <div className="export-grid">
      <article className="panel export-card"><div className="export-icon mint"><GitCompare size={23} /></div><h3>Review pairs</h3><p>Suggested pairs, pack quantities, confidence scores, evidence signals and recorded reviewer decisions.</p><div className="export-actions"><button className="button button-secondary" disabled={!!busy} onClick={() => download("reviews", "csv")}><FileSpreadsheet size={16} /> {busy === "reviews-csv" ? "Preparing…" : "Export CSV"}</button><button className="button button-secondary" disabled={!!busy} onClick={() => download("reviews", "json")}><FileJson size={16} /> JSON</button></div></article>
      <article className="panel export-card"><div className="export-icon lavender"><Package size={23} /></div><h3>Product catalogue</h3><p>Product IDs, titles, brands, models, categories, prices and SKU fields.</p><div className="export-actions"><button className="button button-secondary" disabled={!!busy} onClick={() => download("products", "csv")}><FileSpreadsheet size={16} /> {busy === "products-csv" ? "Preparing…" : "Export CSV"}</button><button className="button button-secondary" disabled={!!busy} onClick={() => download("products", "json")}><FileJson size={16} /> JSON</button></div></article>
    </div>
    <section className="panel export-notice"><ShieldCheck size={22} /><div><h3>Audit-friendly exports</h3><p>Keep the reviewer decision and note alongside the pair ID. Exports are for analysis only; they do not apply changes to the source catalogue.</p></div></section>
  </div>;
}
