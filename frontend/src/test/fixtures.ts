import { vi } from "vitest";
import type { Answer, SchemeCard } from "../types";

export const scheme = (overrides: Partial<SchemeCard> = {}): SchemeCard => ({
  id: "pension", title: "Old Age Pension", department: "Revenue Department", category: "Social welfare",
  overview: "Monthly pension for older people.", url: "https://example.gov.in/pension", source_id: "s1",
  status: "directory", eligibility_enabled: false, ...overrides,
});

export const answer: Answer = {
  text: "The pension is Rs 1,200 a month.",
  mode: "ai",
  citations: [{ id: "s1", title: "CRA pensions", url: "https://example.gov.in/cra", owner: "Revenue Department", status: "Official page", desk_checked_at: "2026-11-10" }],
};

type Route = { status?: number; body: unknown };

/** Replace fetch with a router keyed by path prefix; unmatched paths fail like a down API. */
export function mockApi(routes: Record<string, Route | (() => Route)>) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, _init?: RequestInit) => {
    const url = String(input);
    const key = Object.keys(routes).find((prefix) => url.startsWith(prefix));
    if (!key) return new Response("{}", { status: 503 });
    const route = routes[key];
    const { status = 200, body } = typeof route === "function" ? route() : route;
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

export const baseRoutes = {
  "/api/health": { body: { admin_enabled: false } },
  "/api/sources": { body: { sources: answer.citations } },
  "/api/schemes": { body: { schemes: [scheme(), scheme({ id: "edu", title: "Free Education Scheme", category: "Education", overview: "Fee waiver for students." })] } },
  "/api/changes": { body: { changes: [] } },
};
