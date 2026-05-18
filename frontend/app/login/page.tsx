"use client";

/**
 * RecruitAI — Login Page
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthProvider, useAuth } from "@/lib/auth";
import { APIError } from "@/lib/api";

function LoginForm() {
  const router = useRouter();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated) {
    router.push("/dashboard");
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
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
          "radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.08) 0%, var(--bg-primary) 60%)",
      }}
    >
      <div
        className="glass-card-static animate-fade-in-up"
        style={{ width: "100%", maxWidth: 420, padding: 36 }}
      >
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>🚀</div>
          <h1
            style={{ fontSize: 24, fontWeight: 700, marginBottom: 6 }}
            className="text-gradient"
          >
            Welcome Back
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
            Sign in to your RecruitAI account
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
            <label className="input-label" htmlFor="login-email">
              Email
            </label>
            <input
              id="login-email"
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
            <label className="input-label" htmlFor="login-password">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              className="input"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              autoComplete="current-password"
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
                <span className="spinner" /> Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        {/* Register link */}
        <p
          style={{
            marginTop: 24,
            textAlign: "center",
            fontSize: 14,
            color: "var(--text-secondary)",
          }}
        >
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            style={{ color: "var(--color-primary-light)", fontWeight: 500 }}
          >
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <AuthProvider>
      <LoginForm />
    </AuthProvider>
  );
}
