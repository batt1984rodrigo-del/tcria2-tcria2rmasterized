# Coverage And Provenance

This document defines what the legacy migration summary is allowed to say and where each statement comes from.

The goal is operational clarity.

The goal is not legal interpretation.

## Scope

The current adapter phase is intentionally narrow:

- it reads a sanitized legacy JSON sample;
- it translates technical fields into a human-readable Markdown summary;
- it shows coverage, outcomes, classifications, and extracted signals;
- it does not re-run the old engine;
- it does not create an API;
- it does not create deploy logic;
- it does not replace the executive report that will exist later.

## Coverage Model

The Markdown summary is a coverage report.

That means it answers questions such as:

- how many files were scanned;
- how many were readable;
- how many were unreadable or weakly readable;
- which classifications appeared;
- which outcome states appeared;
- which signal families were detected.

It does not answer whether a case is legally valid.

It does not decide guilt, fraud, or liability.

## Provenance Rules

Every visible section in the generated Markdown should map back to legacy fields:

- batch overview comes from top-level batch metadata;
- reading coverage comes from `extraction_status`, `text_quality`, `extractable_text_chars`, `reading_method`, `ocr_status`, and `reading_confidence`;
- classifications come from `classification_counts` or equivalent per-document derivation;
- outcomes come from `overall_outcome` and gate statuses;
- document map comes from per-document fields such as `file_name`, `classification`, and `gates`;
- signal highlights come from `key_signals`.

If a field is not present in the legacy source, the adapter should not invent a stronger conclusion.

## Translation Guardrails

The adapter is allowed to translate technical state into reader-facing language.

It is not allowed to distort meaning.

Examples:

- `BLOCKED` means processing or decision constraints remain; it does not mean the document is useless;
- `NOT_EVALUATED` means the gate did not close; it does not mean the document failed;
- `WARN` means the reading carries a caution flag; it does not mean there is no useful signal.
- `ocr_failed` means OCR fallback did not recover usable text; it does not mean the document is irrelevant forever.

## Sanitization Rule

The example files and the generated summary must remain sanitized.

They must not include:

- real people;
- real banks;
- real identifiers;
- real statements or extracts;
- real legal evidence;
- sensitive enterprise documents.

## Current Repository Contract

For this migration step, the repository treats the flow as:

`sanitized legacy JSON -> Markdown coverage summary`

Later phases may add richer rendering layers.

This phase exists to stabilize the bridge first.
