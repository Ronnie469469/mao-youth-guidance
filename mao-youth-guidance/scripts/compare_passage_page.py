"""Cross-check queued passages against an independent extractor and render."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

from PIL import Image, ImageStat

from common import jsonl_write, read_json
from verification_common import canonical, cjk_ratio, iter_jsonl, load_results


def image_is_nonblank(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            gray = image.convert("L")
            stat = ImageStat.Stat(gray)
            return stat.mean[0] < 252.5 and stat.var[0] > 2.0
    except Exception:
        return False


def agreement(source: str, independent: str) -> tuple[float, str]:
    left, right = canonical(source), canonical(independent)
    if not left or not right:
        return 0.0, "independent_text_missing"
    if left in right:
        return 1.0, "exact_canonical_substring"
    if right in left and len(right) / len(left) >= 0.985:
        return len(right) / len(left), "near_complete_reverse_substring"
    length_ratio = min(len(left), len(right)) / max(len(left), len(right))
    if length_ratio < 0.9:
        return length_ratio, "length_mismatch"
    ratio = SequenceMatcher(None, left, right).ratio()
    return ratio, "sequence_similarity"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("passages_jsonl", type=Path)
    parser.add_argument("queue_jsonl", type=Path)
    parser.add_argument("manifest_json", type=Path)
    parser.add_argument("raw_dir", type=Path)
    parser.add_argument("render_dir", type=Path)
    parser.add_argument("results_jsonl", type=Path)
    args = parser.parse_args()
    import pdfplumber

    passages = {row["passage_id"]: row for row in iter_jsonl(args.passages_jsonl)}
    manifest = {row["pdf_id"]: row for row in read_json(args.manifest_json, {"files": []}).get("files", [])}
    queue_by_pdf: dict[str, list[dict]] = defaultdict(list)
    for row in iter_jsonl(args.queue_jsonl):
        queue_by_pdf[row["pdf_id"]].append(row)
    results = load_results(args.results_jsonl)
    now = datetime.now(timezone.utc).isoformat()

    for pdf_id, queued in queue_by_pdf.items():
        source = manifest[pdf_id]
        source_path = args.raw_dir / source["filename"]
        try:
            document = pdfplumber.open(source_path)
        except Exception as exc:
            for item in queued:
                results[item["passage_id"]] = {"passage_id": item["passage_id"], "status": "blocked", "reason": f"independent_extractor_failed:{exc.__class__.__name__}", "retry": False, "verification_method": "dual_extraction_plus_render", "verified_at": now}
            continue
        page_cache = {}
        try:
            for item in queued:
                passage = passages[item["passage_id"]]
                page_number = int(item["page"])
                if page_number not in page_cache:
                    try:
                        page_cache[page_number] = document.pages[page_number - 1].extract_text() or ""
                    except Exception:
                        page_cache[page_number] = ""
                rendered = args.render_dir / pdf_id / f"page-{page_number:04d}.jpg"
                render_ok = image_is_nonblank(rendered)
                ratio, method = agreement(passage.get("text", ""), page_cache[page_number])
                if not render_ok:
                    status, reason = "blocked", "render_missing_or_blank"
                elif ratio >= 0.995 and len(canonical(passage.get("text", ""))) >= 20 and cjk_ratio(passage.get("text", "")) >= 0.25:
                    status, reason = "quote_verified", f"independent_agreement:{method}:{ratio:.4f}"
                elif ratio >= 0.8:
                    status, reason = "paraphrase_only", f"partial_independent_agreement:{method}:{ratio:.4f}"
                else:
                    status, reason = "blocked", f"independent_text_mismatch:{method}:{ratio:.4f}"
                row = {"passage_id": item["passage_id"], "status": status, "reason": reason, "retry": False, "verification_method": "pdfplumber_crosscheck_plus_render_sanity", "verified_page": page_number, "verified_paragraph": passage.get("paragraph"), "verified_at": now}
                if status == "quote_verified":
                    row["verified_text"] = passage.get("text", "")
                results[item["passage_id"]] = row
        finally:
            document.close()
        jsonl_write(args.results_jsonl, results.values())
        print(f"{pdf_id}: finalized={len(queued)}", flush=True)
    jsonl_write(args.results_jsonl, results.values())
    print(f"total_results={len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
