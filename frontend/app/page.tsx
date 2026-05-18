"use client";

/**
 * RecruitAI — Landing Page
 * Premium hero + feature showcase with CTA
 */

import Link from "next/link";
import { useEffect, useState } from "react";

const features = [
  {
    icon: "📄",
    title: "AI Resume Parsing",
    desc: "Upload PDF or DOCX and get instant structured data extraction with NLP-powered analysis.",
  },
  {
    icon: "🎯",
    title: "ATS Scoring",
    desc: "Score your resume against job descriptions. Get keyword gaps, section analysis, and improvement suggestions.",
  },
  {
    icon: "✨",
    title: "Smart Personalization",
    desc: "AI rewrites your resume sections to match specific job requirements while keeping it authentic.",
  },
  {
    icon: "🔍",
    title: "Job Matching",
    desc: "Semantic matching finds the best job opportunities based on your skills and experience profile.",
  },
];

export default function LandingPage() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--bg-primary)",
      }}
    >
      {/* ─── Nav ─────────────────────────────────────────── */}
      <nav
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "20px 40px",
          borderBottom: "1px solid var(--border-subtle)",
          backdropFilter: "blur(12px)",
          position: "sticky",
          top: 0,
          zIndex: 50,
          background: "rgba(10, 10, 15, 0.8)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 24 }}>🚀</span>
          <span
            style={{ fontSize: 20, fontWeight: 700 }}
            className="text-gradient"
          >
            RecruitAI
          </span>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <Link href="/login" className="btn btn-ghost">
            Sign In
          </Link>
          <Link href="/register" className="btn btn-primary">
            Get Started
          </Link>
        </div>
      </nav>

      {/* ─── Hero ────────────────────────────────────────── */}
      <main
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          paddingTop: 100,
        }}
      >
        <div
          className={mounted ? "animate-fade-in-up" : ""}
          style={{
            textAlign: "center",
            maxWidth: 720,
            padding: "0 24px",
            opacity: mounted ? 1 : 0,
          }}
        >
          <div
            className="badge badge-primary"
            style={{ marginBottom: 20, fontSize: 13, padding: "5px 16px" }}
          >
            ✨ AI-Powered Recruitment Platform
          </div>
          <h1
            style={{
              fontSize: "clamp(36px, 5vw, 56px)",
              fontWeight: 800,
              lineHeight: 1.15,
              letterSpacing: "-0.02em",
              marginBottom: 20,
            }}
          >
            Land Your Dream Job with{" "}
            <span className="text-gradient">AI-Optimized</span> Resumes
          </h1>
          <p
            style={{
              fontSize: 18,
              color: "var(--text-secondary)",
              lineHeight: 1.7,
              marginBottom: 36,
              maxWidth: 560,
              marginLeft: "auto",
              marginRight: "auto",
            }}
          >
            Upload your resume, get instant ATS scoring, AI-powered
            personalization, and smart job matching — all in one platform.
          </p>
          <div style={{ display: "flex", gap: 14, justifyContent: "center" }}>
            <Link href="/register" className="btn btn-primary btn-lg">
              🚀 Start Free
            </Link>
            <Link href="/login" className="btn btn-secondary btn-lg">
              Sign In →
            </Link>
          </div>
        </div>

        {/* ─── Features ──────────────────────────────────── */}
        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 20,
            maxWidth: 1080,
            width: "100%",
            padding: "100px 24px 80px",
          }}
        >
          {features.map((f, i) => (
            <div
              key={i}
              className={`glass-card ${mounted ? "animate-fade-in-up" : ""}`}
              style={{
                padding: 28,
                opacity: mounted ? 1 : 0,
                animationDelay: `${i * 0.1}s`,
                animationFillMode: "both",
              }}
            >
              <div style={{ fontSize: 32, marginBottom: 14 }}>{f.icon}</div>
              <h3
                style={{
                  fontSize: 17,
                  fontWeight: 600,
                  marginBottom: 8,
                  color: "var(--text-primary)",
                }}
              >
                {f.title}
              </h3>
              <p
                style={{
                  fontSize: 14,
                  color: "var(--text-secondary)",
                  lineHeight: 1.6,
                }}
              >
                {f.desc}
              </p>
            </div>
          ))}
        </section>

        {/* ─── Footer ────────────────────────────────────── */}
        <footer
          style={{
            padding: "24px 40px",
            borderTop: "1px solid var(--border-subtle)",
            width: "100%",
            textAlign: "center",
            color: "var(--text-muted)",
            fontSize: 13,
          }}
        >
          © 2026 RecruitAI · AI-Powered Recruitment Optimization
        </footer>
      </main>
    </div>
  );
}
