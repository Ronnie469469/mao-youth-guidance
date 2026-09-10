"""Register numbered PDFs without changing their contents.

Usage: python inspect_pdfs.py <raw_dir> <manifest_json>
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from common import sha256, write_json


def pdf_metadata(path: Path) -> dict:
    result = {"pages": None, "title": None, "author": None, "producer": None}
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path), strict=False)
        result["pages"] = len(reader.pages)
        metadata = reader.metadata or {}
        result["title"] = metadata.get("/Title")
        result["author"] = metadata.get("/Author")
        result["producer"] = metadata.get("/Producer")
        return result
    except Exception as exc:
        result["error"] = f"pypdf: {exc.__class__.__name__}"
    try:
        completed = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=False)
        for line in completed.stdout.splitlines():
            key, _, value = line.partition(":")
            key = key.strip().lower()
            if key == "pages":
                result["pages"] = int(value.strip())
            elif key in {"title", "author", "producer"}:
                result[key] = value.strip() or None
    except (OSError, ValueError):
        result["error"] = result.get("error", "pdfinfo unavailable")
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: inspect_pdfs.py <raw_dir> <manifest_json>")
        return 2
    raw_dir, manifest_path = map(Path, sys.argv[1:])
    files = sorted(raw_dir.glob("*.pdf"), key=lambda p: p.name.lower())
    rows = []
    for index, path in enumerate(files, 1):
        info = pdf_metadata(path)
        rows.append({
            "pdf_id": f"pdf-{index:04d}",
            "filename": path.name,
            "file_number": path.stem,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "pages": info.pop("pages", None),
            "metadata": info,
            "mapping_status": "unmapped",
            "extraction_status": "pending",
            "verification_status": "unverified",
        })
    write_json(manifest_path, {"schema": "mao-youth-guidance/source-manifest.v1", "files": rows})
    print(f"registered {len(rows)} PDF files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
