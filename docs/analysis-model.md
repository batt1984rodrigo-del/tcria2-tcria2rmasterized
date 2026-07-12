# Analysis Model

This document defines how TCRIA should evaluate document batches for compliance review.

See also: [Governance Profiles](governance-profiles.md)

## Core Rule

TCRIA must separate document reading from risk judgment.

The system should first process and register what is present in the material. Judgment should happen afterward, using explicit analysis rules.

For the MVP, these rules serve one workflow only: document batch compliance review.

## Processing Sequence

The minimum evaluation sequence is:

1. receive the user-defined scope;
2. extract text, metadata, and detectable structure;
3. record gaps, imperfections, and unreadable portions;
4. derive findings and evidence links;
5. apply the configured review rules;
6. produce graded results instead of default pass/fail blocking.

## Operational Rules

The Core should follow these rules:

1. read as much as possible before judging;
2. do not discard a document only because it is imperfect;
3. record imperfections as findings or risk signals;
4. separate source facts from inference;
5. expose what was read and what could not be read;
6. keep conclusions linked to evidence;
7. allow graded severity instead of binary approval logic.

## Review Rules

The system must apply explicit compliance review rules when judging findings.

For the MVP, the repository should assume one primary review workflow. Different profile families can exist later, but they should not redefine the product description now.

The rules still need to be visible in the output. A flagged point should always be traceable to:

- what was detected;
- which rule was applied;
- which evidence supports the point;
- how severe the issue is;
- what remains uncertain.

The main purpose of these rules is to determine whether the analyzed material shows signs of compliance, nonconformity, or missing support for a compliance conclusion.

## Minimum Evaluation Scales

The system should support scales such as:

- responsible party status: identified, not identified, partial, inferred, not applicable;
- accountability risk: low, medium, high, critical;
- conformity status: compliant, partially compliant, noncompliant, inconclusive;
- confidence: high, medium, low;
- impact: informational, attention, relevant, severe.

These scales can be adjusted later, but the repository should assume graded evaluation as a product requirement for the current workflow.

## Output Requirement

When a point is flagged, the output should indicate:

- which rule or policy was used;
- what condition triggered the flag;
- what evidence supports it;
- what remains uncertain about the point.

## AI Assistance Boundary

AI assistance can support:

- explanation of findings;
- executive summarization;
- comparison of evidence;
- suggestion of next steps;
- support for severity phrasing.

AI assistance should not replace:

- source extraction;
- evidence registration;
- declared rule application;
- traceability of conclusions.
