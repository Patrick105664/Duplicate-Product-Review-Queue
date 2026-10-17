import React from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import ReviewQueue from "./pages/ReviewQueue";
import ProductComparison from "./pages/ProductComparison";
import Catalogue from "./pages/Catalogue";
import ScanHistory from "./pages/ScanHistory";
import Evaluation from "./pages/Evaluation";
import Exports from "./pages/Exports";
import Welcome from "./pages/Welcome";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Settings from "./pages/Settings";

function Workspace() {
  const { user } = useAuth();
  const location = useLocation();
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <div className="app-shell"><Sidebar /><div className="main-shell"><Header /><main className="main-content"><Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/queue" element={<ReviewQueue />} />
    <Route path="/compare/:pairId" element={<ProductComparison />} />
    <Route path="/catalogue" element={<Catalogue />} />
    <Route path="/scans" element={<ScanHistory />} />
    <Route path="/scan-history" element={<ScanHistory />} />
    <Route path="/evaluation" element={<Evaluation />} />
    <Route path="/exports" element={<Exports />} />
    <Route path="/settings" element={<Settings />} />
    <Route path="*" element={<Navigate to="/dashboard" replace />} />
  </Routes></main></div></div>;
}

export default function App() {
  return <AuthProvider><Routes>
    <Route path="/" element={<Welcome />} />
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    <Route path="/*" element={<Workspace />} />
  </Routes></AuthProvider>;
}
