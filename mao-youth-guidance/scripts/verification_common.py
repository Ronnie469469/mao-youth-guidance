"""Shared rules for conservative passage verification."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Iterable

FINAL_STATES = {"quote_verified", "paraphrase_only", "blocked"}
STRUCTURAL_MARKERS = (
    "目录", "目 录", "出版说明", "编者按", "责任编辑", "版权所有",
    "isbn", "contents", "索引", "附录", "注释",
)


def canonical(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("\u3000", " ").replace("\ufeff", "")
    return re.sub(r"\s+", "", text).lower()


def cjk_ratio(text: str) -> float:
    compact = canonical(text)
    if not compact:
        return 0.0
    cjk = sum(0x3400 <= ord(ch) <= 0x9FFF for ch in compact)
    return cjk / len(compact)


def noise_ratio(text: str) -> float:
    compact = canonical(text)
    if not compact:
        return 1.0
    allowed = sum(
        ch.isalnum() or 0x3400 <= ord(ch) <= 0x9FFF
        or ch in "，。！？；：、“”‘’（）《》〈〉—…·,.!?;:()[]-"
        for ch in compact
    )
    replacement = compact.count("�") + compact.count("□") + compact.count("■")
    return min(1.0, 1 - allowed / len(compact) + replacement / len(compact))


def structural_reason(text: str) -> str | None:
    stripped = text.strip()
    compact = canonical(text)
    if not stripped:
        return "empty_text"
    if len(compact) < 14:
        return "too_short_for_reliable_quote"
    if any(marker in stripped[:180].lower() for marker in STRUCTURAL_MARKERS):
        return "front_matter_or_reference_material"
    if stripped.count("……") >= 2 or re.search(r"\.{8,}\s*\d+", stripped):
        return "table_of_contents"
    if re.fullmatch(r"[\d一二三四五六七八九十百〇○年月日卷册第\s.·—-]+", stripped):
        return "page_number_or_date_only"
    if noise_ratio(text) > 0.12:
        return "high_character_noise"
    return None


def iter_jsonl(path: Path) -> Iterable[dict]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_results(path: Path) -> dict[str, dict]:
    return {row["passage_id"]: row for row in iter_jsonl(path)}
