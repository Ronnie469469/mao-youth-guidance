# Mao Youth Guidance corpus

Put the numbered source PDFs in `raw/` and keep their original filenames. The pipeline never edits `raw/`.

## Offline pipeline

Run from the repository root with the bundled Python runtime:

```powershell
$env:PYTHONUTF8 = '1'
$py = 'C:\Users\lhn18\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py mao-youth-guidance/scripts/inspect_pdfs.py mao-corpus/raw mao-corpus/source-manifest.json
& $py mao-youth-guidance/scripts/identify_pdfs.py mao-corpus/raw mao-corpus/source-manifest.json review
```

Review `review/pdf-mapping-candidates.md`, then create `review/pdf-mapping.json` using the schema in `metadata/mapping.schema.json`. Only confirmed mappings may be used as formal citations. Apply confirmed records with `apply_mapping.py`.

```powershell
& $py mao-youth-guidance/scripts/extract_text.py mao-corpus/raw mao-corpus/source-manifest.json mao-corpus/extracted
& $py mao-youth-guidance/scripts/normalize_text.py mao-corpus/extracted mao-corpus/normalized/pages
& $py mao-youth-guidance/scripts/apply_mapping.py mao-corpus/source-manifest.json review/pdf-mapping.json
& $py mao-youth-guidance/scripts/build_index.py mao-corpus/normalized/pages review/pdf-mapping.json mao-corpus/index/passages.jsonl
& $py mao-youth-guidance/scripts/build_thought_drafts.py mao-corpus/index/passages.jsonl review/pdf-mapping.json review
```

Edit and approve the draft cards in `review/thought-cards-draft.json`, then promote them into a new version directory with `apply_review.py`.
