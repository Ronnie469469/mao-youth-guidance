# Source policy

The raw corpus is immutable input. Every file is registered by SHA-256, page count, PDF metadata, extraction method, OCR quality, source/version details, and mapping status.

## Passage states

`unmapped -> mapped -> text_extracted -> automatic_crosscheck -> quote_verified`

Final passage states are `quote_verified`, `paraphrase_only`, and `blocked`. An OCR or metadata problem adds `ocr_flagged`; an invalid or unreliable passage is `blocked` with `retry: false`. Only exact short text registered in `verified-quotes.jsonl` may be quoted verbatim. Only `approved` thought cards may drive the core interpretation layer.

For knowledge-base v2, `quote_verified` means the indexed text agreed with an independent PDF text extractor and the corresponding cached page render was present and nonblank. This is conservative automated source-layer verification, not a claim that a person visually proofread every page. OCR-required files remain unavailable for quotation until a later OCR-and-page-review run.

## Offline-first invariant

Preprocessing creates the dictionaries, thought cards, concept relations, and page index. Runtime retrieval reads those artifacts and does not perform fresh ideological synthesis from raw PDFs. Regenerate the knowledge base only through an explicit maintenance command and a new version directory.

## Evidence layers

1. Mao's primary texts: core evidence.
2. Historical scholarship and official bibliographic material: context, variants, and provenance.
3. Contemporary statistics, policy, and reporting: present facts; record source and retrieval date separately.

Never present layer 2 or 3 as Mao's view.
