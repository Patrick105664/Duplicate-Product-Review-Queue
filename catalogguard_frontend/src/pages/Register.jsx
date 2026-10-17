import React, { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { useAuth } from "../auth";
import AuthLayout from "../components/AuthLayout";
import AuthBackground from "../components/AuthBackground";

const emailRx = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Register() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const [f, setF] = useState({ name: "", email: "", password: "", confirm: "" });
  const [show, setShow] = useState(false);
  const [errors, setErrors] = useState({});
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  if (user) return <Navigate to="/dashboard" replace />;

  const submit = (e) => {
    e.preventDefault();
    const next = {};
    if (!f.name.trim()) next.name = "Enter your name.";
    if (!emailRx.test(f.email)) next.email = "Enter a valid work email.";
    if (f.password.length < 8) next.password = "Use at least 8 characters.";
    if (f.confirm !== f.password) next.confirm = "Passwords do not match.";
    setErrors(next);
    if (Object.keys(next).length) return;
    signIn({ name: f.name.trim(), email: f.email, demo: true });
    navigate("/dashboard", { replace: true });
  };

  const field = (k, label, props = {}) => (
    <label className="auth-field">{label}
      <input value={f[k]} onChange={set(k)} aria-invalid={!!errors[k]} {...props} />
      {errors[k] && <span className="auth-error">{errors[k]}</span>}
    </label>
  );

  return (
    <>
      <AuthBackground />
      <AuthLayout title="Create your account" subtitle="Register to start reviewing suggested duplicate products."
        footer={<>Already have an account? <Link to="/login">Login</Link></>}>
        <form onSubmit={submit} noValidate>
          {field("name", "Name", { autoComplete: "name", placeholder: "Your full name" })}
          {field("email", "Work email", { type: "email", autoComplete: "email", placeholder: "you@company.com" })}
          <label className="auth-field">Password
            <div className="auth-pw">
              <input type={show ? "text" : "password"} value={f.password} onChange={set("password")} autoComplete="new-password" aria-invalid={!!errors.password} placeholder="At least 8 characters" />
              <button type="button" aria-label={show ? "Hide password" : "Show password"} onClick={() => setShow(!show)}>{show ? <EyeOff size={16} /> : <Eye size={16} />}</button>
            </div>
            {errors.password && <span className="auth-error">{errors.password}</span>}
          </label>
          {field("confirm", "Confirm password", { type: show ? "text" : "password", autoComplete: "new-password", placeholder: "Re-enter your password" })}
          <button type="submit" className="auth-submit">Register</button>
        </form>
      </AuthLayout>
    </>
  );
}
