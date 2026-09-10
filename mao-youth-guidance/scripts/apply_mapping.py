"""Apply human-confirmed PDF mappings to the immutable-file manifest."""
from __future__ import annotations

import sys
from pathlib import Path

from common import read_json, write_json


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: apply_mapping.py <manifest_json> <confirmed_mapping_json>")
        return 2
    manifest_path, mapping_path = map(Path, sys.argv[1:])
    manifest = read_json(manifest_path, {"files": []})
    mappings = {x["pdf_id"]: x for x in read_json(mapping_path, {}).get("items", [])}
    changed = 0
    for item in manifest.get("files", []):
        mapped = mappings.get(item["pdf_id"])
        if not mapped:
            continue
        status = mapped.get("status", "unmapped")
        item["mapping_status"] = status
        if status == "confirmed":
            item["work"] = mapped.get("work")
            item["volume"] = mapped.get("volume")
            item["date_range"] = mapped.get("date_range")
            item["edition"] = mapped.get("edition")
            item["page_offset"] = mapped.get("page_offset", 0)
            item["language"] = mapped.get("language", item.get("language", "unknown"))
            item["mapping_notes"] = mapped.get("notes")
        changed += 1
    write_json(manifest_path, manifest)
    print(f"applied {changed} mapping records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
