"use client";

/**
 * RecruitAI — Register Page
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthProvider, useAuth } from "@/lib/auth";
import { APIError } from "@/lib/api";

function RegisterForm() {
  const router = useRouter();
  const { register, isAuthenticated } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    router.push("/dashboard");
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await register(name, email, password);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
        background:
          "radial-gradient(ellipse at 50% 0%, rgba(6,182,212,0.06) 0%, var(--bg-primary) 60%)",
      }}
    >
      <div
        className="glass-card-static animate-fade-in-up"
        style={{ width: "100%", maxWidth: 420, padding: 36 }}
      >
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>✨</div>
          <h1
            style={{ fontSize: 24, fontWeight: 700, marginBottom: 6 }}
            className="text-gradient"
          >
            Create Account
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
            Start optimizing your job search with AI
          </p>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              padding: "10px 14px",
              borderRadius: "var(--radius-md)",
              background: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.2)",
              color: "var(--color-danger)",
              fontSize: 13,
              marginBottom: 20,
            }}
          >
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 18 }}>
            <label className="input-label" htmlFor="reg-name">
              Full Name
            </label>
            <input
              id="reg-name"
              type="text"
              className="input"
              placeholder="John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              minLength={2}
              autoComplete="name"
            />
          </div>

          <div style={{ marginBottom: 18 }}>
            <label className="input-label" htmlFor="reg-email">
              Email
            </label>
            <input
              id="reg-email"
              type="email"
              className="input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div style={{ marginBottom: 24 }}>
            <label className="input-label" htmlFor="reg-password">
              Password
            </label>
            <input
              id="reg-password"
              type="password"
              className="input"
              placeholder="Minimum 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              autoComplete="new-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: "100%", padding: "12px 20px", fontSize: 15 }}
          >
            {loading ? (
              <>
                <span className="spinner" /> Creating account...
              </>
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        {/* Login link */}
        <p
          style={{
            marginTop: 24,
            textAlign: "center",
            fontSize: 14,
            color: "var(--text-secondary)",
          }}
        >
          Already have an account?{" "}
          <Link
            href="/login"
            style={{ color: "var(--color-primary-light)", fontWeight: 500 }}
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <AuthProvider>
      <RegisterForm />
    </AuthProvider>
  );
}
