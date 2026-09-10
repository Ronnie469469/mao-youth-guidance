"""Normalize extracted page JSON while retaining page boundaries."""
from __future__ import annotations

import sys
from pathlib import Path

from common import normalize_text, read_json, write_json


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: normalize_text.py <extracted_dir> <normalized_dir>")
        return 2
    source_dir, output_dir = map(Path, sys.argv[1:])
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for source in sorted(source_dir.glob("pdf-*.json")):
        data = read_json(source, {})
        pages = [{"page": p["page"], "text": normalize_text(p.get("text", ""))} for p in data.get("pages", [])]
        write_json(output_dir / source.name, {**data, "pages": pages})
        count += 1
    print(f"normalized {count} extracted files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
