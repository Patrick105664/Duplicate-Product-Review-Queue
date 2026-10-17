import React, { useState } from "react";
import { useAuth } from "../auth";

export default function Settings() {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const save = (event) => {
    event.preventDefault();
    const nextName = name.trim();
    if (!nextName) {
      setError("Enter a display name.");
      setMessage("");
      return;
    }
    updateUser({ name: nextName });
    setName(nextName);
    setError("");
    setMessage("Your display name has been updated.");
  };

  return <div className="page-content">
    <div className="page-toolbar"><div><div className="overline">YOUR PROFILE</div><h2>Account settings</h2><p>Update the name shown throughout your workspace.</p></div></div>
    <section className="panel settings-panel">
      <div className="panel-heading"><div><h3>Profile information</h3><p>Your account email is read-only.</p></div></div>
      <form className="settings-form" onSubmit={save}>
        <label className="auth-field">Display name
          <input value={name} onChange={(event) => { setName(event.target.value); setError(""); setMessage(""); }} autoComplete="name" aria-invalid={!!error} />
          {error && <span className="auth-error">{error}</span>}
        </label>
        <label className="auth-field">Email
          <input value={user?.email || "No email provided"} readOnly />
        </label>
        {message && <p className="settings-message" role="status">{message}</p>}
        <button className="button button-primary" type="submit">Save</button>
      </form>
    </section>
  </div>;
}
