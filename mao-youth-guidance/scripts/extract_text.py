"""Extract page-preserving text from PDFs; flag files that need OCR."""
from __future__ import annotations

import sys
from pathlib import Path

from common import language_hint, read_json, write_json


def extract(path: Path) -> tuple[list[dict], str, str | None]:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path), strict=False)
        pages = []
        nonempty = 0
        for number, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            if text:
                nonempty += 1
            pages.append({"page": number, "text": text})
        status = "text_extracted" if nonempty else "ocr_required"
        language = language_hint("\n".join(p["text"] for p in pages))
        return pages, status, language
    except Exception as exc:
        return [], "extraction_failed", f"{exc.__class__.__name__}: {exc}"


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: extract_text.py <raw_dir> <manifest_json> <output_dir>")
        return 2
    raw_dir, manifest_path, output_dir = map(Path, sys.argv[1:])
    manifest = read_json(manifest_path, {"files": []})
    report = []
    for item in manifest.get("files", []):
        pages, status, language_or_error = extract(raw_dir / item["filename"])
        write_json(output_dir / f"{item['pdf_id']}.json", {"pdf_id": item["pdf_id"], "filename": item["filename"], "pages": pages})
        item["extraction_status"] = status
        if status == "extraction_failed":
            item["language"] = "unknown"
            error = language_or_error
        else:
            item["language"] = language_or_error
            error = None
        report.append({"pdf_id": item["pdf_id"], "filename": item["filename"], "status": status, "language": item["language"], "pages_with_text": sum(bool(p["text"]) for p in pages), "error": error})
    write_json(manifest_path, manifest)
    write_json(output_dir / "extraction-report.json", {"schema": "mao-youth-guidance/extraction-report.v1", "items": report})
    print(f"extracted {len(report)} PDFs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
