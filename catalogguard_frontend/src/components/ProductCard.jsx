import React from "react";
import { BadgeCheck, Package } from "lucide-react";

export default function ProductCard({ product, side }) {
  if (!product) return <article className="product-card empty-product">No product details available.</article>;
  return <article className="product-card">
    <div className="product-card-top"><span className="eyebrow">PRODUCT {side || ""}</span><span className="product-id">{product.id}</span></div>
    <div className="product-image-wrap"><img src={product.image || "/images/product-placeholder.svg"} alt={product.title} onError={(e) => { e.currentTarget.src = "/images/product-placeholder.svg"; }} /></div>
    <h3>{product.title}</h3>
    <p className="product-brand">{product.brand || "Brand not provided"}</p>
    <div className="product-price">₹{Number(product.price || 0).toLocaleString("en-IN")}</div>
    <div className="product-meta-grid">
      <div><span>Model</span><strong>{product.model || "—"}</strong></div>
      <div><span>Category</span><strong>{product.category || "—"}</strong></div>
      <div><span>SKU</span><strong>{product.sku || "—"}</strong></div>
      <div><span>Catalogue</span><strong><BadgeCheck size={13} /> Active</strong></div>
    </div>
  </article>;
}
