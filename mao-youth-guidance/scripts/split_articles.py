"""Detect article-heading candidates while preserving review uncertainty."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from common import write_json

DATE = re.compile(r"(?:（[^）]{4,40}）|\([^)]{4,40}\)|(?:19|20)\d{2}年)")
BAD = re.compile(r"^(目录|目\s*录|注释|附录|后记|出版说明|编者按|说明|第[一二三四五六七八九十百0-9]+[卷册章]|[0-9一二三四五六七八九十百〇○·.\- ]+)$")
NOISE = re.compile(r"(页码|目录|……|\.\.\.|编者|出版社|出版|责任编辑|印刷|发行|ISBN|毛泽东选集第|毛泽东集第)")


def candidate(lines: list[str]) -> tuple[str | None, str | None]:
    cleaned = [re.sub(r"\s+", " ", x).strip() for x in lines if x.strip()]
    for index, line in enumerate(cleaned[:18]):
        line = re.sub(r"^毛泽东(?:选集|集|文稿)[^\n]{0,30}$", "", line).strip()
        if not line or BAD.match(line) or NOISE.search(line) or len(line) < 4 or len(line) > 70:
            continue
        nearby = " ".join(cleaned[index:index + 2])
        match = DATE.search(line) or DATE.search(cleaned[index + 1]) if index + 1 < len(cleaned) else DATE.search(line)
        if match:
            title = re.sub(r"[（(].*$", "", line).strip(" -*#·")
            if (3 <= len(title) <= 45 and not BAD.match(title) and not NOISE.search(title)
                    and not re.search(r"[,，。；;：:！？!?…]|\d", title)
                    and not title.startswith(("一九", "一九", "第", "页"))):
                return title, match.group(0).strip("（(")
    return None, None


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: split_articles.py <passages_jsonl> <articles_json>")
        return 2
    index_path, output_path = map(Path, sys.argv[1:])
    rows, seen = [], set()
    for raw in index_path.read_text(encoding="utf-8").splitlines():
        passage = json.loads(raw)
        title, date_hint = candidate(passage.get("text", "").splitlines())
        if not title:
            continue
        key = (passage["pdf_id"], title)
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "article_id": f"article-{len(rows) + 1:05d}",
            "title_candidate": title,
            "date_hint": date_hint,
            "pdf_id": passage["pdf_id"],
            "filename": passage["filename"],
            "collection": passage.get("work"),
            "volume": passage.get("volume"),
            "start_page_candidate": passage["page"],
            "source_passage": passage["passage_id"],
            "review_status": "draft",
        })
    write_json(output_path, {"schema": "mao-youth-guidance/article-candidates.v1", "articles": rows})
    print(f"detected {len(rows)} article-heading candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
