"""Shared helpers for the offline corpus pipeline."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def language_hint(text: str) -> str:
    """Return a conservative language hint without rewriting source text."""
    if not text.strip():
        return "unknown"
    japanese = sum(0x3040 <= ord(ch) <= 0x30ff for ch in text)
    latin = sum(("a" <= ch.lower() <= "z") for ch in text)
    cjk = sum(0x3400 <= ord(ch) <= 0x9fff for ch in text)
    if japanese >= 3:
        return "ja"
    if cjk >= 3:
        return "zh"
    if latin >= 10:
        return "en"
    return "other"


def jsonl_write(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
