# Naming Boundaries

This document separates three different meanings that were previously being referred to with the same name.

Its purpose is to reduce communication errors in architecture, documentation, and product presentation.

## 1. TCRIA Theory

This refers to the conceptual foundation that may have inspired the project.

It is not the default meaning for software documentation in this repository.

Repository rule:

- do not use theory language to describe implemented product behavior;
- keep conceptual background separate from software specification;
- treat theory as context, not as proof of implemented capability.

## 2. TCRIA Core

This refers to the reusable engine or shared analysis components.

Typical responsibilities may include:

- ingestion support;
- text and metadata extraction;
- signal detection;
- evidence correlation;
- rule-aware evaluation support.

Repository rule:

- use `Core` when referring to reusable analysis mechanisms;
- do not confuse `Core` with a full product surface;
- document Core responsibilities separately from UI, API, or reporting surfaces.

## 3. Product

This refers to a concrete application built for a specific use case.

For the current repository, that concrete application is:

- document batch compliance review.

Repository rule:

- product documentation must describe concrete users, inputs, outputs, task flow, and limits;
- the current product should be described through one primary workflow;
- product claims must stay tied to implemented or scoped behavior.

## Repository Guidance

When writing or reviewing repository material, first identify which layer is being described:

1. theory;
2. core engine;
3. concrete product.

If the text mixes these layers, it should be rewritten.

## Current Working Assumption

This repository currently prioritizes one product definition:

`document batch review`

It may later extract or formalize a reusable `TCRIA Core`, but the repository should not assume that every mention of `TCRIA` refers to theory, engine, and product at the same time.
