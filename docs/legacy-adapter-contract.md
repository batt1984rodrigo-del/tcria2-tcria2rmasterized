# Legacy Adapter Contract

This document defines how legacy TCRIA audit output should enter the remodeled repository.

Reference artifacts:

- legacy sample input: [../examples/legacy/sanitized-strict-audit.json](../examples/legacy/sanitized-strict-audit.json)
- adapted Markdown example: [../output/legacy/legacy-audit-summary.md](../output/legacy/legacy-audit-summary.md)
- coverage and provenance notes: [./coverage-and-provenance.md](./coverage-and-provenance.md)

## Core Rule

Legacy output enters through translation.

The official path is:

`legacy JSON -> normalizer -> structured Markdown`

The repository should not import the old engine wholesale as the first integration step.

## Adapter Objective

The first adapter is not responsible for re-running the old logic.

Its responsibility is to:

- read a legacy audit JSON payload;
- extract the operational and review-relevant information;
- reorganize it into a human-readable coverage summary;
- keep the result objective and suitable for compliance-oriented reading.

## Input Contract

The adapter accepts a legacy audit payload shaped like the older TCRIA outputs.

Expected top-level fields for the sanitized batch sample include:

- `generated_at`
- `audit_basis`
- `input_path`
- `mode`
- `compliance_gate_mode`
- `total_files_scanned`
- `accusation_set_count`
- `classification_counts`
- `route_counts`
- `document_role_counts`
- `accusation_set`
- `non_accusation_set`

The adapter must tolerate partial legacy payloads as long as enough structure exists to summarize the batch.

## Legacy Item Contract

Legacy items may contain fields such as:

- `file_name`
- `file_path`
- `classification`
- `summary`
- `overall_outcome`
- `classification_reasons`
- `text_quality`
- `extraction_status`
- `reading_method`
- `ocr_status`
- `reading_confidence`
- `gates`
- `interpretation`
- `key_signals`

Not every field is required for every item.

The adapter should degrade gracefully when some fields are missing.

## Normalization Goals

The normalizer should produce a simpler summary model with concepts such as:

- files read;
- files unreadable or empty;
- partially usable files;
- files with insufficient text;
- direct extraction counts;
- OCR fallback counts;
- OCR failure counts;
- classification totals;
- document outcomes;
- gate warnings and not-evaluated states;
- document-level coverage map;
- aggregated technical signals.

## Main Output Contract

The adapter must generate:

1. a human-readable Markdown report.

The adapted report should:

- explain the legacy batch in plain language;
- make coverage visible before interpretation;
- make the reading method visible before interpretation;
- preserve uncertainty and limitations;
- act as a migration bridge, not as the final executive report.

## Non-Goals

The adapter should not:

- recreate the entire legacy engine;
- preserve every old field in the main narrative;
- present raw gate dumps as the primary reading experience;
- claim that the adapted report replaces the original technical artifact.

## Relationship To The Legacy JSON

The original legacy JSON remains a technical source artifact.

The adapted Markdown becomes the reader-oriented migration output for this phase.

That means:

- source truth for machine detail stays in the legacy JSON;
- source truth for client communication moves into the adapted report.

## Repository Guidance

When future legacy formats appear, extend the adapter through:

- input normalization;
- compatibility mapping;
- output translation.

Do not widen the repository by copying entire legacy stacks unless a later architectural step justifies it.
