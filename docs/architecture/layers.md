# Architecture Layers

This document defines the main system layers for the current product workflow.

Current workflow:

`bounded document batch -> reading -> correlation -> investigation -> structured review report`

## Layer 1: Ingestion and Preprocessing

This layer receives the bounded document batch and prepares it for analysis.

Responsibilities include:

- file discovery or upload intake;
- format normalization;
- direct text extraction;
- OCR fallback for PDFs when direct extraction is insufficient;
- reading-method provenance capture;
- reading confidence capture when available;
- metadata capture;
- preprocessing for downstream analysis.

## Layer 2: Comparable Fact Preparation

This layer converts different document types into a common comparison shape.

Responsibilities include:

- signal extraction;
- subject and entity identification;
- date, value, deadline and status normalization;
- responsible party and approval extraction;
- reference and process-step capture.

## Layer 3: Correlation and Patterns

This layer compares only documents with a confirmed relationship or an explicit
pattern group.

Responsibilities include:

- grouping by contract, supplier, process, event, period or operation;
- date, value, deadline, status, responsibility and approval comparison;
- missing-reference detection;
- temporal-sequence validation;
- pattern and procedure outlier detection;
- generation of evidence-linked investigation signals;
- explanation of what a professional should verify next.

The correlation layer looks for relevant divergence. It does not declare an
error, assign intent or make a final institutional decision.

## Layer 4: Investigation and Analysis

This layer converts correlated facts and signals into reviewable investigative
reasoning.

Responsibilities include:

- hypothesis formation;
- contradiction and gap review;
- finding generation;
- evidence linking;
- separation between what can and cannot yet be affirmed.

## Layer 5: Policy and Scoring

This layer applies the configured review rules to analysis results.

Responsibilities include:

- evaluation rules;
- severity mapping;
- confidence grading;
- accountability classification;
- rule thresholds.

## Layer 6: Output Composition

This layer converts analysis results into consistent deliverables.

Responsibilities include:

- report assembly;
- findings ordering;
- evidence referencing;
- summary generation;
- document structure and formatting;
- client-facing template application;
- limitation exposure.

## Layer 7: Delivery Surfaces

This is how people interact with the workflow.

For the current repository, the exact interface can vary. It does not change the primary task.

It may include:

- command line execution;
- APIs;
- web interfaces;
- case workspaces;
- export surfaces.

## Repository Guidance

This repository should primarily organize software concerns around:

- Ingestion and Preprocessing;
- Comparable Fact Preparation;
- Correlation and Patterns;
- Investigation and Analysis;
- Policy and Scoring;
- Output Composition;
- Delivery Surfaces.
