"""End-to-end answer evaluation through the real /api/ask pipeline.

    python evaluation/evaluate_answers.py            # search mode only: no Gemini call
    python evaluation/evaluate_answers.py --live 10  # up to 10 Gemini calls, paced under the RPM limit

Measured automatically: mode, citation precision (returned citations that are an expected source),
citation coverage (in-scope answers citing an expected source), gate-rejected claim rate (claims
Gemini produced that the claim-evidence gate removed), abstention on out-of-scope and injection
cases, and end-to-end latency. Answer correctness and faithfulness need a human: every generated
answer is written to evaluation/answer_review.md for that review. Scores are never estimated.
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.gemini import GeminiProvider  # noqa: E402
from app.service import NO_EVIDENCE, TA_NO_EVIDENCE, answer_question  # noqa: E402

HERE = Path(__file__).parent
PACE_SECONDS = 13  # stays under 5 requests/minute


class _OpenBudget:
    def allow(self, _per_minute: int, _per_day: int) -> bool:
        return True


class _CountingProvider:
    """Wraps the real provider to count claims before the evidence gate."""

    def __init__(self, inner: GeminiProvider, live: bool) -> None:
        self.inner, self.live, self.generated_claims = inner, live, 0

    @property
    def available(self) -> bool:
        return self.live and self.inner.available

    def embed(self, contents, task_type):
        return self.inner.embed(contents, task_type)

    def generate(self, question, language, evidence):
        result = self.inner.generate(question, language, evidence)
        self.generated_claims += len(result.claims)
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--live", type=int, default=0, metavar="N", help="max Gemini calls (0 = search mode)")
    args = parser.parse_args()
    cases = json.loads((HERE / "retrieval_cases.json").read_text(encoding="utf-8"))
    provider = _CountingProvider(GeminiProvider(), live=args.live > 0)
    calls, rows, review = 0, [], []
    for case in cases:
        accepted = set(case.get("expected_any") or ([case["expected_source"]] if case.get("expected_source") else []))
        language = "ta" if any("஀" <= ch <= "௿" for ch in case["question"]) else "en"
        live_case = bool(accepted) and calls < args.live
        provider.live = live_case
        before = provider.generated_claims
        start = time.perf_counter()
        response = answer_question(case["question"], language, provider, _OpenBudget(), 99, 9999)
        latency = (time.perf_counter() - start) * 1000
        if live_case:
            calls += 1
        cited = [c.id for c in response.citations]
        abstained = response.text in (NO_EVIDENCE, TA_NO_EVIDENCE) and not cited
        kept = len([p for p in response.text.split("\n\n") if p.strip()]) if response.mode == "ai" else 0
        rows.append({
            "id": case["id"], "in_scope": bool(accepted), "mode": response.mode, "cited": cited,
            "precise": sum(c in accepted for c in cited), "covered": bool(accepted & set(cited)),
            "abstained": abstained, "generated": provider.generated_claims - before, "kept": kept,
            "latency_ms": latency,
        })
        if response.mode == "ai":
            review.append(f"### {case['id']}\n\n**Q:** {case['question']}\n\n{response.text}\n\nCited: {', '.join(cited)}\n\n"
                          "- [ ] Correct  - [ ] Faithful to cited text  - [ ] Unsupported claim present\n")
        if live_case and calls < args.live:
            time.sleep(PACE_SECONDS)
    in_scope = [r for r in rows if r["in_scope"]]
    out_scope = [r for r in rows if not r["in_scope"]]
    ai = [r for r in in_scope if r["mode"] == "ai"]
    total_cited = sum(len(r["cited"]) for r in in_scope)
    generated = sum(r["generated"] for r in rows)
    summary = {
        "gemini_calls": calls,
        "in_scope_cases": len(in_scope),
        "ai_mode_answers": len(ai),
        "search_mode_fallbacks": len(in_scope) - len(ai),
        "citation_precision": round(sum(r["precise"] for r in in_scope) / total_cited, 3) if total_cited else None,
        "citation_coverage": round(sum(r["covered"] for r in in_scope) / len(in_scope), 3) if in_scope else None,
        "ai_citation_coverage": round(sum(r["covered"] for r in ai) / len(ai), 3) if ai else None,
        "claims_generated": generated,
        "claims_rejected_by_gate": generated - sum(r["kept"] for r in rows),
        "gate_rejection_rate": round((generated - sum(r["kept"] for r in rows)) / generated, 3) if generated else None,
        "out_of_scope_abstention": f"{sum(r['abstained'] for r in out_scope)}/{len(out_scope)}",
        "latency_ms_median": round(statistics.median(r["latency_ms"] for r in rows), 1),
        "latency_ms_max_ai": round(max((r["latency_ms"] for r in ai), default=0), 1),
        "provider_state": provider.inner.public_status.get("state"),
    }
    print(json.dumps(summary, indent=2))
    if review:
        (HERE / "answer_review.md").write_text(
            "# Generated answers for human review\n\nGenerated by evaluate_answers.py. Mark each box after reading "
            "the cited source.\n\n" + "\n".join(review), encoding="utf-8")
        print(f"Wrote {len(review)} answers to evaluation/answer_review.md for human review.")
    # Regression gate for CI: every in-scope answer cites its expected source, every probe abstains.
    if summary["citation_coverage"] != 1.0 or any(not r["abstained"] for r in out_scope):
        print("REGRESSION: an expected source was not cited or a probe did not abstain.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
