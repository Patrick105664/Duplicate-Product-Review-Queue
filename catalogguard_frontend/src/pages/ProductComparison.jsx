import React, { useEffect, useState } from "react";
import { ArrowLeft, CircleAlert, ShieldCheck } from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";
import ProductCard from "../components/ProductCard";
import EvidencePanel from "../components/EvidencePanel";
import ReviewActions from "../components/ReviewActions";
import StatusBadge from "../components/StatusBadge";
import { getReviewPair } from "../api/reviews";
import { getProducts } from "../api/products";
import { submitDecision } from "../api/reviews";

export default function ProductComparison() {
  const { pairId } = useParams();
  const navigate = useNavigate();
  const [pair, setPair] = useState(null);
  const [products, setProducts] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([getReviewPair(pairId), getProducts()]).then(([p, prods]) => { setPair(p); setProducts(prods || []); }).catch((e) => setError(e.message));
  }, [pairId]);
  const left = products.find((p) => p.id === pair?.leftId), right = products.find((p) => p.id === pair?.rightId);
  async function decide(decision, note) {
    try { await submitDecision(pair.id, decision, note); setPair({ ...pair, status: decision, decisionNote: note }); }
    catch (e) { setError(e.message); }
  }
  if (error && !pair) return <div className="page-content"><div className="error-banner">{error}</div><Link to="/queue">Back to queue</Link></div>;
  if (!pair) return <div className="page-content"><div className="loading-panel">Loading product comparison…</div></div>;
  return <div className="page-content">
    <div className="breadcrumb-row"><button className="back-link" onClick={() => navigate("/queue")}><ArrowLeft size={16} /> Back to review queue</button><span className="breadcrumb-separator">/</span><span>{pair.id}</span><StatusBadge status={pair.status} /></div>
    <div className="page-toolbar comparison-title"><div><div className="overline">PRODUCT MATCH REVIEW</div><h2>Compare product details</h2><p>Confirm whether these records represent the exact same sellable product.</p></div><span className="pair-id-large">{pair.id}</span></div>
    <div className="comparison-layout"><div className="comparison-main">
      <div className="compare-cards"><ProductCard product={left} side="A" /><div className="compare-divider"><span>VS</span><div /></div><ProductCard product={right} side="B" /></div>
      <section className="panel attribute-panel"><div className="panel-heading"><div><h3>Attribute comparison</h3><p>Differences that may affect duplicate decisions</p></div></div><div className="attribute-table">
        {[["Brand", left?.brand, right?.brand], ["Model", left?.model, right?.model], ["Title", left?.title, right?.title], ["Price", left ? `₹${left.price}` : "—", right ? `₹${right.price}` : "—"], ["SKU", left?.sku, right?.sku], ["Category", left?.category, right?.category]].map(([name, a, b]) => <div className="attribute-row" key={name}><strong>{name}</strong><span className={a !== b ? "attribute-diff" : ""}>{a || "—"}</span><span className={a !== b ? "attribute-diff" : ""}>{b || "—"}</span></div>)}
      </div></section>
      <section className="panel decision-panel"><div className="panel-heading"><div><h3>Reviewer decision</h3><p>Your decision is recorded for audit; no catalogue records are changed.</p></div><ShieldCheck size={20} /></div><ReviewActions onDecision={decide} disabled={pair.status !== "pending"} />{pair.status !== "pending" && <div className="decision-recorded"><ShieldCheck size={16} /> Decision recorded: <strong>{pair.status}</strong>{pair.decisionNote ? ` — ${pair.decisionNote}` : ""}</div>}</section>
    </div><aside className="comparison-aside"><EvidencePanel pair={pair} /><div className="safety-callout"><CircleAlert size={17} /><div><strong>Protect product variants</strong><p>A single item and a multipack are not duplicates. Similar titles alone are not sufficient evidence.</p></div></div></aside></div>
  </div>;
}
