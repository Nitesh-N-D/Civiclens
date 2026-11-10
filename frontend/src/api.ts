import type { Language } from "./copy";
import type { AdminOverview, Answer, Change, Citation, SchemeCard } from "./types";

// Empty in local development (Vite proxies /api); set VITE_API_BASE when the API is on another origin.
export const API = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

export class RateLimitedError extends Error {}

async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(API + path, init);
  if (response.status === 429) throw new RateLimitedError("rate limited");
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return (await response.json()) as T;
}

export type Health = { admin_enabled?: boolean; admin_sign_in?: boolean };

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

export const fetchAdminOverview = (token: string) =>
  getJson<AdminOverview>("/api/admin/overview", { headers: { Authorization: `Bearer ${token}` } });
