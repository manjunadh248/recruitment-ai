"use client";

/**
 * RecruitAI — Resume Management Page
 * Upload zone + resume list with actions
 */

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  apiUploadResume,
  apiGetResumes,
  apiDeleteResume,
  apiSetPrimaryResume,
  APIError,
  type ResumeListItem,
} from "@/lib/api";

export default function ResumesPage() {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchResumes = useCallback(async () => {
    try {
      const data = await apiGetResumes();
      setResumes(data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResumes();
  }, [fetchResumes]);

  const handleUpload = async (file: File) => {
    setUploadError("");
    setUploadSuccess("");
    setUploading(true);

    try {
      const result = await apiUploadResume(file);
      setUploadSuccess(
        `"${result.filename}" uploaded and parsed — ${result.skills_count} skills detected!`
      );
      await fetchResumes();
    } catch (err) {
      if (err instanceof APIError) {
        setUploadError(err.message);
      } else {
        setUploadError("Upload failed. Please try again.");
      }
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    e.target.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleUpload(file);
  };

  const handleDelete = async (id: string, filename: string) => {
    if (!confirm(`Delete "${filename}"? This cannot be undone.`)) return;
    try {
      await apiDeleteResume(id);
      await fetchResumes();
    } catch {
      alert("Failed to delete resume.");
    }
  };

  const handleSetPrimary = async (id: string) => {
    try {
      await apiSetPrimaryResume(id);
      await fetchResumes();
    } catch {
      alert("Failed to set as primary.");
    }
  };

  return (
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 28,
        }}
      >
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>
            My Resumes
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
            Upload and manage your resumes. AI will parse them automatically.
          </p>
        </div>
      </div>

      {/* ─── Upload Zone ───────────────────────────────── */}
      <div
        className={`upload-zone ${dragOver ? "drag-over" : ""}`}
        onClick={() => !uploading && fileInputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{ marginBottom: 28 }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileSelect}
          style={{ display: "none" }}
        />

        {uploading ? (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 14,
            }}
          >
            <div className="spinner spinner-lg" />
            <p style={{ color: "var(--text-secondary)", fontSize: 15 }}>
              Uploading & parsing with AI...
            </p>
          </div>
        ) : (
          <>
            <div
              style={{
                fontSize: 44,
                marginBottom: 12,
                lineHeight: 1,
              }}
            >
              📄
            </div>
            <p
              style={{
                fontSize: 16,
                fontWeight: 500,
                marginBottom: 6,
                color: "var(--text-primary)",
              }}
            >
              Drag & drop your resume here
            </p>
            <p style={{ color: "var(--text-muted)", fontSize: 13 }}>
              or click to browse · PDF, DOCX · Max 10MB
            </p>
          </>
        )}
      </div>

      {/* ─── Messages ──────────────────────────────────── */}
      {uploadError && (
        <div
          style={{
            padding: "12px 16px",
            borderRadius: "var(--radius-md)",
            background: "rgba(239, 68, 68, 0.08)",
            border: "1px solid rgba(239, 68, 68, 0.2)",
            color: "var(--color-danger)",
            fontSize: 13,
            marginBottom: 20,
          }}
        >
          ❌ {uploadError}
        </div>
      )}

      {uploadSuccess && (
        <div
          style={{
            padding: "12px 16px",
            borderRadius: "var(--radius-md)",
            background: "rgba(16, 185, 129, 0.08)",
            border: "1px solid rgba(16, 185, 129, 0.2)",
            color: "var(--color-success)",
            fontSize: 13,
            marginBottom: 20,
          }}
        >
          ✅ {uploadSuccess}
        </div>
      )}

      {/* ─── Resume List ───────────────────────────────── */}
      {loading ? (
        <div
          style={{
            display: "grid",
            gap: 14,
          }}
        >
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="skeleton"
              style={{ height: 80, borderRadius: "var(--radius-lg)" }}
            />
          ))}
        </div>
      ) : resumes.length === 0 ? (
        <div
          className="glass-card-static"
          style={{
            padding: "48px 24px",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: 40, marginBottom: 12 }}>📭</div>
          <p
            style={{
              fontSize: 16,
              fontWeight: 500,
              marginBottom: 6,
            }}
          >
            No resumes yet
          </p>
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: 13,
            }}
          >
            Upload your first resume to get started
          </p>
        </div>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {resumes.map((resume, i) => (
            <div
              key={resume.id}
              className="glass-card animate-fade-in-up"
              style={{
                padding: "18px 22px",
                display: "flex",
                alignItems: "center",
                gap: 16,
                animationDelay: `${i * 0.05}s`,
                animationFillMode: "both",
              }}
            >
              {/* Icon */}
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: "var(--radius-md)",
                  background:
                    resume.file_type === "pdf"
                      ? "rgba(239, 68, 68, 0.1)"
                      : "rgba(59, 130, 246, 0.1)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 20,
                  flexShrink: 0,
                }}
              >
                {resume.file_type === "pdf" ? "📕" : "📘"}
              </div>

              {/* Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Link
                    href={`/dashboard/resumes/${resume.id}`}
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: "var(--text-primary)",
                      textDecoration: "none",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {resume.filename}
                  </Link>
                  {resume.is_primary && (
                    <span className="badge badge-success">⭐ Primary</span>
                  )}
                </div>
                <div
                  style={{
                    display: "flex",
                    gap: 14,
                    marginTop: 4,
                    fontSize: 12,
                    color: "var(--text-muted)",
                  }}
                >
                  <span>{resume.file_type.toUpperCase()}</span>
                  <span>·</span>
                  <span>{resume.skills_count} skills</span>
                  <span>·</span>
                  <span>
                    {new Date(resume.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                <Link
                  href={`/dashboard/resumes/${resume.id}`}
                  className="btn btn-ghost btn-sm"
                >
                  View
                </Link>
                {!resume.is_primary && (
                  <button
                    onClick={() => handleSetPrimary(resume.id)}
                    className="btn btn-secondary btn-sm"
                  >
                    Set Primary
                  </button>
                )}
                <button
                  onClick={() => handleDelete(resume.id, resume.filename)}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
