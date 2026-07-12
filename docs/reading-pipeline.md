# Reading Pipeline

This document defines how TCRIA should handle document reading when OCR is available as an optional fallback.

The purpose is to make reading behavior explicit, predictable, and visible in the report.

## Core Rule

TCRIA should prefer direct text extraction first.

OCR should be used only as a fallback for PDFs when direct extraction does not produce usable text.

## Reading Sequence

For PDF inputs, the intended sequence is:

1. attempt direct text extraction;
2. if usable text is found, keep the direct extraction result and do not run OCR;
3. if no text is found or extraction fails, attempt OCR automatically;
4. if OCR succeeds, mark the document as read by OCR fallback;
5. if OCR fails, record that failure explicitly.

For non-PDF inputs, OCR is normally not applicable unless a later product decision defines otherwise.

## Required Reading States

At minimum, the reading layer should expose:

- `direct_text`: text came from direct extraction and OCR was not needed;
- `ocr_text`: text came from OCR fallback after direct extraction was insufficient;
- `ocr_failed`: direct extraction was insufficient and OCR also failed;
- `not_applicable`: OCR was not relevant for that file type.

## Reporting Rule

The final report must never hide how the text was obtained.

For each relevant document, the system should expose:

- reading method used;
- OCR status;
- reading confidence when available;
- whether the text came from direct extraction or OCR fallback.

At batch level, the report should also expose totals for:

- text extracted directly;
- text obtained by OCR;
- OCR failures.

## Confidence Rule

When the reading layer can estimate quality or confidence, that signal should be carried forward.

Examples:

- `high`
- `medium`
- `low`
- `unknown`

Confidence is a reading-quality signal.

It is not the same as legal certainty or compliance certainty.

## Product Boundary

This repository now defines the OCR fallback policy and the required output transparency.

It does not yet claim that the full production ingestion engine is implemented here.
