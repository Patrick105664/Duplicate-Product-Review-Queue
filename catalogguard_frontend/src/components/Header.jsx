import React from "react";
import { Bell, ChevronDown, Search, Sparkles } from "lucide-react";
import { useLocation } from "react-router-dom";
import { useAuth, initials } from "../auth";

const titles = {
  "/dashboard": ["Overview", "Here’s what’s happening across your catalogue."],
  "/queue": ["Review queue", "Inspect suggested product matches and make the final call."],
  "/catalogue": ["Catalogue", "Browse products and inspect catalogue attributes."],
  "/scans": ["Scan history", "Track duplicate-detection runs and their outcomes."],
  "/evaluation": ["Evaluation & quality", "Measure matching quality against labelled data."],
  "/exports": ["Exports & reports", "Download review and catalogue data for analysis."]
};

export default function Header() {
  const location = useLocation();
  const { user } = useAuth();
  const [title, subtitle] = titles[location.pathname] || ["Product comparison", "Review evidence before deciding."];
  return <header className="topbar">
    <div className="mobile-brand"><Sparkles size={19} /> Duplicate Product Review Queue</div>
    <div className="page-heading"><h1>{title}</h1><p>{subtitle}</p></div>
    <div className="topbar-actions">
      <label className="global-search"><Search size={16} /><input placeholder="Search anything..." aria-label="Search anything" /><kbd>⌘ K</kbd></label>
      <button className="icon-button" aria-label="Notifications"><Bell size={18} /><i /></button>
      <div className="top-profile"><div className="avatar">{initials(user?.name)}</div><ChevronDown size={15} /></div>
    </div>
  </header>;
}
