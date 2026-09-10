"""Export a compact Markdown review sheet from thought-card JSON."""
from __future__ import annotations

import sys
from pathlib import Path

from common import read_json


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: export_review.py <thought_cards_json> <markdown_output>")
        return 2
    source, output = map(Path, sys.argv[1:])
    data = read_json(source, {})
    lines = ["# Thought card review", "", "Edit the JSON for machine-stable fields; approve only after checking the rendered source.", ""]
    for card in data.get("cards", []):
        lines.extend([
            f"## {card.get('thought_id')} - {card.get('title')}",
            f"- 主题：{'、'.join(card.get('themes', []))}",
            f"- 来源：{'、'.join(card.get('source_passages', []))}",
            f"- 核心命题：{card.get('core_proposition', '')}",
            f"- 可迁移方法：{card.get('transferable_method', '')}",
            f"- 时代边界：{card.get('period_bound_claims', '')}",
            f"- 局限/反例：{card.get('limitations', '')}",
            f"- 审核状态：{card.get('review_status', 'draft')}", "",
        ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"exported {len(data.get('cards', []))} review cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
