# Architecture Layers

This document defines the main system layers for the current product workflow.

Current workflow:

`bounded document batch -> analysis -> structured review report`

## Layer 1: Ingestion and Preprocessing

This layer receives the bounded document batch and prepares it for analysis.

Responsibilities include:

- file discovery or upload intake;
- format normalization;
- text extraction;
- metadata capture;
- preprocessing for downstream analysis.

## Layer 2: Analysis and Correlation

This layer processes the prepared material and derives structured results.

Responsibilities include:

- signal extraction;
- classification;
- cross-document correlation;
- finding generation;
- evidence linking.

## Layer 3: Policy and Scoring

This layer applies the configured review rules to analysis results.

Responsibilities include:

- evaluation rules;
- severity mapping;
- confidence grading;
- accountability classification;
- rule thresholds.

## Layer 4: Output Composition

This layer converts analysis results into consistent deliverables.

Responsibilities include:

- report assembly;
- findings ordering;
- evidence referencing;
- summary generation;
- document structure and formatting;
- client-facing template application;
- limitation exposure.

## Layer 5: Delivery Surfaces

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
- Analysis and Correlation;
- Policy and Scoring;
- Output Composition;
- Delivery Surfaces.
