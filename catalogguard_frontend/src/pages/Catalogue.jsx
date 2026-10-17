import React, { useMemo, useState } from "react";
import { Search, Package, ArrowUpRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useProducts } from "../hooks/useProducts";
import { useQueue } from "../hooks/useQueue";
import DataTable from "../components/DataTable";
import { formatPackQuantity } from "../utils/formatters";

export default function Catalogue() {
  const { products, loading, error } = useProducts();
  const { pairs, loading: pairsLoading, error: pairsError } = useQueue();
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const duplicateCounts = useMemo(() => {
    const duplicatesByProduct = new Map();
    pairs.filter((pair) => pair.score >= 0.7 && pair.status !== "rejected").forEach((pair) => {
      [[pair.leftId, pair.rightId], [pair.rightId, pair.leftId]].forEach(([productId, duplicateId]) => {
        if (!duplicatesByProduct.has(productId)) duplicatesByProduct.set(productId, new Set());
        duplicatesByProduct.get(productId).add(duplicateId);
      });
    });
    return duplicatesByProduct;
  }, [pairs]);
  const rows = useMemo(() => products.filter((product) => `${product.product_id} ${product.title} ${product.brand} ${product.model} ${product.size}`.toLowerCase().includes(search.toLowerCase()))
    .map((product) => ({ ...product, duplicateCount: duplicateCounts.get(product.product_id)?.size || 0 })), [products, search, duplicateCounts]);
  return <div className="page-content">
    <div className="page-toolbar"><div><div className="overline">PRODUCT DATA</div><h2>Catalogue products</h2><p>Inspect product records without modifying the source catalogue.</p></div><div className="catalogue-count"><Package size={18} /><strong>{products.length}</strong><span>products loaded</span></div></div>
    <section className="panel">
      <div className="panel-heading"><div><h3>All products</h3><p>Search by product ID, title, brand, model or size.</p></div></div>
      <label className="search-field wide-search"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Find by product ID, title, brand, model or size..." /></label>
      {(error || pairsError) && <div className="error-banner">{error || pairsError}</div>}
      {loading ? <div className="loading-panel">Loading catalogue…</div> : <DataTable className="catalogue-table" columns={[
        { key: "product_id", label: "Product ID", render: (v) => <strong className="table-id">{v}</strong> },
        { key: "title", label: "Title", render: (v, row) => <div className="catalogue-product"><img src={row.image || "/images/product-placeholder.svg"} alt="" /><div><strong>{v}</strong></div></div> },
        { key: "brand", label: "Brand" },
        { key: "model", label: "Model" },
        { key: "pack_quantity", label: "Pack quantity", render: (quantity) => <span className="pack-quantity-badge">{quantity === 1 ? "1" : formatPackQuantity(quantity)}</span> },
        { key: "size", label: "Size", render: (size) => size === "—" ? "—" : <span className="size-badge">{size}</span> },
        { key: "duplicateCount", label: "Duplicates", render: (count) => <span className={`duplicate-count ${count ? "has-duplicates" : ""}`} aria-label={`${count} duplicates`}>{pairsLoading ? "—" : count}</span> },
      ]} rows={rows} onRowClick={(row) => navigate(`/queue?product=${row.product_id}`)} emptyMessage="No products match your search." />}
    </section>
    <div className="inline-info"><ArrowUpRight size={16} /> Selecting a product opens the review queue; source catalogue writes are intentionally disabled in this pilot.</div>
  </div>;
}
