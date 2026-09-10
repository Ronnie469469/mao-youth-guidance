"""Export finalized blocked passages so later runs skip them explicitly."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from verification_common import iter_jsonl


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results_jsonl", type=Path)
    parser.add_argument("output_jsonl", type=Path)
    args = parser.parse_args()
    rows = []
    for result in iter_jsonl(args.results_jsonl):
        if result.get("status") != "blocked":
            continue
        rows.append(
            {
                "passage_id": result["passage_id"],
                "reason": result.get("reason", "unspecified_verification_failure"),
                "retry": False,
                "status": "blocked",
                "verification_method": result.get("verification_method"),
                "verified_at": result.get("verified_at"),
            }
        )
    rows.sort(key=lambda row: row["passage_id"])
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output_jsonl.with_suffix(args.output_jsonl.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(args.output_jsonl)
    print(f"blocked={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
