import React, { useMemo, useState } from "react";
import { Search, SlidersHorizontal, ArrowUpDown, GitCompare, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useQueue } from "../hooks/useQueue";
import { useProducts } from "../hooks/useProducts";
import StatusBadge from "../components/StatusBadge";
import { formatPackQuantity } from "../utils/formatters";

export default function ReviewQueue() {
  const { pairs, loading, error, refresh } = useQueue();
  const { products } = useProducts();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("pending");
  const [sort, setSort] = useState("score");
  const navigate = useNavigate();
  const filtered = useMemo(() => pairs.filter((pair) => {
    const a = products.find((p) => p.id === pair.leftId);
    const b = products.find((p) => p.id === pair.rightId);
    const matches = `${pair.id} ${a?.title} ${b?.title} ${a?.brand} ${b?.brand}`.toLowerCase().includes(search.toLowerCase());
    return matches && (filter === "all" || pair.status === filter);
  }).sort((a, b) => sort === "score" ? b.score - a.score : new Date(b.createdAt) - new Date(a.createdAt)), [pairs, products, search, filter, sort]);
  return <div className="page-content">
    <div className="page-toolbar"><div><div className="overline">MATCH MANAGEMENT</div><h2>Suggested product pairs <span className="count-bubble">{filtered.length}</span></h2><p>Review each suggestion using product attributes and evidence signals.</p></div><button className="button button-secondary" onClick={refresh}><RefreshCw size={15} /> Refresh queue</button></div>
    <div className="queue-toolbar panel">
      <label className="search-field"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search products or pair ID..." /></label>
      <div className="filter-group"><SlidersHorizontal size={16} /><select value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filter status"><option value="pending">Pending review</option><option value="accepted">Accepted</option><option value="rejected">Rejected</option><option value="flagged">Flagged</option><option value="all">All statuses</option></select></div>
      <div className="filter-group"><ArrowUpDown size={16} /><select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort queue"><option value="score">Highest score</option><option value="date">Newest first</option></select></div>
    </div>
    {error && <div className="error-banner">{error}</div>}
    {loading ? <div className="loading-panel">Loading review suggestions…</div> : <div className="queue-list">
      {filtered.map((pair) => {
        const a = products.find((p) => p.id === pair.leftId), b = products.find((p) => p.id === pair.rightId);
        return <article className="queue-card" key={pair.id}>
          <div className="queue-card-main"><div className="queue-card-top"><span className="table-id">{pair.id}</span><StatusBadge status={pair.status} /><span className={`score-pill ${pair.score >= .9 ? "high" : pair.score >= .7 ? "mid" : "low"}`}>{Math.round(pair.score * 100)}% match</span></div>
            <div className="queue-products"><div className="queue-product"><img src={a?.image || "/images/product-placeholder.svg"} alt="" /><div><div className="queue-product-title"><strong>{a?.title || pair.leftId}</strong><span className="pack-quantity-badge">{formatPackQuantity(a?.pack_quantity)}</span></div><span>{a?.brand || "Unknown brand"} · {a?.model || "No model"} · {a?.size || "—"}</span><b>₹{Number(a?.price || 0).toLocaleString("en-IN")}</b></div></div><div className="versus">VS</div><div className="queue-product"><img src={b?.image || "/images/product-placeholder.svg"} alt="" /><div><div className="queue-product-title"><strong>{b?.title || pair.rightId}</strong><span className="pack-quantity-badge">{formatPackQuantity(b?.pack_quantity)}</span></div><span>{b?.brand || "Unknown brand"} · {b?.model || "No model"} · {b?.size || "—"}</span><b>₹{Number(b?.price || 0).toLocaleString("en-IN")}</b></div></div></div>
            <p className="queue-reason">{pair.reason}</p><div className="signal-tags">{(pair.signals || []).slice(0, 4).map((s) => <span key={s}>{s}</span>)}</div>
          </div><div className="queue-card-side"><span className="muted-label">Suggested status</span><strong>{pair.label || "Review required"}</strong><button className="button button-primary" onClick={() => navigate(`/compare/${pair.id}`)}><GitCompare size={15} /> Review pair</button></div>
        </article>;
      })}
      {!filtered.length && <div className="empty-state"><GitCompare size={28} /><h3>No matching pairs</h3><p>Try another filter or search term.</p></div>}
    </div>}
  </div>;
}
