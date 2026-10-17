import React, { useEffect, useRef } from "react";
import { ChevronDown, LogOut, Settings } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth, initials } from "../auth";

export default function AccountMenu({ open, onToggle, onClose }) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const menuRef = useRef(null);
  const triggerRef = useRef(null);
  const menuId = "account-menu";

  useEffect(() => {
    if (!open) return undefined;
    const onPointerDown = (event) => {
      if (!menuRef.current?.contains(event.target)) onClose();
    };
    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
        triggerRef.current?.focus();
      }
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onClose]);

  useEffect(() => {
    if (open) menuRef.current?.querySelector('[role="menuitem"]')?.focus();
  }, [open]);

  const moveFocus = (event) => {
    const items = [...(menuRef.current?.querySelectorAll('[role="menuitem"]') || [])];
    if (!items.length) return;
    const currentIndex = items.indexOf(document.activeElement);
    let nextIndex = currentIndex;
    if (event.key === "ArrowDown") nextIndex = (currentIndex + 1) % items.length;
    else if (event.key === "ArrowUp") nextIndex = (currentIndex - 1 + items.length) % items.length;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = items.length - 1;
    else return;
    event.preventDefault();
    items[nextIndex]?.focus();
  };

  const logout = () => {
    onClose();
    signOut();
    navigate("/login", { replace: true });
  };

  return <div className="account-menu" ref={menuRef} onKeyDown={moveFocus}>
    <button
      ref={triggerRef}
      className="top-profile"
      type="button"
      aria-label={`Account menu for ${user?.name || "user"}`}
      aria-haspopup="menu"
      aria-expanded={open}
      aria-controls={menuId}
      onClick={onToggle}
      onKeyDown={(event) => {
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
          event.preventDefault();
          onToggle();
        }
      }}
    >
      <span className="avatar">{initials(user?.name)}</span>
      <ChevronDown className={open ? "account-chevron is-open" : "account-chevron"} size={15} aria-hidden="true" />
    </button>
    {open && <div className="account-dropdown" id={menuId} role="menu" aria-label="Account options">
      <div className="account-menu-user">
        <strong>{user?.name || "User"}</strong>
        <span>{user?.email || user?.role || (user?.demo ? "Demo access" : "Catalogue operations")}</span>
      </div>
      <div className="account-menu-options">
        <button className="account-menu-item" type="button" role="menuitem" onClick={() => { onClose(); navigate("/settings"); }}>
          <Settings size={16} aria-hidden="true" /> <span>Account settings</span>
        </button>
        <button className="account-menu-item danger" type="button" role="menuitem" onClick={logout}>
          <LogOut size={16} aria-hidden="true" /> <span>Log out</span>
        </button>
      </div>
    </div>}
  </div>;
}
