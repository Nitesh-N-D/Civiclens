"""Offline retrieval evaluation; it does not call Gemini or assess generated answers.

Reports Recall@1/@4, Precision@4, MRR, abstention accuracy and latency, overall and per language
(en / ta / mixed). Every case has exactly one relevant source (or an accepted set for ambiguous
questions), so Precision@4 is bounded by 1/k per returned result. Fails CI on regression.
"""

import json
import re
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.gemini import GeminiProvider  # noqa: E402
from app.retrieval import retrieve  # noqa: E402

TAMIL = re.compile(r"[஀-௿]")
LATIN = re.compile(r"[A-Za-z]{3,}")
K = 4


def language_of(question: str) -> str:
    tamil, latin = bool(TAMIL.search(question)), bool(LATIN.search(question))
    return "mixed" if tamil and latin else "ta" if tamil else "en"


def evaluate(cases: list[dict]) -> dict:
    provider = GeminiProvider()
    groups: dict[str, dict] = defaultdict(lambda: {"rr": [], "hit1": 0, "precision": [], "abst": [0, 0]})
    latencies = []
    for case in cases:
        start = time.perf_counter()
        ranked = [source.id for source, _ in retrieve(case["question"], provider, limit=K)]
        latencies.append((time.perf_counter() - start) * 1000)
        accepted = set(case.get("expected_any") or ([case["expected_source"]] if case.get("expected_source") else []))
        for name in ("all", language_of(case["question"])):
            group = groups[name]
            if not accepted:
                group["abst"][0] += not ranked
                group["abst"][1] += 1
                continue
            rank = next((i + 1 for i, sid in enumerate(ranked) if sid in accepted), 0)
            group["rr"].append(1 / rank if rank else 0)
            group["hit1"] += rank == 1
            group["precision"].append(sum(sid in accepted for sid in ranked) / K)
        status = "abstained" if not ranked else f"rank={next((i + 1 for i, s in enumerate(ranked) if s in accepted), 0)}"
        print(f"{case['id']:28} {status:10} returned={ranked}")
    report = {}
    for name, g in sorted(groups.items()):
        n = len(g["rr"])
        report[name] = {
            "cases": n + g["abst"][1],
            "recall_at_4": f"{sum(r > 0 for r in g['rr'])}/{n}",
            "recall_at_1": round(g["hit1"] / n, 3) if n else None,
            "precision_at_4": round(statistics.mean(g["precision"]), 3) if n else None,
            "mrr": round(sum(g["rr"]) / n, 3) if n else None,
            "abstention": f"{g['abst'][0]}/{g['abst'][1]}",
        }
    report["latency_ms"] = {"median": round(statistics.median(latencies), 2), "max": round(max(latencies), 2)}
    return report


def main() -> None:
    cases = json.loads(Path(__file__).with_name("retrieval_cases.json").read_text(encoding="utf-8"))
    report = evaluate(cases)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("Limit: synthetic queries over four hand-authored records; no generation/citation entailment test.")
    overall = report["all"]
    found, total = map(int, overall["recall_at_4"].split("/"))
    abstained, should = map(int, overall["abstention"].split("/"))
    if found < total or abstained < should:
        raise SystemExit("Retrieval evaluation regressed")


if __name__ == "__main__":
    main()
