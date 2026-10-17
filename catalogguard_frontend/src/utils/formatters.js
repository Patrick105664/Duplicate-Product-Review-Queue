export const formatNumber = (value) =>
  new Intl.NumberFormat("en-IN").format(Number(value || 0));

export const formatDate = (value) => {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit", month: "short", year: "numeric"
  }).format(new Date(value));
};

export const formatDateTime = (value) => {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit"
  }).format(new Date(value));
};

export const percentage = (numerator, denominator) =>
  denominator ? `${Math.round((numerator / denominator) * 100)}%` : "—";

export const titleCase = (value = "") =>
  value.replace(/[_-]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
