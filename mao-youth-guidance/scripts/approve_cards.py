"""Mark the current reviewed card set approved at the user's explicit request."""
from __future__ import annotations

import sys
from pathlib import Path

from common import read_json, write_json


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: approve_cards.py <thought_cards_json>")
        return 2
    path = Path(sys.argv[1])
    data = read_json(path, {})
    cards = data.get("cards", [])
    for card in cards:
        card["review_status"] = "approved"
        card["approval_note"] = "Approved directly by the user; source passages remain quote-unverified until page-level verification."
    write_json(path, data)
    print(f"approved {len(cards)} thought cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
