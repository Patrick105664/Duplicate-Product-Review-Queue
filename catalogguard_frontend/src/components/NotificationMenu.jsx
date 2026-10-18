import React, { useEffect, useRef } from "react";
import { Bell, CircleAlert, GitCompare, Package, ScanSearch, Sparkles, Check } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useNotifications } from "../hooks/useNotifications";

const notificationIcons = {
  review: GitCompare,
  match: Sparkles,
  pack: Package,
  scan: ScanSearch,
  cost: CircleAlert
};

export default function NotificationMenu({ open, onToggle, onClose }) {
  const { notifications, unreadCount, loading, error, markRead, markAllAsRead } = useNotifications();
  const menuRef = useRef(null);
  const triggerRef = useRef(null);
  const navigate = useNavigate();
  const menuId = "notification-center";
  const unreadLabel = unreadCount > 9 ? "9+" : String(unreadCount);

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
    if (open) menuRef.current?.querySelector(".notification-item")?.focus();
  }, [open]);

  const moveFocus = (event) => {
    const items = [...(menuRef.current?.querySelectorAll(".notification-item") || [])];
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

  const openNotification = (notification) => {
    markRead(notification.id);
    onClose();
    navigate(notification.href);
  };

  return <div className="notification-menu" ref={menuRef} onKeyDown={moveFocus}>
    <button
      ref={triggerRef}
      className="icon-button notification-trigger"
      type="button"
      aria-label={unreadCount ? `Notifications, ${unreadCount} unread` : "Notifications, no unread notifications"}
      aria-haspopup="dialog"
      aria-expanded={open}
      aria-controls={menuId}
      onClick={onToggle}
    >
      <Bell size={18} aria-hidden="true" />
      {unreadCount > 0 && <span className="notification-count" aria-hidden="true">{unreadLabel}</span>}
    </button>
    {open && <section className="notification-panel" id={menuId} role="dialog" aria-label="Notifications">
      <div className="notification-panel-header">
        <div><h2>Notifications</h2><span>{unreadCount} unread</span></div>
        {unreadCount > 0 && <button type="button" className="notification-mark-all" onClick={markAllAsRead}>Mark all as read</button>}
      </div>
      {error && <p className="notification-error" role="status">{error}</p>}
      {loading ? <div className="notification-empty" role="status">Loading notifications…</div>
        : notifications.length === 0 ? <div className="notification-empty"><span className="notification-empty-icon"><Check size={17} /></span><strong>You&apos;re all caught up</strong></div>
          : <div className="notification-list">
            {notifications.map((notification) => {
              const Icon = notificationIcons[notification.icon] || Bell;
              return <button
                className={`notification-item ${notification.unread ? "is-unread" : "is-read"}`}
                type="button"
                key={notification.id}
                onClick={() => openNotification(notification)}
              >
                <span className="notification-icon"><Icon size={16} aria-hidden="true" /></span>
                <span className="notification-copy">
                  <span className="notification-title">{notification.title}</span>
                  <span className="notification-description">{notification.description}</span>
                  <span className="notification-time">{notification.time}</span>
                </span>
                {notification.unread && <span className="notification-unread-dot" aria-label="Unread" />}
              </button>;
            })}
          </div>}
      <div className="notification-panel-footer">
        <Link to="/queue" onClick={onClose}>View review queue <GitCompare size={14} aria-hidden="true" /></Link>
      </div>
    </section>}
  </div>;
}
