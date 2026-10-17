import { useAuth } from "../auth";
import React, { useEffect, useState } from "react";
import { ArrowUpRight, CheckCircle2, CircleAlert, Clock3, GitCompare, Package, Plus, ScanSearch, Sparkles } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import StatCard from "../components/StatCard";
import DataTable from "../components/DataTable";
import { getMetrics } from "../api/metrics";
import { getReviewPairs } from "../api/reviews";
import { getProducts } from "../api/products";
import { startRescan } from "../api/scans";
import { DEMO_MODE } from "../api/client";
import { formatCurrencyINR } from "../utils/formatters";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [pairs, setPairs] = useState([]);
  const [products, setProducts] = useState([]);
  const [toast, setToast] = useState("");
  const navigate = useNavigate();
  const { user } = useAuth();
  useEffect(() => { Promise.all([getMetrics(), getReviewPairs(), getProducts()]).then(([m, p, prods]) => { setMetrics(m); setPairs(p); setProducts(prods); }).catch(() => setToast("Some dashboard data could not be loaded.")); }, []);
  const pending = pairs.filter((p) => p.status === "pending");
  async function runScan() { try { const result = await startRescan({ source: "current-catalogue" }); setToast(result.message || `Scan ${result.id} started.`); } catch (e) { setToast(e.message); } }
  return <div className="page-content">
    {DEMO_MODE && <div className="demo-banner"><Sparkles size={16} /><span><strong>Demo workspace</strong> — sample data is shown. Connect your backend and set <code>VITE_DEMO_MODE=false</code> to use live API data.</span></div>}
    {toast && <div className="toast-message" role="status">{toast}<button onClick={() => setToast("")}>Dismiss</button></div>}
    <div className="welcome-row"><div><div className="overline">FRIDAY, OCTOBER 16, 2026</div><h2>Good afternoon, {user?.name?.split(" ")[0] || "there"} <span>✦</span></h2><p>Your catalogue is looking healthy. Here’s your review snapshot.</p></div><div className="welcome-actions"><button className="button button-secondary" onClick={() => navigate("/queue")}><GitCompare size={16} /> Open review queue</button><button className="button button-primary" onClick={runScan}><Plus size={16} /> Run new scan</button></div></div>
    <div className="stats-grid">
      <StatCard label="Catalogue products" value={metrics?.totalProducts ?? "—"} icon={Package} tone="mint" change="+8.4%" />
      <StatCard label="Pending review" value={pending.length || metrics?.pendingReviews || 0} icon={Clock3} tone="lavender" change="Needs attention" footnote="awaiting a human decision" />
      <StatCard label="Accepted this week" value={metrics?.acceptedThisWeek ?? "—"} icon={CheckCircle2} tone="peach" change="+12.5%" />
      <StatCard label="Scans this month" value={metrics?.scansThisMonth ?? "—"} icon={ScanSearch} tone="blue" change="All completed" />
    </div>
    <div className="dashboard-grid">
      <section className="panel recent-panel">
        <div className="panel-heading"><div><h3>Needs your attention</h3><p>Suggested pairs waiting for a decision</p></div><Link className="text-link" to="/queue">View all <ArrowUpRight size={15} /></Link></div>
        <DataTable columns={[
          { key: "id", label: "PAIR ID", render: (v) => <strong className="table-id">{v}</strong> },
          { key: "products", label: "PRODUCT PAIR", render: (_, row) => { const a = products.find((p) => p.id === row.leftId); const b = products.find((p) => p.id === row.rightId); return <div className="pair-cell"><strong>{a?.title || row.leftId}</strong><span>{b?.title || row.rightId}</span></div>; } },
          { key: "score", label: "MATCH SCORE", render: (v) => <span className={`score-pill ${v >= .9 ? "high" : v >= .7 ? "mid" : "low"}`}>{Math.round(v * 100)}%</span> },
          { key: "status", label: "STATUS" }
        ]} rows={pending.slice(0, 4)} onRowClick={(row) => navigate(`/compare/${row.id}`)} emptyMessage="You're all caught up!" />
      </section>
      <section className="panel quick-panel">
        <div className="panel-heading"><div><h3>Quick actions</h3><p>Keep your catalogue in shape</p></div><div className="soft-icon"><Sparkles size={17} /></div></div>
        <button className="quick-action" onClick={() => navigate("/queue")}><div className="quick-icon mint"><GitCompare size={18} /></div><div><strong>Review suggested matches</strong><small>{pending.length} pairs waiting for review</small></div><ArrowUpRight size={16} /></button>
        <button className="quick-action" onClick={runScan}><div className="quick-icon lavender"><ScanSearch size={18} /></div><div><strong>Run duplicate scan</strong><small>Check the latest catalogue data</small></div><ArrowUpRight size={16} /></button>
        <button className="quick-action" onClick={() => navigate("/evaluation")}><div className="quick-icon peach"><CheckCircle2 size={18} /></div><div><strong>Check match quality</strong><small>Review precision and recall</small></div><ArrowUpRight size={16} /></button>
        <div className="quick-footnote">Human review is required before any future catalogue write.</div>
      </section>
    </div>
    <div className="bottom-grid">
      <section className="panel quality-mini"><div className="panel-heading"><div><h3>Matching quality</h3><p>Evaluation metrics</p></div><Link to="/evaluation" className="text-link">Details <ArrowUpRight size={15} /></Link></div>
        <div className="quality-metrics">
          <div><span>Precision</span><strong>{metrics?.precision ?? "—"}{metrics?.precision != null ? "%" : ""}</strong><div className="progress-track"><span style={{ width: `${metrics?.precision || 0}%` }} /></div><small>{metrics?.precisionCorrect ?? 0} correct / {metrics?.precisionReviewed ?? 0} reviewed</small></div>
          <div><span>Recall</span><strong>{metrics?.recall ?? "—"}{metrics?.recall != null ? "%" : ""}</strong><div className="progress-track lavender-track"><span style={{ width: `${metrics?.recall || 0}%` }} /></div><small>{metrics?.recallFound ?? 0} found / {metrics?.recallExpected ?? 0} expected</small></div>
          <div className="false-merge-metric">
            <span className="metric-label-with-info">False merge cost <button className="metric-info" type="button" aria-label="About false merge cost" title={`Estimated damage per incorrect product merge. Formula: labour ${formatCurrencyINR((metrics?.labourMinutes || 0) / 60 * (metrics?.labourRatePerHour || 0))} + downstream loss ${formatCurrencyINR(metrics?.downstreamLoss)} + customer remediation ${formatCurrencyINR(metrics?.remediationCost)} = ${formatCurrencyINR(metrics?.falseMergeCostPerMerge)}.`}><CircleAlert size={13} /></button></span>
            <strong>{metrics ? formatCurrencyINR(metrics.falseMergeCostPerMerge) : "—"}</strong>
            <small>{metrics ? `${metrics.falseMergeCount} false merges x ${formatCurrencyINR(metrics.falseMergeCostPerMerge)} = ${formatCurrencyINR(metrics.falseMergeExposure)} est. exposure` : "Estimated correction and downstream cost"}</small>
          </div>
        </div>
        <p className="false-merge-notice">Review the false merge cost before enabling bulk automation.</p>
        <p className="metric-disclaimer">{metrics?.note}</p>
      </section>
      <section className="panel safety-panel"><div className="safety-illustration"><div className="shield-orb"><CheckCircle2 size={28} /></div><div className="orb-dot dot-one" /><div className="orb-dot dot-two" /></div><div><h3>Human-first by design</h3><p>Accepting a match records a review decision only. Distinct product variants stay protected from accidental merges.</p><Link to="/evaluation" className="text-link">Read quality safeguards <ArrowUpRight size={15} /></Link></div></section>
    </div>
  </div>;
}
