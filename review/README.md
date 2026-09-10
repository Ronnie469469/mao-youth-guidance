# Review workflow

1. Confirm `pdf-mapping-candidates.md` and maintain `pdf-mapping.json`.
2. Inspect rendered source pages for OCR quality.
3. Edit `thought-cards-draft.json` or the companion Markdown.
4. Set only source-grounded cards to `approved`.
5. Run `verify_passages.py` before promotion.

An approved card must contain a human-written core proposition, historical context, transferable method, period-bound claims, modern translation, limitations, and source passage IDs. Heuristic placeholders are not approval-ready.
