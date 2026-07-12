# Repository Scope

This document defines the repository's working scope and decision criteria.

Its purpose is to keep the repository objective: one product, one primary task, clear boundaries.

## Repository Objective

This repository exists to define and implement a document analysis product focused on compliance review, with:

- explicit inputs;
- bounded processing scope;
- reproducible outputs;
- clear architectural responsibilities.

Current primary task:

`receive one bounded company document batch and generate one structured compliance review report`

## Product Scope

The product scope currently includes:

- document ingestion;
- document parsing and preprocessing;
- signal extraction;
- evidence organization;
- rule-based evaluation and scoring;
- structured compliance review report generation;
- operator-facing review outputs.

The product scope currently does not include:

- unrestricted environment monitoring;
- autonomous institutional decision-making;
- unbounded interpretation without source reference;
- claims that exceed available evidence;
- multiple product lines inside the same MVP.

## Repository Rules

### 1. Define the system concretely

Every major document should answer these questions directly:

- what document batch enters the system;
- what happens to that batch;
- what compliance review report leaves the system;
- who uses the result;
- what remains outside the system.

### 2. Prefer capabilities over slogans

Product language in the repository should describe capabilities, the current task, and its boundaries, not broad conceptual positioning.

If a sentence does not help define the current workflow, it should be removed or moved out of the main product docs.

### 3. Separate implementation layers early

The repository should distinguish:

- ingestion and preprocessing;
- analysis and correlation;
- policy and scoring;
- output composition;
- delivery surfaces such as CLI, API, or UI.

### 4. Treat output as a functional requirement

Report quality is not a branding concern only. It is part of the system specification because the output is one of the product's main deliverables.

### 5. Keep scope claims bounded

If a capability is not implemented or not technically defined yet, it should not be described as current product behavior.

### 6. Separate theory, core, and product references

The repository should not use the same term interchangeably for:

- conceptual foundation;
- reusable engine;
- concrete application.

These layers must be named explicitly whenever the distinction matters.

## Immediate Repository Priorities

- define the MVP in concrete terms;
- identify reusable components from prior versions;
- formalize the single report output requirement;
- formalize the client-facing report formatting requirement;
- define the minimum architecture needed to support those requirements;
- keep repository language aligned with implemented or planned functionality.

## Working Definition

Current repository definition:

`TCRIA is a document batch compliance review system that processes a bounded set of company documents and generates one structured compliance review report based on extracted signals, correlated evidence, explicit review rules, and report composition rules.`
