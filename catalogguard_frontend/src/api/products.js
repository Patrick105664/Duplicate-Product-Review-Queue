import { apiRequest, DEMO_MODE } from "./client";

export const demoProducts = [
  { product_id: "P-1042", title: "AeroSound Wireless Headphones", brand: "AeroSound", model: "AS-500", pack_quantity: 1, size: "Standard", category: "Electronics", price: 2499, sku: "AS500-BLK", status: "active", image: "/images/headphones.svg", updatedAt: "2026-10-16" },
  { product_id: "P-1043", title: "AeroSound AS-500 Bluetooth Headphones", brand: "AeroSound", model: "AS-500", pack_quantity: 1, size: "Standard", category: "Electronics", price: 2499, sku: "AS500-BLK-2", status: "active", image: "/images/headphones.svg", updatedAt: "2026-10-15" },
  { product_id: "P-2081", title: "HydraSip Stainless Steel Bottle 750ml", brand: "HydraSip", model: "HS750", pack_quantity: 1, size: "750 ml", category: "Home & Kitchen", price: 799, sku: "HS-750-GRN", status: "active", image: "/images/bottle.svg", updatedAt: "2026-10-14" },
  { product_id: "P-2082", title: "HydraSip Steel Bottle 750 ml — Set of 2", brand: "HydraSip", model: "HS750-2PK", pack_quantity: 2, size: "750 ml", category: "Home & Kitchen", price: 1399, sku: "HS-750-2", status: "active", image: "/images/bottle.svg", updatedAt: "2026-10-14" },
  { product_id: "P-3107", title: "LumaDesk LED Study Lamp", brand: "LumaDesk", model: "LD-20", pack_quantity: 1, size: "Standard", category: "Home & Office", price: 1199, sku: "LD20-WHT", status: "active", image: "/images/lamp.svg", updatedAt: "2026-10-12" },
  { product_id: "P-3108", title: "LumaDesk LED Desk Lamp Pro", brand: "LumaDesk", model: "LD-20P", pack_quantity: 1, size: "Standard", category: "Home & Office", price: 1599, sku: "LD20P-WHT", status: "active", image: "/images/lamp.svg", updatedAt: "2026-10-11" }
];

const textField = (datasetValue, camelValue, legacyValue) =>
  [datasetValue, camelValue, legacyValue].find((value) => typeof value === "string" && value.trim())?.trim() || "—";

export function normalizeProduct(product) {
  if (!product) return product;
  const title = textField(product.title, null, null);
  const rawQuantity = product.pack_quantity ?? product.packQuantity;
  const parsedQuantity = title.match(/(?:set|pack)\s+of\s+(\d+)/i)?.[1];
  const quantity = Number(rawQuantity);
  const packQuantity = Number.isInteger(quantity) && quantity > 0
    ? quantity
    : Number(parsedQuantity) > 0 ? Number(parsedQuantity) : 1;
  const productId = textField(product.product_id, product.productId, product.id);
  const brand = textField(product.brand, null, null);
  const model = textField(product.model, null, null);
  const size = textField(product.size, null, null);
  return {
    ...product,
    product_id: productId,
    productId,
    id: productId,
    title,
    brand,
    model,
    pack_quantity: packQuantity,
    packQuantity,
    size
  };
}

export async function getProducts() {
  const products = DEMO_MODE ? demoProducts : await apiRequest("/api/products");
  return (products || []).map(normalizeProduct);
}

export async function getProduct(id) {
  const product = DEMO_MODE ? demoProducts.find((p) => p.product_id === id) : await apiRequest(`/api/products/${id}`);
  return normalizeProduct(product);
}
