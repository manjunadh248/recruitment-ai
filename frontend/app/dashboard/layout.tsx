"use client";

/**
 * RecruitAI — Dashboard Layout
 * Sidebar navigation + top bar with auth guard
 */

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { AuthProvider, useAuth } from "@/lib/auth";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "🏠", exact: true },
  { href: "/dashboard/resumes", label: "Resumes", icon: "📄", exact: false },
  { href: "#", label: "ATS Scoring", icon: "🎯", exact: false, soon: true },
  { href: "#", label: "Job Matching", icon: "🔍", exact: false, soon: true },
  { href: "#", label: "Personalize", icon: "✨", exact: false, soon: true },
];

function DashboardShell({ children }: { children: ReactNode }) {
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !isAuthenticated) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--bg-primary)",
        }}
      >
        <div className="spinner spinner-lg" />
      </div>
    );
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* ─── Sidebar ─────────────────────────────────────── */}
      <aside
        style={{
          width: "var(--sidebar-width)",
          flexShrink: 0,
          background: "var(--bg-secondary)",
          borderRight: "1px solid var(--border-subtle)",
          display: "flex",
          flexDirection: "column",
          position: "fixed",
          top: 0,
          left: 0,
          bottom: 0,
          zIndex: 40,
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: "24px 20px 20px",
            borderBottom: "1px solid var(--border-subtle)",
          }}
        >
          <Link
            href="/dashboard"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              textDecoration: "none",
            }}
          >
            <span style={{ fontSize: 24 }}>🚀</span>
            <span
              style={{ fontSize: 18, fontWeight: 700 }}
              className="text-gradient"
            >
              RecruitAI
            </span>
          </Link>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "16px 12px", display: "flex", flexDirection: "column", gap: 4 }}>
          {navItems.map((item) => {
            const isActive = item.exact
              ? pathname === item.href
              : pathname.startsWith(item.href) && item.href !== "/dashboard";

            return (
              <Link
                key={item.label}
                href={item.soon ? "#" : item.href}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 14px",
                  borderRadius: "var(--radius-md)",
                  fontSize: 14,
                  fontWeight: isActive ? 500 : 400,
                  color: item.soon
                    ? "var(--text-muted)"
                    : isActive
                    ? "var(--text-primary)"
                    : "var(--text-secondary)",
                  background: isActive
                    ? "rgba(99, 102, 241, 0.1)"
                    : "transparent",
                  textDecoration: "none",
                  transition: "all var(--transition-fast)",
                  cursor: item.soon ? "default" : "pointer",
                  opacity: item.soon ? 0.5 : 1,
                }}
              >
                <span style={{ fontSize: 18 }}>{item.icon}</span>
                {item.label}
                {item.soon && (
                  <span
                    style={{
                      marginLeft: "auto",
                      fontSize: 10,
                      padding: "2px 6px",
                      borderRadius: "var(--radius-full)",
                      background: "rgba(255,255,255,0.06)",
                      color: "var(--text-muted)",
                    }}
                  >
                    Soon
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div
          style={{
            padding: "16px 16px",
            borderTop: "1px solid var(--border-subtle)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              marginBottom: 12,
            }}
          >
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: "var(--radius-full)",
                background:
                  "linear-gradient(135deg, var(--color-primary), var(--color-accent))",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 14,
                fontWeight: 600,
                color: "white",
                flexShrink: 0,
              }}
            >
              {user?.name?.charAt(0).toUpperCase() || "U"}
            </div>
            <div style={{ overflow: "hidden" }}>
              <div
                style={{
                  fontSize: 13,
                  fontWeight: 500,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {user?.name}
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--text-muted)",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {user?.email}
              </div>
            </div>
          </div>
          <button
            onClick={logout}
            className="btn btn-ghost btn-sm"
            style={{ width: "100%", fontSize: 13 }}
          >
            Sign Out
          </button>
        </div>
      </aside>

      {/* ─── Main Content ────────────────────────────────── */}
      <main
        style={{
          flex: 1,
          marginLeft: "var(--sidebar-width)",
          padding: "32px 36px",
          minHeight: "100vh",
          background: "var(--bg-primary)",
        }}
      >
        <div className="page-enter">{children}</div>
      </main>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <DashboardShell>{children}</DashboardShell>
    </AuthProvider>
  );
}
