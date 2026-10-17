import React, { createContext, useContext, useState } from "react";

// DEMO AUTH: the signed-in user is kept in this browser only (localStorage).
// There is no server, so nothing here is secure authentication.
const AuthContext = createContext(null);
const KEY = "dprq_user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch { return null; }
  });
  const signIn = (u) => { localStorage.setItem(KEY, JSON.stringify(u)); setUser(u); };
  const signOut = () => { localStorage.removeItem(KEY); setUser(null); };
  const updateUser = (updates) => {
    if (!user) return;
    const updatedUser = { ...user, ...updates };
    localStorage.setItem(KEY, JSON.stringify(updatedUser));
    setUser(updatedUser);
  };
  return <AuthContext.Provider value={{ user, signIn, signOut, updateUser }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
export const initials = (name = "") =>
  name.trim().split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase()).join("") || "U";
