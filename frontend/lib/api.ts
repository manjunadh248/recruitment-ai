/**
 * ═══════════════════════════════════════════════════════════
 * RecruitAI — API Client
 * ═══════════════════════════════════════════════════════════
 * Centralized API utility for communicating with the FastAPI
 * backend. Handles auth tokens, error formatting, and
 * provides typed methods for each endpoint.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ─── Types ───────────────────────────────────────────────

export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
  timestamp: string;
}

export interface UserData {
  id: string;
  email: string;
  name: string;
  phone?: string;
  location?: string;
  headline?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  target_roles: string[];
  experience_years?: number;
  created_at: string;
  updated_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserData;
}

export interface ResumeListItem {
  id: string;
  filename: string;
  file_type: string;
  skills_count: number;
  is_primary: boolean;
  created_at: string;
}

export interface ContactInfo {
  email?: string;
  phone?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  location?: string;
}

export interface Education {
  institution: string;
  degree: string;
  field_of_study: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  description?: string;
}

export interface Experience {
  company: string;
  title: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  highlights: string[];
}

export interface Project {
  name: string;
  description?: string;
  technologies: string[];
  url?: string;
  highlights: string[];
}

export interface Certification {
  name: string;
  issuer?: string;
  date?: string;
  url?: string;
}

export interface ParsedResumeData {
  contact_info: ContactInfo;
  summary?: string;
  skills: string[];
  education: Education[];
  experience: Experience[];
  projects: Project[];
  certifications: Certification[];
  languages: string[];
  total_experience_years?: number;
}

export interface ResumeDetail {
  id: string;
  user_id: string;
  filename: string;
  file_type: string;
  parsed_data: ParsedResumeData;
  skills_count: number;
  is_primary: boolean;
  created_at: string;
}

// ─── Token Management ────────────────────────────────────

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("recruitai_access_token");
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("recruitai_refresh_token");
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem("recruitai_access_token", access);
  localStorage.setItem("recruitai_refresh_token", refresh);
}

export function clearTokens() {
  localStorage.removeItem("recruitai_access_token");
  localStorage.removeItem("recruitai_refresh_token");
  localStorage.removeItem("recruitai_user");
}

export function getStoredUser(): UserData | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("recruitai_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredUser(user: UserData) {
  localStorage.setItem("recruitai_user", JSON.stringify(user));
}

// ─── Core Fetch ──────────────────────────────────────────

export class APIError extends Error {
  status: number;
  errorCode: string;

  constructor(message: string, status: number, errorCode: string = "UNKNOWN") {
    super(message);
    this.status = status;
    this.errorCode = errorCode;
    this.name = "APIError";
  }
}

async function fetchAPI<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<APIResponse<T>> {
  const url = `${API_BASE}${endpoint}`;
  const token = getAccessToken();

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new APIError(
      data.message || "Something went wrong",
      response.status,
      data.error_code
    );
  }

  return data as APIResponse<T>;
}

// ─── Auth Endpoints ──────────────────────────────────────

export async function apiRegister(
  name: string,
  email: string,
  password: string
): Promise<AuthTokens> {
  const res = await fetchAPI<AuthTokens>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
  return res.data;
}

export async function apiLogin(
  email: string,
  password: string
): Promise<AuthTokens> {
  const res = await fetchAPI<AuthTokens>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return res.data;
}

export async function apiGetProfile(): Promise<UserData> {
  const res = await fetchAPI<UserData>("/auth/me");
  return res.data;
}

// ─── Resume Endpoints ────────────────────────────────────

export async function apiUploadResume(file: File): Promise<ResumeDetail> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetchAPI<ResumeDetail>("/resume/upload", {
    method: "POST",
    body: formData,
  });
  return res.data;
}

export async function apiGetResumes(): Promise<ResumeListItem[]> {
  const res = await fetchAPI<ResumeListItem[]>("/resume/");
  return res.data;
}

export async function apiGetResume(id: string): Promise<ResumeDetail> {
  const res = await fetchAPI<ResumeDetail>(`/resume/${id}`);
  return res.data;
}

export async function apiDeleteResume(id: string): Promise<void> {
  await fetchAPI(`/resume/${id}`, { method: "DELETE" });
}

export async function apiSetPrimaryResume(id: string): Promise<void> {
  await fetchAPI(`/resume/${id}/primary`, { method: "PATCH" });
}
