"use client";

/**
 * RecruitAI — Dashboard Home
 * Welcome + quick stats + quick actions
 */

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { apiGetResumes, type ResumeListItem } from "@/lib/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGetResumes()
      .then(setResumes)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const primaryResume = resumes.find((r) => r.is_primary);
  const totalSkills = resumes.reduce((sum, r) => sum + r.skills_count, 0);

  const stats = [
    {
      label: "Resumes",
      value: loading ? "—" : resumes.length.toString(),
      icon: "📄",
      color: "var(--color-primary)",
    },
    {
      label: "Skills Found",
      value: loading ? "—" : totalSkills.toString(),
      icon: "⚡",
      color: "var(--color-accent)",
    },
    {
      label: "Primary Resume",
      value: loading ? "—" : primaryResume?.filename || "None",
      icon: "⭐",
      color: "var(--color-warning)",
      truncate: true,
    },
    {
      label: "ATS Score",
      value: "—",
      icon: "🎯",
      color: "var(--color-success)",
      subtext: "Coming soon",
    },
  ];

  return (
    <div>
      {/* ─── Welcome ───────────────────────────────────── */}
      <div style={{ marginBottom: 36 }}>
        <h1
          style={{
            fontSize: 28,
            fontWeight: 700,
            marginBottom: 6,
          }}
        >
          Welcome back,{" "}
          <span className="text-gradient">
            {user?.name?.split(" ")[0] || "there"}
          </span>
          ! 👋
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 15 }}>
          Here&apos;s an overview of your recruitment journey.
        </p>
      </div>

      {/* ─── Stats Grid ────────────────────────────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: 16,
          marginBottom: 40,
        }}
      >
        {stats.map((stat, i) => (
          <div
            key={i}
            className="glass-card animate-fade-in-up"
            style={{
              padding: "22px 24px",
              animationDelay: `${i * 0.08}s`,
              animationFillMode: "both",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: 14,
              }}
            >
              <span style={{ fontSize: 13, color: "var(--text-muted)" }}>
                {stat.label}
              </span>
              <span style={{ fontSize: 22 }}>{stat.icon}</span>
            </div>
            <div
              style={{
                fontSize: stat.truncate ? 14 : 26,
                fontWeight: 700,
                color: stat.color,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {stat.value}
            </div>
            {stat.subtext && (
              <div
                style={{
                  fontSize: 11,
                  color: "var(--text-muted)",
                  marginTop: 4,
                }}
              >
                {stat.subtext}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* ─── Quick Actions ─────────────────────────────── */}
      <h2
        style={{
          fontSize: 18,
          fontWeight: 600,
          marginBottom: 16,
        }}
      >
        Quick Actions
      </h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: 16,
        }}
      >
        <Link
          href="/dashboard/resumes"
          className="glass-card"
          style={{
            padding: 24,
            textDecoration: "none",
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: "var(--radius-lg)",
              background: "rgba(99, 102, 241, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 22,
              flexShrink: 0,
            }}
          >
            📤
          </div>
          <div>
            <div
              style={{
                fontSize: 15,
                fontWeight: 600,
                color: "var(--text-primary)",
                marginBottom: 4,
              }}
            >
              Upload Resume
            </div>
            <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>
              Upload and parse a new resume with AI
            </div>
          </div>
        </Link>

        <div
          className="glass-card"
          style={{
            padding: 24,
            display: "flex",
            alignItems: "center",
            gap: 16,
            opacity: 0.5,
            cursor: "default",
          }}
        >
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: "var(--radius-lg)",
              background: "rgba(6, 182, 212, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 22,
              flexShrink: 0,
            }}
          >
            🎯
          </div>
          <div>
            <div
              style={{
                fontSize: 15,
                fontWeight: 600,
                color: "var(--text-primary)",
                marginBottom: 4,
              }}
            >
              Score Against Job
            </div>
            <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
              Coming in Phase 4
            </div>
          </div>
        </div>

        <div
          className="glass-card"
          style={{
            padding: 24,
            display: "flex",
            alignItems: "center",
            gap: 16,
            opacity: 0.5,
            cursor: "default",
          }}
        >
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: "var(--radius-lg)",
              background: "rgba(16, 185, 129, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 22,
              flexShrink: 0,
            }}
          >
            ✨
          </div>
          <div>
            <div
              style={{
                fontSize: 15,
                fontWeight: 600,
                color: "var(--text-primary)",
                marginBottom: 4,
              }}
            >
              Personalize Resume
            </div>
            <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
              Coming in Phase 5
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
