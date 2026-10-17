import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Activity, Box, ChartNoAxesCombined, FileDown, GitCompare, LayoutDashboard, LogOut, Package, ScanSearch, ShieldCheck } from "lucide-react";
import { NAV_ITEMS } from "../utils/constants";
import { useAuth, initials } from "../auth";

const icons = {
  "layout-dashboard": LayoutDashboard, "git-compare": GitCompare, package: Package,
  "scan-search": ScanSearch, "chart-no-axes-combined": ChartNoAxesCombined, "file-down": FileDown
};

export default function Sidebar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  return <aside className="sidebar">
    <div className="brand"><div className="brand-mark"><ShieldCheck size={21} /></div><div><strong>Duplicate Product Review Queue</strong></div></div>
    <div className="workspace-label">WORKSPACE</div>
    <nav className="nav-list">
      {NAV_ITEMS.map((item) => {
        const Icon = icons[item.icon] || Box;
        return <NavLink key={item.path} to={item.path} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
          <Icon size={18} strokeWidth={1.8} /><span>{item.label}</span>{item.count && <b className="nav-count">{item.count}</b>}
        </NavLink>;
      })}
    </nav>
    <div className="sidebar-bottom">
      <div className="sidebar-tip"><div className="tip-icon"><Activity size={17} /></div><strong>Review with confidence</strong><p>Every suggested match gets a human decision before any catalogue action.</p></div>
      <div className="profile-mini"><div className="avatar">{initials(user?.name)}</div><div><strong>{user?.name}</strong><small>{user?.demo ? "Demo access" : "Catalogue operations"}</small></div>
        <button className="icon-button plain logout-btn" aria-label="Logout" title="Logout" onClick={() => { signOut(); navigate("/"); }}><LogOut size={16} /></button></div>
    </div>
  </aside>;
}
