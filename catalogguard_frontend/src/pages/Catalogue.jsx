import React, { useMemo, useState } from "react";
import { Search, Package, ArrowUpRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useProducts } from "../hooks/useProducts";
import DataTable from "../components/DataTable";

export default function Catalogue() {
  const { products, loading, error } = useProducts();
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const rows = useMemo(() => products.filter((p) => `${p.id} ${p.title} ${p.brand} ${p.model} ${p.sku}`.toLowerCase().includes(search.toLowerCase())), [products, search]);
  return <div className="page-content">
    <div className="page-toolbar"><div><div className="overline">PRODUCT DATA</div><h2>Catalogue products</h2><p>Inspect product records without modifying the source catalogue.</p></div><div className="catalogue-count"><Package size={18} /><strong>{products.length}</strong><span>products loaded</span></div></div>
    <section className="panel">
      <div className="panel-heading"><div><h3>All products</h3><p>Search by title, brand, model, SKU or product ID.</p></div></div>
      <label className="search-field wide-search"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Find a product..." /></label>
      {error && <div className="error-banner">{error}</div>}
      {loading ? <div className="loading-panel">Loading catalogue…</div> : <DataTable columns={[
        { key: "id", label: "PRODUCT ID", render: (v) => <strong className="table-id">{v}</strong> },
        { key: "title", label: "PRODUCT", render: (v, row) => <div className="catalogue-product"><img src={row.image || "/images/product-placeholder.svg"} alt="" /><div><strong>{v}</strong><span>{row.brand || "Brand missing"}</span></div></div> },
        { key: "model", label: "MODEL" }, { key: "category", label: "CATEGORY" },
        { key: "price", label: "PRICE", render: (v) => `₹${Number(v || 0).toLocaleString("en-IN")}` },
        { key: "status", label: "STATUS" }
      ]} rows={rows} onRowClick={(row) => navigate(`/queue?product=${row.id}`)} emptyMessage="No products match your search." />}
    </section>
    <div className="inline-info"><ArrowUpRight size={16} /> Selecting a product opens the review queue; source catalogue writes are intentionally disabled in this pilot.</div>
  </div>;
}
