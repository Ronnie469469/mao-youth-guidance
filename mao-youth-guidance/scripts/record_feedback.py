"""Append anonymized classification feedback and report five-match proposals."""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: record_feedback.py <feedback_jsonl> <field> <correction_key>")
        return 2
    path = Path(sys.argv[1])
    field = sys.argv[2]
    correction = sys.argv[3]
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": datetime.now(timezone.utc).isoformat(), "field": field, "correction_key": correction}
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    counts = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            counts[(item.get("field"), item.get("correction_key"))] += 1
        except json.JSONDecodeError:
            continue
    count = counts[(field, correction)]
    print(f"recorded anonymized feedback; matching corrections={count}; upgrade_proposal={'yes' if count >= 5 else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
