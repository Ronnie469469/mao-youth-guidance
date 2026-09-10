"""Validate and summarize the complete v2 passage-verification run."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from common import read_json
from verification_common import FINAL_STATES, canonical, iter_jsonl


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_passages_jsonl", type=Path)
    parser.add_argument("results_jsonl", type=Path)
    parser.add_argument("quotes_jsonl", type=Path)
    parser.add_argument("blocked_jsonl", type=Path)
    parser.add_argument("knowledge_base_dir", type=Path)
    parser.add_argument("render_dir", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()

    source = {row["passage_id"]: row for row in iter_jsonl(args.source_passages_jsonl)}
    results = {row["passage_id"]: row for row in iter_jsonl(args.results_jsonl)}
    quotes = list(iter_jsonl(args.quotes_jsonl))
    blocked = list(iter_jsonl(args.blocked_jsonl))
    cards_data = read_json(args.knowledge_base_dir / "thought-cards.json", {})
    manifest = read_json(args.knowledge_base_dir / "manifest.json", {})
    errors = []

    missing = set(source) - set(results)
    extra = set(results) - set(source)
    if missing:
        errors.append(f"missing verification results: {len(missing)}")
    if extra:
        errors.append(f"verification results without source passages: {len(extra)}")
    nonfinal = [pid for pid, row in results.items() if row.get("status") not in FINAL_STATES]
    if nonfinal:
        errors.append(f"non-final verification results: {len(nonfinal)}")

    status_counts = Counter(row.get("status", "missing") for row in results.values())
    reason_counts = Counter(
        str(row.get("reason", "unspecified")).split(":", 1)[0]
        for row in results.values()
    )
    quote_ids = set()
    for quote in quotes:
        quote_id = quote.get("quote_id")
        if not quote_id or quote_id in quote_ids:
            errors.append(f"duplicate or missing quote id: {quote_id}")
        quote_ids.add(quote_id)
        passage_id = quote.get("passage_id")
        result = results.get(passage_id, {})
        if result.get("status") != "quote_verified":
            errors.append(f"quote {quote_id} points to non-verified passage {passage_id}")
        if canonical(quote.get("quote_text", "")) not in canonical(result.get("verified_text") or ""):
            errors.append(f"quote {quote_id} is not an exact substring of verified text")
        if not quote.get("pdf_id") or not quote.get("page"):
            errors.append(f"quote {quote_id} lacks PDF/page provenance")
        render = args.render_dir / str(quote.get("pdf_id")) / f"page-{int(quote.get('page') or 0):04d}.jpg"
        if not render.is_file():
            errors.append(f"quote {quote_id} lacks cached render")

    blocked_ids = {row.get("passage_id") for row in blocked}
    expected_blocked = {pid for pid, row in results.items() if row.get("status") == "blocked"}
    if blocked_ids != expected_blocked:
        errors.append(
            f"blocked export mismatch: expected={len(expected_blocked)} actual={len(blocked_ids)}"
        )
    if any(row.get("retry") is not False for row in blocked):
        errors.append("one or more blocked passages are retryable")

    cards = cards_data.get("cards", [])
    if len(cards) != 18 or any(card.get("review_status") != "approved" for card in cards):
        errors.append("expected exactly 18 approved thought cards")
    for card in cards:
        missing_quote_ids = set(card.get("verified_quote_ids", [])) - quote_ids
        if missing_quote_ids:
            errors.append(f"{card.get('thought_id')} has missing quote ids")

    expected_total = len(source)
    if manifest.get("total_passages") != expected_total:
        errors.append("manifest total_passages does not match source")
    for status in sorted(FINAL_STATES):
        if manifest.get(status) != status_counts[status]:
            errors.append(f"manifest {status} count does not match results")
    if manifest.get("unverified") != 0:
        errors.append("manifest still reports unverified passages")

    report = {
        "schema": "mao-youth-guidance/passage-verification-report.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": not errors,
        "errors": errors[:100],
        "total_passages": expected_total,
        "status_counts": dict(sorted(status_counts.items())),
        "reason_code_counts": dict(reason_counts.most_common()),
        "verified_quotes": len(quotes),
        "blocked_exported": len(blocked),
        "approved_cards": len(cards),
        "cards_with_quotes": sum(bool(card.get("verified_quote_ids")) for card in cards),
        "manual_visual_review": False,
        "verification_note": (
            "quote_verified means two independent PDF text extractors agreed and a cached page render was nonblank; "
            "it does not claim human visual review of every rendered page."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output_json.with_suffix(args.output_json.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(args.output_json)
    print(
        f"ok={report['ok']} total={expected_total} statuses={dict(status_counts)} "
        f"quotes={len(quotes)} cards_with_quotes={report['cards_with_quotes']} "
        f"errors={len(errors)}"
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
