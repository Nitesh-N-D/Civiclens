import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { EligibilityChecker, SchemeComparison } from "../components/EligibilityChecker";
import { copy } from "../copy";
import { mockApi, scheme } from "./fixtures";

const schemes = [scheme({ id: "pp", title: "Pudhumai Penn", eligibility_enabled: true }), scheme({ id: "fe", title: "Free Education", eligibility_enabled: true })];
const source = { id: "s1", title: "myScheme page", url: "https://www.myscheme.gov.in/x", owner: "myScheme", status: "Official directory", desk_checked_at: "2026-11-10" };
const result = {
  scheme_id: "pp", status: "requires_official_verification", missing_fields: [],
  criteria: [{ id: "c1", label: "Girl student", field: "gender", outcome: "met", source_id: "s1", basis: "girl students", human_verified: false }],
  documents: [{ name: "Proof of admission", reason: "Course required", criterion_id: "c1", source_id: "s1", mandatory: false, verification: "not_named_by_source" }],
  guidance: { route: "Penkalvi portal", steps: ["Open the official page"], contact: "Social Welfare Department", source_id: "s1" },
};

afterEach(() => vi.unstubAllGlobals());

describe("EligibilityChecker", () => {
  it("sends only chosen answers and shows a verification-first result with its source", async () => {
    const fetchMock = mockApi({
      "/api/eligibility/questions": { body: { questions: [{ field: "gender", options: ["female", "male"], purpose: "The summary refers to girl students." }] } },
      "/api/eligibility": { body: { results: [result], sources: [source] } },
    });
    render(<EligibilityChecker t={copy.en} language="en" schemes={schemes} />);
    await userEvent.selectOptions(await screen.findByRole("combobox", { name: /gender/i }), "female");
    await userEvent.click(screen.getByRole("button", { name: copy.en.eligibilityRun }));

    expect(await screen.findByText(copy.en.statusLabels.requires_official_verification)).toBeInTheDocument();
    expect(screen.getByText(copy.en.eligibilityCaveat)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /myScheme page/ })).toHaveAttribute("href", source.url);
    const call = fetchMock.mock.calls.find(([url]) => String(url) === "/api/eligibility");
    expect(JSON.parse(String(call?.[1]?.body))).toEqual({ profile: { gender: "female" }, language: "en", scheme_ids: [] });
  });

  it("renders nothing when no scheme supports screening", () => {
    mockApi({});
    const { container } = render(<EligibilityChecker t={copy.en} language="en" schemes={[scheme()]} />);
    expect(container).toBeEmptyDOMElement();
  });
});

describe("SchemeComparison", () => {
  it("compares two selected schemes side by side", async () => {
    mockApi({ "/api/schemes/compare": { body: { schemes: [
      { scheme_id: "pp", criteria: ["Girl student"], documents: [], route: "Penkalvi portal", contact: "SWD", source_id: "s1" },
      { scheme_id: "fe", criteria: ["Undergraduate"], documents: [], route: "Not named", contact: "BC Dept", source_id: "s1" },
    ], sources: [source] } } });
    render(<SchemeComparison t={copy.en} language="en" schemes={schemes} />);
    const run = screen.getByRole("button", { name: copy.en.compareRun });
    expect(run).toBeDisabled();
    await userEvent.click(screen.getByLabelText("Pudhumai Penn"));
    await userEvent.click(screen.getByLabelText("Free Education"));
    await userEvent.click(run);
    expect(await screen.findByRole("table")).toBeInTheDocument();
    expect(screen.getByText("Penkalvi portal")).toBeInTheDocument();
  });
});
