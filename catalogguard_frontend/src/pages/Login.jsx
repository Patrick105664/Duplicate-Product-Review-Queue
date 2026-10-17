import React, { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { useAuth } from "../auth";
import AuthLayout, { GoogleIcon } from "../components/AuthLayout";

export default function Login() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const from = useLocation().state?.from || "/dashboard";
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [errors, setErrors] = useState({});

  if (user) return <Navigate to="/dashboard" replace />;

  const submit = (e) => {
    e.preventDefault();
    const next = {};
    if (!name.trim()) next.name = "Enter your name.";
    if (!password) next.password = "Enter your password.";
    setErrors(next);
    if (Object.keys(next).length) return;
    signIn({ name: name.trim(), demo: true });
    navigate(from, { replace: true });
  };

  // Placeholder: real Google sign-in needs an OAuth client ID and a backend.
  const google = () => { signIn({ name: "Google Demo User", provider: "google", demo: true }); navigate(from, { replace: true }); };

  return (
    <AuthLayout title="Welcome back" subtitle="Login to continue reviewing suggested duplicate products."
      footer={<>Don’t have an account? <Link to="/register">Register</Link></>}>
      <button type="button" className="google-btn" onClick={google}><GoogleIcon /> Continue with Google</button>
      <div className="auth-divider"><span>or</span></div>
      <form onSubmit={submit} noValidate>
        <label className="auth-field">Name
          <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" aria-invalid={!!errors.name} placeholder="Your full name" />
          {errors.name && <span className="auth-error">{errors.name}</span>}
        </label>
        <label className="auth-field">Password
          <div className="auth-pw">
            <input type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" aria-invalid={!!errors.password} placeholder="Your password" />
            <button type="button" aria-label={show ? "Hide password" : "Show password"} onClick={() => setShow(!show)}>{show ? <EyeOff size={16} /> : <Eye size={16} />}</button>
          </div>
          {errors.password && <span className="auth-error">{errors.password}</span>}
        </label>
        <button type="submit" className="auth-submit">Login</button>
      </form>
    </AuthLayout>
  );
}
