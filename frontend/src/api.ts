import type { Language } from "./copy";
import type { AdminOverview, SourceCheck, Answer, Change, Citation, ComparisonRow, EligibilityQuestion, EligibilityResult, SchemeCard } from "./types";

// Empty in local development (Vite proxies /api); set VITE_API_BASE when the API is on another origin.
export const API = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

export class RateLimitedError extends Error {}

async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(API + path, init);
  if (response.status === 429) throw new RateLimitedError("rate limited");
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return (await response.json()) as T;
}

export type SignInConfig = { url: string; publishable_key: string };
export type Health = { admin_enabled?: boolean; admin_sign_in?: SignInConfig | null };

export const fetchHealth = () => getJson<Health>("/api/health");

export const fetchSources = () => getJson<{ sources?: Citation[] }>("/api/sources").then((data) => data.sources ?? []);

export const fetchSchemes = (language: Language) =>
  getJson<{ schemes?: SchemeCard[] }>(`/api/schemes?language=${language}`).then((data) => data.schemes ?? []);

export const fetchChanges = (language: Language) =>
  getJson<{ changes?: Change[] }>(`/api/changes?language=${language}`).then((data) => data.changes ?? []);

export const askQuestion = (question: string, language: Language) =>
  getJson<Answer>("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, language }),
  });

export const fetchEligibilityQuestions = (language: Language) =>
  getJson<{ questions?: EligibilityQuestion[] }>(`/api/eligibility/questions?language=${language}`).then((data) => data.questions ?? []);

/** Answers are coarse choices; the API evaluates them by rule and stores nothing. */
export const checkEligibility = (profile: Record<string, string>, language: Language, schemeIds: string[] = []) =>
  getJson<{ results: EligibilityResult[]; sources: Citation[] }>("/api/eligibility", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, language, scheme_ids: schemeIds }),
  });

export const compareSchemes = (ids: string[], language: Language) =>
  getJson<{ schemes: ComparisonRow[]; sources: Citation[] }>(`/api/schemes/compare?ids=${ids.map(encodeURIComponent).join(",")}&language=${language}`);

export const fetchAdminOverview = (token: string) =>
  getJson<AdminOverview>("/api/admin/overview", { headers: { Authorization: `Bearer ${token}` } });

export const recordSourceCheck = (token: string, sourceId: string, outcome: string, note: string) =>
  getJson<SourceCheck>(`/api/admin/sources/${encodeURIComponent(sourceId)}/checks`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ outcome, note }),
  });

/**
 * Maintainer sign-in goes straight to Supabase Auth; CivicLens never sees the password. The access
 * token is kept in memory only (not localStorage), so closing the tab signs out of this page.
 */
const authBase = (config: SignInConfig) => config.url.replace(/\/+$/, "");

export async function supabaseSignIn(config: SignInConfig, email: string, password: string): Promise<string> {
  const response = await fetch(`${authBase(config)}/auth/v1/token?grant_type=password`, {
    method: "POST",
    headers: { apikey: config.publishable_key, "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error(`Sign-in failed: ${response.status}`);
  const data = (await response.json()) as { access_token?: string };
  if (!data.access_token) throw new Error("Sign-in failed");
  return data.access_token;
}

export async function supabaseSignOut(config: SignInConfig, token: string): Promise<void> {
  await fetch(`${authBase(config)}/auth/v1/logout`, {
    method: "POST",
    headers: { apikey: config.publishable_key, Authorization: `Bearer ${token}` },
  }).catch(() => undefined);
}
