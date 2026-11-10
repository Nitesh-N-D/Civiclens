"""Small offline retrieval check; it does not call Gemini or assess answer correctness."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.gemini import GeminiProvider
from app.retrieval import retrieve


def main() -> None:
    cases_path = Path(__file__).with_name("retrieval_cases.json")
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    provider = GeminiProvider()
    reciprocal_ranks = []
    correct_top1 = 0
    abstention_correct = 0

    for case in cases:
        results = retrieve(case["question"], provider, limit=4)
        ranked_ids = [source.id for source, _score in results]
        expected = case["expected_source"]
        if expected is None:
            abstention_correct += not ranked_ids
            print(f"{case['id']}: expected abstention; returned={ranked_ids}")
            continue
        rank = ranked_ids.index(expected) + 1 if expected in ranked_ids else 0
        reciprocal_ranks.append(1 / rank if rank else 0)
        correct_top1 += bool(ranked_ids and ranked_ids[0] == expected)
        print(f"{case['id']}: expected={expected}; rank={rank}; returned={ranked_ids}")

    relevant_count = len(reciprocal_ranks)
    mrr = sum(reciprocal_ranks) / relevant_count if relevant_count else 0
    top1 = correct_top1 / relevant_count if relevant_count else 0
    abstention_count = sum(case["expected_source"] is None for case in cases)
    abstention_accuracy = abstention_correct / abstention_count if abstention_count else 0
    print(f"Recall@4: {sum(score > 0 for score in reciprocal_ranks)}/{relevant_count}")
    print(f"MRR: {mrr:.3f}")
    print(f"Top-1 accuracy: {top1:.3f}")
    print(f"Out-of-scope abstention accuracy: {abstention_accuracy:.3f}")
    print("Limit: synthetic queries over four hand-authored records; no generation/citation entailment test.")
    # Fail CI on regression: every in-scope case found, every out-of-scope case abstained.
    if sum(score > 0 for score in reciprocal_ranks) < relevant_count or abstention_accuracy < 1.0:
        raise SystemExit("Retrieval evaluation regressed")


if __name__ == "__main__":
    main()
