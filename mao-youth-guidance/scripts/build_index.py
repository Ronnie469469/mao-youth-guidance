"""Build a page/paragraph retrieval index; passages remain unverified by default."""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

from common import jsonl_write, read_json, write_json


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: build_index.py <normalized_dir> <mapping_json> <index_jsonl>")
        return 2
    normalized_dir, mapping_path, index_path = map(Path, sys.argv[1:])
    mapping = {x["pdf_id"]: x for x in read_json(mapping_path, {}).get("items", [])}
    rows = []
    for source in sorted(normalized_dir.glob("pdf-*.json")):
        data = read_json(source, {})
        pdf_id = data.get("pdf_id", source.stem)
        mapped = mapping.get(pdf_id, {})
        work = mapped.get("work") or mapped.get("title")
        for page in data.get("pages", []):
            chunks = [x.strip() for x in re.split(r"\n\s*\n", page.get("text", "")) if x.strip()]
            if not chunks and page.get("text"):
                chunks = [page["text"]]
            for number, text in enumerate(chunks, 1):
                passage_id = f"{pdf_id}-p{int(page['page']):04d}-{number:03d}"
                rows.append({
                    "passage_id": passage_id,
                    "pdf_id": pdf_id,
                    "filename": data.get("filename"),
                    "work": work,
                    "volume": mapped.get("volume"),
                    "date_range": mapped.get("date_range"),
                    "edition": mapped.get("edition"),
                    "language": mapped.get("language", "unknown"),
                    "page": page["page"],
                    "paragraph": number,
                    "text": text,
                    "text_hash": hashlib.sha256(text.encode('utf-8')).hexdigest(),
                    "quote_status": "unverified",
                })
    jsonl_write(index_path, rows)
    print(f"indexed {len(rows)} passages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
