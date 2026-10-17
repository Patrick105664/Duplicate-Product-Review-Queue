import React from "react";

export default function StatCard({ label, value, change, icon: Icon, tone = "mint", footnote }) {
  return <article className="stat-card">
    <div className="stat-top"><span>{label}</span><div className={`stat-icon ${tone}`}>{Icon && <Icon size={19} />}</div></div>
    <div className="stat-value">{value}</div>
    <div className="stat-bottom">{change && <span className="stat-change">{change}</span>}<span>{footnote || "vs. previous period"}</span></div>
  </article>;
}
