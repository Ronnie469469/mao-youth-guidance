from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "mao-youth-guidance" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_verified_quotes import choose_short_quotes  # noqa: E402
from compare_passage_page import agreement  # noqa: E402
from verification_common import canonical, structural_reason  # noqa: E402


class VerificationRulesTests(unittest.TestCase):
    def test_dual_extractor_comparison_ignores_layout_whitespace(self) -> None:
        score, method = agreement("实践是检验真理的标准。", "实践是检验\n真理的标准。")
        self.assertEqual(1.0, score)
        self.assertEqual("exact_canonical_substring", method)

    def test_high_noise_is_blocked_by_precheck(self) -> None:
        self.assertEqual("high_character_noise", structural_reason("��□■��□■��□■��□■��□■"))

    def test_table_of_contents_is_not_a_quote_candidate(self) -> None:
        self.assertEqual("table_of_contents", structural_reason("调查研究..............12"))

    def test_editorial_passage_produces_no_quotes(self) -> None:
        text = "本电子版是整理本。这里说明版式。——整理者注"
        self.assertEqual([], choose_short_quotes(text))

    def test_line_wrap_does_not_split_a_sentence(self) -> None:
        text = "页首承接上页的一句话。认识来源于社会\n实践，并且要回到实践中接受检验。"
        self.assertEqual(
            ["认识来源于社会\n实践，并且要回到实践中接受检验。"],
            choose_short_quotes(text),
        )


class BuiltKnowledgeBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.kb = ROOT / "knowledge-base" / "v2"
        cls.manifest = json.loads((cls.kb / "manifest.json").read_text(encoding="utf-8"))
        cls.passages = [
            json.loads(line)
            for line in (cls.kb / "passages.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]
        cls.quotes = [
            json.loads(line)
            for line in (cls.kb / "verified-quotes.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]
        cls.cards = json.loads((cls.kb / "thought-cards.json").read_text(encoding="utf-8"))["cards"]

    def test_all_passages_have_final_status(self) -> None:
        self.assertEqual(24_181, len(self.passages))
        self.assertEqual(
            {"quote_verified", "paraphrase_only", "blocked"},
            {row["quote_status"] for row in self.passages},
        )
        self.assertEqual(0, self.manifest["unverified"])

    def test_quote_registry_is_exact_and_traceable(self) -> None:
        passage_by_id = {row["passage_id"]: row for row in self.passages}
        for quote in self.quotes:
            passage = passage_by_id[quote["passage_id"]]
            self.assertEqual("quote_verified", passage["quote_status"])
            self.assertIn(canonical(quote["quote_text"]), canonical(passage["verified_text"]))
            self.assertTrue(quote["pdf_id"])
            self.assertGreater(quote["page"], 0)

    def test_every_card_is_approved_and_has_a_verified_quote(self) -> None:
        quote_ids = {row["quote_id"] for row in self.quotes}
        self.assertEqual(18, len(self.cards))
        for card in self.cards:
            self.assertEqual("approved", card["review_status"])
            self.assertTrue(card["verified_quote_ids"])
            self.assertTrue(set(card["verified_quote_ids"]) <= quote_ids)


if __name__ == "__main__":
    unittest.main()
