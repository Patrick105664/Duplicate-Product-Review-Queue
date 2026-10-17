import React, { useState } from "react";
import { Search, Sparkles } from "lucide-react";
import { useLocation } from "react-router-dom";
import AccountMenu from "./AccountMenu";
import NotificationMenu from "./NotificationMenu";

const titles = {
  "/dashboard": ["Overview", "Here’s what’s happening across your catalogue."],
  "/queue": ["Review queue", "Inspect suggested product matches and make the final call."],
  "/catalogue": ["Catalogue", "Browse products and inspect catalogue attributes."],
  "/scans": ["Scan history", "Track duplicate-detection runs and their outcomes."],
  "/scan-history": ["Scan history", "Track duplicate-detection runs and their outcomes."],
  "/evaluation": ["Evaluation & quality", "Measure matching quality against labelled data."],
  "/exports": ["Exports & reports", "Download review and catalogue data for analysis."],
  "/settings": ["Account settings", "Manage your profile information."]
};

export default function Header() {
  const location = useLocation();
  const [openMenu, setOpenMenu] = useState(null);
  const [title, subtitle] = titles[location.pathname] || ["Product comparison", "Review evidence before deciding."];
  const closeMenu = () => setOpenMenu(null);
  return <header className="topbar">
    <div className="mobile-brand"><Sparkles size={19} /> Duplicate Product Review Queue</div>
    <div className="page-heading"><h1>{title}</h1><p>{subtitle}</p></div>
    <div className="topbar-actions">
      <label className="global-search"><Search size={16} /><input placeholder="Search anything..." aria-label="Search anything" /><kbd>⌘ K</kbd></label>
      <NotificationMenu open={openMenu === "notifications"} onToggle={() => setOpenMenu((current) => current === "notifications" ? null : "notifications")} onClose={closeMenu} />
      <AccountMenu open={openMenu === "account"} onToggle={() => setOpenMenu((current) => current === "account" ? null : "account")} onClose={closeMenu} />
    </div>
  </header>;
}
