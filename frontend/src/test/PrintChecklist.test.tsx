import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PrintChecklist } from "../components/PrintChecklist";
import { copy } from "../copy";
import { answer } from "./fixtures";

describe("PrintChecklist", () => {
  it("prints the question, the official link and the safety steps", () => {
    const { container } = render(<PrintChecklist turn={{ question: "pension?", answer }} t={copy.en} />);
    const text = container.textContent ?? "";
    expect(text).toContain("pension?");
    expect(text).toContain("https://example.gov.in/cra");
    expect(text).toContain("Never share your Aadhaar, bank details or OTP");
    expect(text).toContain("not a government website");
  });
});
