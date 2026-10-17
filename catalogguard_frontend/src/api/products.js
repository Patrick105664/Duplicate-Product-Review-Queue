import { apiRequest, DEMO_MODE } from "./client";

export const demoProducts = [
  { id: "P-1042", title: "AeroSound Wireless Headphones", brand: "AeroSound", model: "AS-500", category: "Electronics", price: 2499, sku: "AS500-BLK", status: "active", image: "/images/headphones.svg", updatedAt: "2026-10-16" },
  { id: "P-1043", title: "AeroSound AS-500 Bluetooth Headphones", brand: "AeroSound", model: "AS-500", category: "Electronics", price: 2499, sku: "AS500-BLK-2", status: "active", image: "/images/headphones.svg", updatedAt: "2026-10-15" },
  { id: "P-2081", title: "HydraSip Stainless Steel Bottle 750ml", brand: "HydraSip", model: "HS750", category: "Home & Kitchen", price: 799, sku: "HS-750-GRN", status: "active", image: "/images/bottle.svg", updatedAt: "2026-10-14" },
  { id: "P-2082", title: "HydraSip Steel Bottle 750 ml — Set of 2", brand: "HydraSip", model: "HS750-2PK", category: "Home & Kitchen", price: 1399, sku: "HS-750-2", status: "active", image: "/images/bottle.svg", updatedAt: "2026-10-14" },
  { id: "P-3107", title: "LumaDesk LED Study Lamp", brand: "LumaDesk", model: "LD-20", category: "Home & Office", price: 1199, sku: "LD20-WHT", status: "active", image: "/images/lamp.svg", updatedAt: "2026-10-12" },
  { id: "P-3108", title: "LumaDesk LED Desk Lamp Pro", brand: "LumaDesk", model: "LD-20P", category: "Home & Office", price: 1599, sku: "LD20P-WHT", status: "active", image: "/images/lamp.svg", updatedAt: "2026-10-11" }
];

export async function getProducts() {
  if (DEMO_MODE) return demoProducts;
  return apiRequest("/api/products");
}

export async function getProduct(id) {
  if (DEMO_MODE) return demoProducts.find((p) => p.id === id);
  return apiRequest(`/api/products/${id}`);
}
