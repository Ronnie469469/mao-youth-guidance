"""Precheck every passage and create a resumable verification queue.

Usage: python verify_all_passages.py <passages_jsonl> <manifest_json> <raw_dir> <qa_dir>
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from common import jsonl_write, read_json
from verification_common import FINAL_STATES, iter_jsonl, load_results, structural_reason


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: verify_all_passages.py <passages_jsonl> <manifest_json> <raw_dir> <qa_dir>")
        return 2
    index_path, manifest_path, raw_dir, qa_dir = map(Path, sys.argv[1:])
    files = {row["pdf_id"]: row for row in read_json(manifest_path, {"files": []}).get("files", [])}
    results_path = qa_dir / "passage-verification.jsonl"
    prior = load_results(results_path)
    queue, immediate = [], []
    now = datetime.now(timezone.utc).isoformat()
    for passage in iter_jsonl(index_path):
        passage_id = passage["passage_id"]
        if passage_id in prior and prior[passage_id].get("status") in FINAL_STATES:
            continue
        source = files.get(passage.get("pdf_id"))
        reason = None
        status = None
        if not source:
            status, reason = "blocked", "manifest_entry_missing"
        elif source.get("mapping_status") != "confirmed":
            status, reason = "blocked", "pdf_mapping_not_confirmed"
        elif not (raw_dir / source["filename"]).is_file():
            status, reason = "blocked", "source_pdf_missing"
        elif not isinstance(passage.get("page"), int) or passage["page"] < 1 or passage["page"] > int(source.get("pages") or 0):
            status, reason = "blocked", "page_out_of_range"
        else:
            reason = structural_reason(passage.get("text", ""))
            if reason:
                status = "paraphrase_only" if reason in {"too_short_for_reliable_quote", "front_matter_or_reference_material", "table_of_contents", "page_number_or_date_only"} else "blocked"
        if status:
            immediate.append({"passage_id": passage_id, "status": status, "reason": reason, "retry": False, "verification_method": "automatic_precheck", "verified_at": now})
        else:
            queue.append({"passage_id": passage_id, "pdf_id": passage["pdf_id"], "filename": passage["filename"], "page": passage["page"]})
    merged = list(prior.values()) + immediate
    jsonl_write(results_path, merged)
    jsonl_write(qa_dir / "verification-queue.jsonl", queue)
    print(f"prechecked={len(immediate)} queued={len(queue)} retained_final={len(prior)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
