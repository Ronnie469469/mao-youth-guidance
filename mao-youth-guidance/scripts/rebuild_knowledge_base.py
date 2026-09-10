"""Build knowledge-base/v2 from finalized verification artifacts."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from common import read_json
from verification_common import FINAL_STATES, iter_jsonl


CURATED_FALLBACK_PASSAGES = {
    "thought-005": ["pdf-0027-p0087-001"],
    "thought-013": ["pdf-0027-p0385-001"],
}


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("passages_jsonl", type=Path)
    parser.add_argument("results_jsonl", type=Path)
    parser.add_argument("quotes_jsonl", type=Path)
    parser.add_argument("blocked_jsonl", type=Path)
    parser.add_argument("thought_cards_json", type=Path)
    parser.add_argument("relations_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    passages = list(iter_jsonl(args.passages_jsonl))
    results = {row["passage_id"]: row for row in iter_jsonl(args.results_jsonl)}
    passage_ids = {row["passage_id"] for row in passages}
    if len(results) != len(passages) or set(results) != passage_ids:
        missing = passage_ids - set(results)
        extra = set(results) - passage_ids
        raise SystemExit(
            f"verification is incomplete: passages={len(passages)} results={len(results)} "
            f"missing={len(missing)} extra={len(extra)}"
        )
    invalid = [pid for pid, row in results.items() if row.get("status") not in FINAL_STATES]
    if invalid:
        raise SystemExit(f"verification has {len(invalid)} non-final statuses")

    merged_passages = []
    for passage in passages:
        result = results[passage["passage_id"]]
        merged = dict(passage)
        merged["quote_status"] = result["status"]
        for key in (
            "verified_text",
            "verified_page",
            "verified_paragraph",
            "verification_method",
            "reason",
            "verified_at",
        ):
            if key in result:
                merged[key] = result[key]
        merged_passages.append(merged)

    quotes = list(iter_jsonl(args.quotes_jsonl))
    quotes_by_passage: dict[str, list[dict]] = defaultdict(list)
    for quote in quotes:
        if quote.get("quote_status") != "quote_verified":
            raise SystemExit(f"non-verified quote in registry: {quote.get('quote_id')}")
        if quote.get("passage_id") not in passage_ids:
            raise SystemExit(f"quote points to missing passage: {quote.get('quote_id')}")
        quotes_by_passage[quote["passage_id"]].append(quote)

    cards_data = read_json(args.thought_cards_json, {})
    cards = []
    for source_card in cards_data.get("cards", []):
        if source_card.get("review_status") != "approved":
            continue
        card = dict(source_card)
        ranked_quotes = []
        keywords = [str(keyword).lower() for keyword in card.get("keywords", [])]
        candidate_passages = list(card.get("source_passages", []))
        candidate_passages.extend(CURATED_FALLBACK_PASSAGES.get(card.get("thought_id"), []))
        for passage_id in candidate_passages:
            for quote in quotes_by_passage.get(passage_id, []):
                text = str(quote.get("quote_text", "")).lower()
                score = sum(3 + len(keyword) for keyword in keywords if keyword in text)
                if score:
                    ranked_quotes.append((score, quote["quote_id"]))
        ranked_quotes.sort(key=lambda item: (-item[0], item[1]))
        quote_ids = list(dict.fromkeys(quote_id for _, quote_id in ranked_quotes[:4]))
        card["verified_quote_ids"] = quote_ids
        card["verified_source_passages"] = list(
            dict.fromkeys(
                quote["passage_id"]
                for quote_id in quote_ids
                for quote in quotes
                if quote["quote_id"] == quote_id
            )
        )
        card["quote_status"] = "quote_verified" if quote_ids else "paraphrase_only"
        if quote_ids:
            card.pop("quote_note", None)
        else:
            card["quote_note"] = (
                "当前资料未找到可安全逐字引用的代表段落，只能进行明确标注的转述。"
            )
        cards.append(card)
    card_output = {
        "schema": "mao-youth-guidance/approved-thought-cards.v2",
        "cards": cards,
        "count": len(cards),
    }

    relations = read_json(args.relations_json, {})
    relations["schema"] = "mao-youth-guidance/concept-relations.v2"
    blocked = list(iter_jsonl(args.blocked_jsonl))
    counts = Counter(row["status"] for row in results.values())
    manifest = {
        "schema": "mao-youth-guidance/knowledge-base.v2",
        "version": "v2",
        "source_version": "v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "total_passages": len(passages),
        "quote_verified": counts["quote_verified"],
        "paraphrase_only": counts["paraphrase_only"],
        "blocked": counts["blocked"],
        "unverified": len(passages) - sum(counts.values()),
        "verified_quotes": len(quotes),
        "approved_cards": len(cards),
        "concept_relations": len(relations.get("relations", [])),
        "verification_policy": "conservative dual extraction plus render sanity; reliable passages only",
        "manual_visual_review": False,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl_atomic(args.output_dir / "passages.jsonl", merged_passages)
    write_jsonl_atomic(args.output_dir / "verified-quotes.jsonl", quotes)
    write_jsonl_atomic(args.output_dir / "blocked-passages.jsonl", blocked)
    write_json_atomic(args.output_dir / "thought-cards.json", card_output)
    write_json_atomic(args.output_dir / "concept-relations.json", relations)
    write_json_atomic(args.output_dir / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
