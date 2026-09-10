"""Render each queued source page once for visual-sanity verification."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from common import read_json
from verification_common import iter_jsonl


def render_pdf(pdf_id: str, source: Path, pages: set[int], output_root: Path, executable: str, dpi: int) -> tuple[str, int, str | None]:
    output_dir = output_root / pdf_id
    output_dir.mkdir(parents=True, exist_ok=True)
    missing = [page for page in sorted(pages) if not (output_dir / f"page-{page:04d}.jpg").exists()]
    if not missing:
        return pdf_id, 0, None
    # Rendering the full span once is much faster than starting Poppler per page.
    first, last = min(missing), max(missing)
    prefix = output_dir / "render"
    command = [executable, "-f", str(first), "-l", str(last), "-jpeg", "-gray", "-r", str(dpi), "-jpegopt", "quality=55", str(source), str(prefix)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return pdf_id, 0, completed.stderr.strip() or f"pdftoppm exit {completed.returncode}"
    created = 0
    for path in output_dir.glob("render-*.jpg"):
        match = re.search(r"-(\d+)\.jpg$", path.name)
        if not match:
            continue
        page = int(match.group(1))
        destination = output_dir / f"page-{page:04d}.jpg"
        if page in pages:
            path.replace(destination)
            created += 1
        else:
            path.unlink()
    return pdf_id, created, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("queue_jsonl", type=Path)
    parser.add_argument("manifest_json", type=Path)
    parser.add_argument("raw_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--dpi", type=int, default=36)
    args = parser.parse_args()
    executable = shutil.which("pdftoppm")
    if not executable:
        raise SystemExit("pdftoppm is unavailable")
    manifest = {row["pdf_id"]: row for row in read_json(args.manifest_json, {"files": []}).get("files", [])}
    pages_by_pdf: dict[str, set[int]] = {}
    for row in iter_jsonl(args.queue_jsonl):
        pages_by_pdf.setdefault(row["pdf_id"], set()).add(int(row["page"]))
    futures = []
    errors = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for pdf_id, pages in pages_by_pdf.items():
            source = manifest.get(pdf_id, {})
            source_path = args.raw_dir / source.get("filename", "")
            futures.append(pool.submit(render_pdf, pdf_id, source_path, pages, args.output_dir, executable, args.dpi))
        for future in as_completed(futures):
            pdf_id, created, error = future.result()
            print(f"{pdf_id}: rendered={created}" + (f" error={error}" if error else ""), flush=True)
            if error:
                errors.append((pdf_id, error))
    print(f"rendered_pdf_sets={len(pages_by_pdf)} errors={len(errors)}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
