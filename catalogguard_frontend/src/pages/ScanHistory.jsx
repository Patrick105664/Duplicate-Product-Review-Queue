import React, { useEffect, useState } from "react";
import { ScanSearch, RefreshCw, Plus } from "lucide-react";
import { getScans, startRescan } from "../api/scans";
import DataTable from "../components/DataTable";
import StatusBadge from "../components/StatusBadge";

export default function ScanHistory() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  async function load() { setLoading(true); try { setScans(await getScans() || []); setError(""); } catch (e) { setError(e.message); } finally { setLoading(false); } }
  useEffect(() => { load(); }, []);
  async function run() { try { const result = await startRescan(); setMessage(result.message || `Scan ${result.id} started.`); await load(); } catch (e) { setError(e.message); } }
  return <div className="page-content">
    <div className="page-toolbar"><div><div className="overline">DETECTION RUNS</div><h2>Scan history</h2><p>Review previous scans, source files and suggested-pair counts.</p></div><button className="button button-primary" onClick={run}><Plus size={16} /> Run new scan</button></div>
    {message && <div className="toast-message">{message}<button onClick={() => setMessage("")}>Dismiss</button></div>}{error && <div className="error-banner">{error}</div>}
    <section className="panel"><div className="panel-heading"><div><h3>Recent scans</h3><p>Runs shown here may be demo data until the API is connected.</p></div><button className="icon-button plain" onClick={load} aria-label="Refresh scans"><RefreshCw size={17} /></button></div>
      {loading ? <div className="loading-panel">Loading scan history…</div> : <DataTable columns={[
        { key: "id", label: "SCAN ID", render: (v) => <strong className="table-id">{v}</strong> },
        { key: "startedAt", label: "STARTED", render: (v) => v ? new Date(v).toLocaleString("en-IN") : "—" },
        { key: "source", label: "SOURCE" }, { key: "products", label: "PRODUCTS SCANNED" },
        { key: "pairs", label: "PAIRS SUGGESTED" }, { key: "duration", label: "DURATION" },
        { key: "status", label: "STATUS", render: (v) => <StatusBadge status={v} /> }
      ]} rows={scans} emptyMessage="No scans have been recorded." />}
    </section>
    <div className="scan-footnote"><ScanSearch size={18} /><div><strong>Suggestion-only pilot</strong><p>A scan generates candidates for human review. It does not merge products or write to the catalogue.</p></div></div>
  </div>;
}
