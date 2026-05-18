"use client";

/**
 * RecruitAI — Resume Detail Page
 * Displays full parsed resume data in organized sections
 */

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  apiGetResume,
  apiSetPrimaryResume,
  apiDeleteResume,
  type ResumeDetail,
} from "@/lib/api";

export default function ResumeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const resumeId = params.id as string;

  const [resume, setResume] = useState<ResumeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!resumeId) return;
    apiGetResume(resumeId)
      .then(setResume)
      .catch((err) => setError(err.message || "Failed to load resume"))
      .finally(() => setLoading(false));
  }, [resumeId]);

  const handleSetPrimary = async () => {
    if (!resume) return;
    try {
      await apiSetPrimaryResume(resume.id);
      setResume({ ...resume, is_primary: true });
    } catch {
      alert("Failed to set as primary.");
    }
  };

  const handleDelete = async () => {
    if (!resume) return;
    if (!confirm(`Delete "${resume.filename}"? This cannot be undone.`)) return;
    try {
      await apiDeleteResume(resume.id);
      router.push("/dashboard/resumes");
    } catch {
      alert("Failed to delete resume.");
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "40px 0" }}>
        <div className="skeleton" style={{ height: 28, width: 240, marginBottom: 16 }} />
        <div className="skeleton" style={{ height: 16, width: 180, marginBottom: 40 }} />
        <div style={{ display: "grid", gap: 16 }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton" style={{ height: 120, borderRadius: "var(--radius-lg)" }} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="glass-card-static" style={{ padding: 48, textAlign: "center" }}>
        <div style={{ fontSize: 40, marginBottom: 12 }}>😕</div>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
          {error || "Resume not found"}
        </h2>
        <Link href="/dashboard/resumes" className="btn btn-secondary" style={{ marginTop: 12 }}>
          ← Back to Resumes
        </Link>
      </div>
    );
  }

  const { parsed_data: pd } = resume;

  return (
    <div className="animate-fade-in-up">
      {/* ─── Header ─────────────────────────────────────── */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          marginBottom: 32,
          flexWrap: "wrap",
          gap: 16,
        }}
      >
        <div>
          <Link
            href="/dashboard/resumes"
            style={{
              fontSize: 13,
              color: "var(--text-muted)",
              textDecoration: "none",
              display: "inline-flex",
              alignItems: "center",
              gap: 4,
              marginBottom: 12,
            }}
          >
            ← Back to Resumes
          </Link>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <h1 style={{ fontSize: 24, fontWeight: 700 }}>{resume.filename}</h1>
            {resume.is_primary && <span className="badge badge-success">⭐ Primary</span>}
          </div>
          <div
            style={{
              display: "flex",
              gap: 14,
              marginTop: 8,
              fontSize: 13,
              color: "var(--text-muted)",
            }}
          >
            <span>{resume.file_type.toUpperCase()}</span>
            <span>·</span>
            <span>{resume.skills_count} skills detected</span>
            <span>·</span>
            <span>
              Uploaded{" "}
              {new Date(resume.created_at).toLocaleDateString("en-US", {
                month: "long",
                day: "numeric",
                year: "numeric",
              })}
            </span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {!resume.is_primary && (
            <button onClick={handleSetPrimary} className="btn btn-secondary btn-sm">
              ⭐ Set Primary
            </button>
          )}
          <button onClick={handleDelete} className="btn btn-danger btn-sm">
            Delete
          </button>
        </div>
      </div>

      {/* ─── Content Grid ──────────────────────────────── */}
      <div style={{ display: "grid", gap: 20 }}>
        {/* Contact Info */}
        {pd.contact_info &&
          Object.values(pd.contact_info).some(Boolean) && (
            <Section title="📇 Contact Information">
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
                  gap: 12,
                }}
              >
                {pd.contact_info.email && (
                  <InfoItem label="Email" value={pd.contact_info.email} />
                )}
                {pd.contact_info.phone && (
                  <InfoItem label="Phone" value={pd.contact_info.phone} />
                )}
                {pd.contact_info.location && (
                  <InfoItem label="Location" value={pd.contact_info.location} />
                )}
                {pd.contact_info.linkedin_url && (
                  <InfoItem label="LinkedIn" value={pd.contact_info.linkedin_url} isLink />
                )}
                {pd.contact_info.github_url && (
                  <InfoItem label="GitHub" value={pd.contact_info.github_url} isLink />
                )}
                {pd.contact_info.portfolio_url && (
                  <InfoItem label="Portfolio" value={pd.contact_info.portfolio_url} isLink />
                )}
              </div>
            </Section>
          )}

        {/* Summary */}
        {pd.summary && (
          <Section title="📝 Summary">
            <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-secondary)" }}>
              {pd.summary}
            </p>
          </Section>
        )}

        {/* Skills */}
        {pd.skills.length > 0 && (
          <Section title={`⚡ Skills (${pd.skills.length})`}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {pd.skills.map((skill, i) => {
                const colors = [
                  "badge-primary",
                  "badge-accent",
                  "badge-success",
                  "badge-warning",
                ];
                return (
                  <span key={i} className={`badge ${colors[i % colors.length]}`}>
                    {skill}
                  </span>
                );
              })}
            </div>
          </Section>
        )}

        {/* Experience */}
        {pd.experience.length > 0 && (
          <Section title={`💼 Experience (${pd.experience.length})`}>
            <div style={{ display: "grid", gap: 16 }}>
              {pd.experience.map((exp, i) => (
                <div
                  key={i}
                  style={{
                    padding: 18,
                    borderRadius: "var(--radius-md)",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid var(--border-subtle)",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      flexWrap: "wrap",
                      gap: 8,
                      marginBottom: 8,
                    }}
                  >
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 600 }}>
                        {exp.title || "Unknown Title"}
                      </div>
                      {exp.company && (
                        <div
                          style={{
                            fontSize: 13,
                            color: "var(--color-primary-light)",
                            marginTop: 2,
                          }}
                        >
                          {exp.company}
                          {exp.location && ` · ${exp.location}`}
                        </div>
                      )}
                    </div>
                    {(exp.start_date || exp.end_date) && (
                      <div
                        style={{
                          fontSize: 12,
                          color: "var(--text-muted)",
                          flexShrink: 0,
                        }}
                      >
                        {exp.start_date} — {exp.is_current ? "Present" : exp.end_date}
                      </div>
                    )}
                  </div>
                  {exp.description && (
                    <p
                      style={{
                        fontSize: 13,
                        color: "var(--text-secondary)",
                        lineHeight: 1.6,
                        marginBottom: exp.highlights.length > 0 ? 10 : 0,
                      }}
                    >
                      {exp.description}
                    </p>
                  )}
                  {exp.highlights.length > 0 && (
                    <ul
                      style={{
                        listStyle: "none",
                        padding: 0,
                        display: "grid",
                        gap: 6,
                      }}
                    >
                      {exp.highlights.map((h, j) => (
                        <li
                          key={j}
                          style={{
                            fontSize: 13,
                            color: "var(--text-secondary)",
                            paddingLeft: 16,
                            position: "relative",
                          }}
                        >
                          <span
                            style={{
                              position: "absolute",
                              left: 0,
                              color: "var(--color-primary-light)",
                            }}
                          >
                            •
                          </span>
                          {h}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Education */}
        {pd.education.length > 0 && (
          <Section title={`🎓 Education (${pd.education.length})`}>
            <div style={{ display: "grid", gap: 14 }}>
              {pd.education.map((edu, i) => (
                <div
                  key={i}
                  style={{
                    padding: 18,
                    borderRadius: "var(--radius-md)",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid var(--border-subtle)",
                  }}
                >
                  <div style={{ fontSize: 15, fontWeight: 600 }}>
                    {edu.institution || "Unknown Institution"}
                  </div>
                  {edu.degree && (
                    <div
                      style={{
                        fontSize: 13,
                        color: "var(--color-accent-light)",
                        marginTop: 2,
                      }}
                    >
                      {edu.degree}
                      {edu.field_of_study && ` in ${edu.field_of_study}`}
                    </div>
                  )}
                  <div
                    style={{
                      display: "flex",
                      gap: 12,
                      marginTop: 6,
                      fontSize: 12,
                      color: "var(--text-muted)",
                    }}
                  >
                    {(edu.start_date || edu.end_date) && (
                      <span>
                        {edu.start_date} — {edu.end_date}
                      </span>
                    )}
                    {edu.gpa && <span>GPA: {edu.gpa}</span>}
                  </div>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Projects */}
        {pd.projects.length > 0 && (
          <Section title={`🛠️ Projects (${pd.projects.length})`}>
            <div style={{ display: "grid", gap: 14 }}>
              {pd.projects.map((proj, i) => (
                <div
                  key={i}
                  style={{
                    padding: 18,
                    borderRadius: "var(--radius-md)",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid var(--border-subtle)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ fontSize: 15, fontWeight: 600 }}>{proj.name}</div>
                    {proj.url && (
                      <a
                        href={proj.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ fontSize: 12, color: "var(--color-primary-light)" }}
                      >
                        🔗 Link
                      </a>
                    )}
                  </div>
                  {proj.description && (
                    <p
                      style={{
                        fontSize: 13,
                        color: "var(--text-secondary)",
                        lineHeight: 1.6,
                        marginTop: 6,
                      }}
                    >
                      {proj.description}
                    </p>
                  )}
                  {proj.technologies.length > 0 && (
                    <div
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: 6,
                        marginTop: 10,
                      }}
                    >
                      {proj.technologies.map((tech, j) => (
                        <span
                          key={j}
                          style={{
                            fontSize: 11,
                            padding: "2px 8px",
                            borderRadius: "var(--radius-full)",
                            background: "rgba(99,102,241,0.1)",
                            color: "var(--color-primary-light)",
                          }}
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                  {proj.highlights.length > 0 && (
                    <ul style={{ listStyle: "none", padding: 0, marginTop: 10 }}>
                      {proj.highlights.map((h, j) => (
                        <li
                          key={j}
                          style={{
                            fontSize: 13,
                            color: "var(--text-secondary)",
                            paddingLeft: 16,
                            position: "relative",
                            marginBottom: 4,
                          }}
                        >
                          <span
                            style={{
                              position: "absolute",
                              left: 0,
                              color: "var(--color-accent-light)",
                            }}
                          >
                            •
                          </span>
                          {h}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Certifications */}
        {pd.certifications.length > 0 && (
          <Section title={`🏆 Certifications (${pd.certifications.length})`}>
            <div style={{ display: "grid", gap: 10 }}>
              {pd.certifications.map((cert, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 16px",
                    borderRadius: "var(--radius-md)",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid var(--border-subtle)",
                  }}
                >
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 500 }}>
                      {cert.name}
                    </div>
                    {cert.issuer && (
                      <div
                        style={{
                          fontSize: 12,
                          color: "var(--text-muted)",
                          marginTop: 2,
                        }}
                      >
                        {cert.issuer}
                      </div>
                    )}
                  </div>
                  {cert.date && (
                    <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                      {cert.date}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Languages */}
        {pd.languages.length > 0 && (
          <Section title="🌍 Languages">
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {pd.languages.map((lang, i) => (
                <span key={i} className="badge badge-accent">
                  {lang}
                </span>
              ))}
            </div>
          </Section>
        )}

        {/* Experience Summary */}
        {pd.total_experience_years && (
          <div
            className="glass-card-static"
            style={{
              padding: "18px 24px",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <span style={{ fontSize: 22 }}>📊</span>
            <span style={{ fontSize: 14, color: "var(--text-secondary)" }}>
              Estimated total experience:{" "}
              <strong style={{ color: "var(--color-primary-light)" }}>
                {pd.total_experience_years} years
              </strong>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Helper Components ──────────────────────────────────

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="glass-card-static" style={{ padding: 24 }}>
      <h2
        style={{
          fontSize: 16,
          fontWeight: 600,
          marginBottom: 18,
          paddingBottom: 12,
          borderBottom: "1px solid var(--border-subtle)",
        }}
      >
        {title}
      </h2>
      {children}
    </div>
  );
}

function InfoItem({
  label,
  value,
  isLink = false,
}: {
  label: string;
  value: string;
  isLink?: boolean;
}) {
  return (
    <div>
      <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 3 }}>
        {label}
      </div>
      {isLink ? (
        <a
          href={value.startsWith("http") ? value : `https://${value}`}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontSize: 13,
            color: "var(--color-primary-light)",
            textDecoration: "none",
            wordBreak: "break-all",
          }}
        >
          {value}
        </a>
      ) : (
        <div style={{ fontSize: 13, wordBreak: "break-all" }}>{value}</div>
      )}
    </div>
  );
}
