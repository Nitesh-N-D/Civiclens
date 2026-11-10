import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { SchemeExplorer, filterSchemes } from "../components/SchemeExplorer";
import { copy } from "../copy";
import { scheme } from "./fixtures";

const schemes = [
  scheme(),
  scheme({ id: "edu", title: "புதுமைப் பெண்", department: "சமூக நலத் துறை", category: "கல்வி", overview: "மாணவிகளுக்கு மாத உதவி" }),
];

describe("filterSchemes", () => {
  it("matches title, department and overview case-insensitively", () => {
    expect(filterSchemes(schemes, "PENSION", "").map((s) => s.id)).toEqual(["pension"]);
    expect(filterSchemes(schemes, "revenue", "").map((s) => s.id)).toEqual(["pension"]);
  });

  it("matches Tamil text and filters by category", () => {
    expect(filterSchemes(schemes, "மாணவி", "").map((s) => s.id)).toEqual(["edu"]);
    expect(filterSchemes(schemes, "", "கல்வி").map((s) => s.id)).toEqual(["edu"]);
    expect(filterSchemes(schemes, "pension", "கல்வி")).toEqual([]);
  });
});

describe("SchemeExplorer", () => {
  it("narrows by category and says when nothing matches", async () => {
    const user = userEvent.setup();
    render(<SchemeExplorer t={copy.en} schemes={schemes} />);
    await user.selectOptions(screen.getByRole("combobox", { name: "Category" }), "கல்வி");
    expect(screen.queryByText("Old Age Pension")).not.toBeInTheDocument();
    await user.type(screen.getByRole("searchbox"), "zzz");
    expect(screen.getByText(/No program matches/)).toBeInTheDocument();
  });

  it("links every card to its official directory in a new tab without a referrer", () => {
    render(<SchemeExplorer t={copy.en} schemes={schemes} />);
    for (const link of screen.getAllByRole("link", { name: /Open official directory/ })) {
      expect(link.getAttribute("href")).toMatch(/^https:\/\//);
      expect(link).toHaveAttribute("rel", "noreferrer");
    }
  });
});
