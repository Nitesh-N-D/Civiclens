import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import App from "../App";
import { answer, baseRoutes, mockApi } from "./fixtures";

async function renderInEnglish() {
  const user = userEvent.setup();
  render(<App />);
  await user.click(screen.getByRole("button", { name: "EN" }));
  return user;
}

describe("App", () => {
  it("starts in Tamil and switches to English", async () => {
    mockApi(baseRoutes);
    const user = userEvent.setup();
    render(<App />);
    expect(document.documentElement.lang).toBe("ta");
    expect(screen.getByText("சுயாதீன தகவல் சேவை · அரசு இணையதளம் அல்ல")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "EN" }));
    expect(document.documentElement.lang).toBe("en");
    expect(screen.getByText(/Not a government website/)).toBeInTheDocument();
  });

  it("asks a question and shows the answer with its citation", async () => {
    const fetchMock = mockApi({ ...baseRoutes, "/api/ask": { body: answer } });
    const user = await renderInEnglish();
    await user.type(screen.getByRole("textbox", { name: /Ask about a scheme/ }), "old age pension");
    await user.click(screen.getByRole("button", { name: /Ask CivicLens/ }));
    expect(await screen.findByText(answer.text, { selector: ".answer-text" })).toBeInTheDocument();
    const link = screen.getByRole("link", { name: /CRA pensions/ });
    expect(link).toHaveAttribute("href", "https://example.gov.in/cra");
    expect(link).toHaveAttribute("rel", "noreferrer");
    const call = fetchMock.mock.calls.find(([url]) => String(url) === "/api/ask");
    expect(JSON.parse(String(call?.[1]?.body))).toEqual({ question: "old age pension", language: "en" });
  });

  it("keeps earlier questions on screen during the visit", async () => {
    mockApi({ ...baseRoutes, "/api/ask": { body: answer } });
    const user = await renderInEnglish();
    await user.type(screen.getByRole("textbox", { name: /Ask about a scheme/ }), "first question{Enter}");
    await screen.findByText(answer.text, { selector: ".answer-text" });
    await user.type(screen.getByRole("textbox", { name: "Ask another question" }), "second question{Enter}");
    await waitFor(() => expect(screen.getAllByText(answer.text, { selector: ".answer-text" })).toHaveLength(2));
    expect(screen.getByRole("heading", { level: 3, name: "first question" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "second question" })).toBeInTheDocument();
  });

  it("explains a rate limit instead of failing", async () => {
    mockApi({ ...baseRoutes, "/api/ask": { status: 429, body: { detail: "slow down" } } });
    const user = await renderInEnglish();
    await user.type(screen.getByRole("textbox", { name: /Ask about a scheme/ }), "pension{Enter}");
    expect(await screen.findByText(/Please wait a minute/, { selector: ".answer-text" })).toBeInTheDocument();
    expect(screen.queryByText(/The API is unavailable/)).not.toBeInTheDocument();
  });

  it("shows a safe fallback when the API is down", async () => {
    mockApi({});
    const user = await renderInEnglish();
    await user.type(screen.getByRole("textbox", { name: /Ask about a scheme/ }), "pension{Enter}");
    expect(await screen.findByText(/find enough reviewed information/, { selector: ".answer-text" })).toBeInTheDocument();
    expect(screen.getByText(/The API is unavailable/)).toBeInTheDocument();
  });

  it("toggles and remembers the theme", async () => {
    mockApi(baseRoutes);
    const user = await renderInEnglish();
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    await user.click(screen.getByRole("button", { name: /Switch to (dark|light) mode/ }));
    expect(document.documentElement.dataset.theme).toBe(next);
    expect(localStorage.getItem("civiclens-theme")).toBe(next);
  });

  it("filters the scheme directory", async () => {
    mockApi(baseRoutes);
    const user = await renderInEnglish();
    const explorer = (await screen.findByText("Free Education Scheme")).closest("section") as HTMLElement;
    await user.type(within(explorer).getByRole("searchbox", { name: "Search programs" }), "pension");
    expect(within(explorer).queryByText("Free Education Scheme")).not.toBeInTheDocument();
    expect(within(explorer).getByText("Old Age Pension")).toBeInTheDocument();
  });

  it("hides the maintainer panel unless the API enables it", async () => {
    mockApi(baseRoutes);
    await renderInEnglish();
    await screen.findByText("Old Age Pension");
    expect(screen.queryByRole("button", { name: /Maintainer/ })).not.toBeInTheDocument();
  });
});
