"""Summarize corpus coverage, mapping, extraction, and approval states."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from common import read_json, write_json


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: corpus_report.py <manifest_json> <output_json>")
        return 2
    manifest_path, output_path = map(Path, sys.argv[1:])
    manifest = read_json(manifest_path, {"files": []})
    passage_count = 0
    index_path = manifest_path.parent / "index" / "passages.jsonl"
    if index_path.exists():
        passage_count = sum(1 for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip())
    report = {"schema": "mao-youth-guidance/corpus-report.v1", "pdf_count": len(manifest.get("files", [])), "mapping_states": dict(Counter(x.get("mapping_status", "unknown") for x in manifest.get("files", []))), "extraction_states": dict(Counter(x.get("extraction_status", "unknown") for x in manifest.get("files", []))), "passage_count": passage_count, "files": [{"pdf_id": x.get("pdf_id"), "filename": x.get("filename"), "pages": x.get("pages"), "mapping_status": x.get("mapping_status"), "extraction_status": x.get("extraction_status")} for x in manifest.get("files", [])]}
    write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
