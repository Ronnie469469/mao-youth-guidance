"""Promote approved thought cards into a versioned knowledge-base directory."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from common import read_json, write_json


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: apply_review.py <draft_json> <index_jsonl> <knowledge_base_version_dir>")
        return 2
    draft_path, index_path, target = map(Path, sys.argv[1:])
    draft = read_json(draft_path, {})
    approved = [card for card in draft.get("cards", []) if card.get("review_status") == "approved"]
    target.mkdir(parents=True, exist_ok=True)
    write_json(target / "thought-cards.json", {"schema": "mao-youth-guidance/approved-thought-cards.v1", "cards": approved, "count": len(approved)})
    (target / "passages.jsonl").write_text(index_path.read_text(encoding="utf-8") if index_path.exists() else "", encoding="utf-8")
    write_json(target / "concept-relations.json", {"schema": "mao-youth-guidance/concept-relations.v1", "relations": draft.get("relations", [])})
    write_json(target / "manifest.json", {"schema": "mao-youth-guidance/knowledge-base.v1", "source_draft": str(draft_path), "approved_cards": len(approved), "status": "active" if approved else "empty"})
    print(f"promoted {len(approved)} approved thought cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
