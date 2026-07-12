# Governance Profiles

This document defines the governance profiles that can be applied to the same TCRIA product workflow.

The product does not become a different system for each profile.

The workflow remains the same:

`bounded company document batch -> compliance analysis -> structured compliance review report`

What changes is the strictness of the review rules.

## Core Rule

Profiles do not change the product.

Profiles change the review threshold.

That means:

- the same batch can be reviewed under different rule intensity;
- the same finding can be classified differently depending on the profile;
- the output must state which profile was used.

## Profile Model

Each governance profile should define:

- review objective;
- control strictness;
- severity thresholds;
- conformity expectations;
- wording expectations in the final report.

## Official Profiles

### 1. Baseline Compliance

This should be treated as the default product profile for the current MVP.

Purpose:

- determine whether the submitted batch supports a reasonable compliance conclusion;
- identify conformity gaps;
- flag missing support without over-blocking the whole batch.

Behavior:

- reads imperfect material when possible;
- records missing support as a finding;
- uses graded severity instead of binary blocking by default;
- favors operational clarity over punitive language.

Best use:

- standard business compliance review;
- first-pass review of internal document batches;
- client-facing reporting in normal operating conditions.

### 2. Strict Governance

This profile applies a stronger standard for traceability, accountability, and formal support.

Purpose:

- test whether the batch meets a stricter governance expectation;
- highlight formal gaps that may be acceptable in a softer review but not under stronger control requirements.

Behavior:

- raises the severity of missing approvals and missing traceability more quickly;
- expects stronger support for ownership, authorization, and process integrity;
- exposes formal weaknesses with less tolerance.

Best use:

- mature internal control environments;
- audits of high-risk processes;
- executive review where documentation discipline is expected.

### 3. Exploratory Review

This profile is softer and more diagnostic.

Purpose:

- understand the condition of a document batch before demanding full maturity;
- surface signals without treating every imperfection as a compliance failure.

Behavior:

- prioritizes reading and signal discovery;
- keeps severity more conservative when evidence is partial;
- distinguishes weak support from confirmed nonconformity.

Best use:

- first contact with disorganized batches;
- early-stage review before formal escalation;
- internal triage.

## Current MVP Position

For the current repository, the main product promise should stay centered on:

`Baseline Compliance`

Other profiles may exist, but they should be documented as stricter or softer rule packs within the same workflow, not as separate products.

## Output Requirement

Every client-facing report should state:

- which governance profile was applied;
- why that profile was used;
- how that profile influenced classification severity.

## Classification Guidance

When profile choice materially changes the interpretation of a point, the report should say so clearly.

Example:

`Under the applied profile, this issue was classified as Relevant because approval support is missing. Under a softer review profile, the same point might appear as an Attention finding rather than a stronger conformity gap.`

## Repository Guidance

When adding or changing a profile:

1. define the objective first;
2. define the stricter or softer rule changes second;
3. define how the report language should change third;
4. avoid creating profiles that are actually different products in disguise.
