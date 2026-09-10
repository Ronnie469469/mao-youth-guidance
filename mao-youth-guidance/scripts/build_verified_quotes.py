"""Build a deterministic registry of short quotations from verified passages."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import read_json
from verification_common import canonical, cjk_ratio, iter_jsonl, structural_reason


SENTENCE_RE = re.compile(r"[^。！？!?；;]+[。！？!?；;]?")
EDITORIAL_MARKERS = (
    "本电子版",
    "整理者",
    "编者",
    "原书",
    "页码",
    "底本",
    "录入",
    "刊印",
    "出版说明",
    "版本考",
    "责任编辑",
)
EDITORIAL_PASSAGE_MARKERS = (
    "本电子版是",
    "本电子版整理者",
    "本《例言》",
    "编辑方针编集",
    "——整理者注",
)


def write_jsonl_atomic(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(path)


def choose_short_quotes(text: str, limit: int = 4) -> list[str]:
    if any(marker in (text or "")[:500] for marker in EDITORIAL_PASSAGE_MARKERS):
        return []
    candidates: list[tuple[int, int, str]] = []
    for match in SENTENCE_RE.finditer(text or ""):
        candidate = match.group(0).strip()
        length = len(canonical(candidate))
        if not 14 <= length <= 180:
            continue
        if structural_reason(candidate):
            continue
        if cjk_ratio(candidate) < 0.25:
            continue
        if any(marker in candidate for marker in EDITORIAL_MARKERS):
            continue
        if re.search(r"根据.{0,40}(出版社|报|刊|手稿)", candidate):
            continue
        if re.search(r"(?:一九|二〇|19|20)\d{2}年.{0,20}(出版|刊|印)", candidate):
            continue
        # Page-level passages often begin with a sentence continued from the previous page.
        if match.start() == 0:
            continue
        # Prefer complete, information-rich sentences without favoring very long text.
        punctuation_bonus = 20 if candidate[-1:] in "。！？!?；;" else 0
        score = punctuation_bonus + min(length, 90)
        candidates.append((score, -match.start(), candidate))
    selected = sorted(candidates, reverse=True)[:limit]
    return [candidate for _, _, candidate in sorted(selected, key=lambda row: -row[1])]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("passages_jsonl", type=Path)
    parser.add_argument("results_jsonl", type=Path)
    parser.add_argument("manifest_json", type=Path)
    parser.add_argument("output_jsonl", type=Path)
    args = parser.parse_args()

    passages = {row["passage_id"]: row for row in iter_jsonl(args.passages_jsonl)}
    results = {row["passage_id"]: row for row in iter_jsonl(args.results_jsonl)}
    manifest = {
        row["pdf_id"]: row
        for row in read_json(args.manifest_json, {"files": []}).get("files", [])
    }
    quote_rows = []
    skipped_without_sentence = 0
    for passage_id in sorted(passages):
        result = results.get(passage_id, {})
        if result.get("status") != "quote_verified":
            continue
        passage = passages[passage_id]
        verified_text = result.get("verified_text") or passage.get("text", "")
        quote_texts = choose_short_quotes(verified_text)
        if not quote_texts:
            skipped_without_sentence += 1
            continue
        source = manifest.get(passage["pdf_id"], {})
        for quote_text in quote_texts:
            display_text = re.sub(r"\s+", " ", quote_text).strip()
            display_text = re.sub(r"(?<=[\u3400-\u9fff]) (?=[\u3400-\u9fff])", "", display_text)
            quote_rows.append(
                {
                    "quote_id": f"quote-{len(quote_rows) + 1:06d}",
                    "passage_id": passage_id,
                    "quote_text": display_text,
                    "source_text": quote_text,
                    "whitespace_normalized": display_text != quote_text,
                    "work": source.get("work") or passage.get("work"),
                    "volume": source.get("volume") or passage.get("volume"),
                    "date_range": source.get("date_range") or passage.get("date_range"),
                    "edition": source.get("edition") or passage.get("edition"),
                    "pdf_id": passage["pdf_id"],
                    "filename": source.get("filename") or passage.get("filename"),
                    "page": result.get("verified_page") or passage.get("page"),
                    "paragraph": result.get("verified_paragraph") or passage.get("paragraph"),
                    "language": source.get("language") or passage.get("language"),
                    "quote_status": "quote_verified",
                    "verification_method": result.get("verification_method"),
                    "verified_at": result.get("verified_at"),
                }
            )
    write_jsonl_atomic(args.output_jsonl, quote_rows)
    print(
        f"verified_passages={sum(r.get('status') == 'quote_verified' for r in results.values())} "
        f"quotes={len(quote_rows)} skipped_without_sentence={skipped_without_sentence}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
