"""Validate thought-card passage and verified-quote references."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from common import read_json, write_json


def main() -> int:
    if len(sys.argv) not in {3, 4}:
        print("usage: verify_passages.py <thought_cards_json> <index_jsonl> [verified_quotes_jsonl]")
        return 2
    cards_path, index_path = map(Path, sys.argv[1:3])
    cards_data = read_json(cards_path, {})
    passages = {}
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            passages[row["passage_id"]] = row
    quotes = {}
    if len(sys.argv) == 4:
        quotes_path = Path(sys.argv[3])
        if quotes_path.exists():
            for line in quotes_path.read_text(encoding="utf-8").splitlines():
                if line:
                    row = json.loads(line)
                    quotes[row["quote_id"]] = row
    errors = []
    for card in cards_data.get("cards", []):
        for passage_id in card.get("source_passages", []):
            if passage_id not in passages:
                errors.append(f"{card.get('thought_id')}: missing {passage_id}")
        verified_quote_ids = card.get("verified_quote_ids", [])
        if verified_quote_ids and not quotes:
            errors.append(f"{card.get('thought_id')}: quote registry was not provided")
        for quote_id in verified_quote_ids:
            quote = quotes.get(quote_id)
            if not quote:
                errors.append(f"{card.get('thought_id')}: missing quote {quote_id}")
                continue
            passage = passages.get(quote.get("passage_id"))
            if not passage or passage.get("quote_status") != "quote_verified":
                errors.append(f"{card.get('thought_id')}: quote {quote_id} has no verified passage")
        if card.get("quote_status") == "quote_verified" and not verified_quote_ids:
            errors.append(f"{card.get('thought_id')}: verified card has no verified_quote_ids")
    report = {"schema": "mao-youth-guidance/verification-report.v1", "ok": not errors, "errors": errors, "cards": len(cards_data.get("cards", [])), "passages": len(passages)}
    write_json(cards_path.parent / "verification-report.json", report)
    print("verification passed" if not errors else f"verification failed: {len(errors)} errors")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
