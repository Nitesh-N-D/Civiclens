import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AdminPanel } from "../components/AdminPanel";
import { copy } from "../copy";
import { answer, mockApi } from "./fixtures";

const signIn = { url: "https://demo.supabase.co", publishable_key: "sb_publishable_demo" };
const overview = (mutations: boolean) => ({
  sources: answer.citations,
  source_count: 1,
  human_verified_count: 0,
  review_pending_count: 1,
  provider: { configured: false, configured_keys: 0, last_request_succeeded: null, last_failure_category: null, model: null },
  monitoring: "manual_checks",
  mutations_enabled: mutations,
  you: { email: "reviewer@example.org", role: "reviewer", via: "supabase" },
  recent_checks: [],
  recent_audit: [],
});

async function signInAs(mutations: boolean) {
  const fetchMock = mockApi({
    "https://demo.supabase.co/auth/v1/token": { body: { access_token: "jwt-123" } },
    "https://demo.supabase.co/auth/v1/logout": { status: 204, body: {} },
    "/api/admin/overview": { body: overview(mutations) },
    "/api/admin/sources/": { status: 201, body: { id: 1, source_id: "s1", outcome: "changed", checked_at: "2026-11-10T10:00:00+00:00" } },
  });
  const user = userEvent.setup();
  render(<AdminPanel t={copy.en} signIn={signIn} />);
  await user.click(screen.getByRole("button", { name: /Maintainer overview/ }));
  await user.type(screen.getByLabelText("Email"), "reviewer@example.org");
  await user.type(screen.getByLabelText("Password"), "correct horse");
  await user.click(screen.getByRole("button", { name: "Sign in" }));
  return { user, fetchMock };
}

describe("AdminPanel with Supabase sign-in", () => {
  it("sends the password only to Supabase and the token only as a bearer header", async () => {
    const { fetchMock } = await signInAs(true);
    expect(await screen.findByText(/Signed in as reviewer@example.org/)).toBeInTheDocument();
    const [authUrl, authInit] = fetchMock.mock.calls[0];
    expect(String(authUrl)).toBe("https://demo.supabase.co/auth/v1/token?grant_type=password");
    expect(JSON.parse(String(authInit?.body))).toEqual({ email: "reviewer@example.org", password: "correct horse" });
    const apiCalls = fetchMock.mock.calls.filter(([url]) => String(url).startsWith("/api/"));
    for (const [, init] of apiCalls) {
      expect(String(init?.body ?? "")).not.toContain("correct horse");
      expect((init?.headers as Record<string, string>).Authorization).toBe("Bearer jwt-123");
    }
    expect(localStorage.length).toBe(0);
  });

  it("lets a reviewer record a source check", async () => {
    const { user, fetchMock } = await signInAs(true);
    await screen.findByText("Record a source check");
    await user.selectOptions(screen.getByRole("combobox", { name: "Outcome" }), "changed");
    await user.type(screen.getByRole("textbox", { name: "What you checked" }), "New G.O. posted");
    await user.click(screen.getByRole("button", { name: "Save check" }));
    expect(await screen.findByText(/Check saved/)).toBeInTheDocument();
    const post = fetchMock.mock.calls.find(([url]) => String(url) === "/api/admin/sources/s1/checks");
    expect(JSON.parse(String(post?.[1]?.body))).toEqual({ outcome: "changed", note: "New G.O. posted" });
  });

  it("hides the check form when the role cannot write, and signs out", async () => {
    const { user, fetchMock } = await signInAs(false);
    await screen.findByText("Need human review", { selector: "small" });
    expect(screen.queryByText("Record a source check")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Sign out" }));
    expect(fetchMock.mock.calls.some(([url]) => String(url).endsWith("/auth/v1/logout"))).toBe(true);
    expect(screen.getByLabelText("Password")).toHaveValue("");
  });

  it("shows an error when sign-in is refused", async () => {
    mockApi({ "https://demo.supabase.co/auth/v1/token": { status: 400, body: {} } });
    const user = userEvent.setup();
    render(<AdminPanel t={copy.en} signIn={signIn} />);
    await user.click(screen.getByRole("button", { name: /Maintainer overview/ }));
    await user.type(screen.getByLabelText("Email"), "x@example.org");
    await user.type(screen.getByLabelText("Password"), "wrong");
    await user.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/Sign-in failed/);
  });
});
