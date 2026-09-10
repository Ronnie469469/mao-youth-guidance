"""Create human-reviewable title and volume candidates for numbered PDFs."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from common import read_json, write_json


def first_pages(path: Path, limit: int = 5) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path), strict=False)
        return "\n".join((page.extract_text() or "") for page in reader.pages[:limit])
    except Exception:
        return ""


def candidates(text: str) -> list[str]:
    patterns = [
        r"《[^》]{2,40}》",
        r"毛泽东选集[^\n]{0,20}",
        r"毛泽东文集[^\n]{0,20}",
    ]
    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text))
    return list(dict.fromkeys(x.strip() for x in found if x.strip()))[:10]


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: identify_pdfs.py <raw_dir> <manifest_json> <output_dir>")
        return 2
    raw_dir, manifest_path, output_dir = map(Path, sys.argv[1:])
    manifest = read_json(manifest_path, {"files": []})
    rows = []
    for item in manifest.get("files", []):
        text = first_pages(raw_dir / item["filename"])
        found = candidates(text)
        rows.append({
            "pdf_id": item["pdf_id"],
            "filename": item["filename"],
            "candidate_titles": found,
            "evidence_excerpt": " ".join(text.split())[:500],
            "confidence": 0.0 if not found else min(0.95, 0.45 + 0.1 * len(found)),
            "status": "awaiting_user_confirmation",
        })
    write_json(output_dir / "pdf-mapping-candidates.json", {"schema": "mao-youth-guidance/pdf-candidates.v1", "items": rows})
    lines = ["# PDF mapping candidates", "", "Confirm or correct each row before quoting.", ""]
    for row in rows:
        titles = "、".join(row["candidate_titles"]) or "未识别"
        lines += [f"## {row['pdf_id']} - {row['filename']}", f"- 候选：{titles}", f"- 置信度：{row['confidence']:.2f}", f"- 证据：{row['evidence_excerpt']}", "- 确认结果：", ""]
    (output_dir / "pdf-mapping-candidates.md").parent.mkdir(parents=True, exist_ok=True)
    (output_dir / "pdf-mapping-candidates.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"created candidates for {len(rows)} PDFs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
