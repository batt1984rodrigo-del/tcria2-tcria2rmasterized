# TCRIA

**Document compliance review that turns evidence into a clear, auditable decision recommendation.**

TCRIA receives a bounded batch of company documents, reads and organizes the available evidence, identifies compliance risks and produces a structured report showing:

- what was confirmed;
- what is missing or inconsistent;
- which risks require attention;
- which evidence supports each finding;
- what decision is recommended;
- what must still be validated by a responsible professional.

> TCRIA does not replace legal, compliance, audit or management authority. It supports the responsible person with an evidence-linked recommendation and a reviewable decision trail.

## For prospective clients

TCRIA is designed for organizations that need to make a decision from a controlled document batch without losing the connection between the decision and its evidence.

A pilot may be used to review, for example:

- supplier qualification documents;
- procurement or contracting records;
- accountability and governance files;
- policy and procedure evidence;
- internal control documentation;
- a bounded set of contracts, certificates or declarations.

### What the client provides

One clearly defined document batch, together with the decision or review question.

Example question:

> Based on the submitted documents, should this supplier be approved, approved with conditions, or held for further review?

### What TCRIA returns

One client-facing compliance review report containing:

1. scope and documents reviewed;
2. reading quality and OCR provenance;
3. confirmed facts;
4. missing, expired or inconsistent evidence;
5. findings linked to document references;
6. risk and conformity assessment;
7. recommended decision;
8. conditions, limits and required human validation;
9. next review priorities.

## How TCRIA shows what decision to take

TCRIA does not produce an unexplained answer. It builds a decision path.

```text
Submitted documents
        ↓
Validation and document inventory
        ↓
Direct extraction and OCR fallback
        ↓
Comparable facts and document relationships
        ↓
Cross-document correlation, patterns and timeline
        ↓
Facts, gaps and investigation signals
        ↓
Compliance findings linked to evidence
        ↓
Decision recommendation with conditions
        ↓
Human review and final institutional decision
```

A recommendation may be expressed as:

- **PROCEED** — available evidence supports continuation;
- **PROCEED WITH CONDITIONS** — continuation is possible after stated corrective actions;
- **HOLD FOR REVIEW** — material evidence is missing, inconsistent or requires responsible review;
- **DO NOT PROCEED YET** — the submitted batch contains unresolved critical issues.

Each recommendation must explain **why**, identify the supporting evidence and state its limitations.

## Example client scenario

**Review question:** Should a supplier be approved based on the submitted qualification batch?

**Illustrative result:**

> **Recommended decision: PROCEED WITH CONDITIONS**
>
> The submitted batch supports preliminary supplier qualification, but the tax clearance certificate is expired and the beneficial ownership declaration was not found. Approval should remain conditional until updated evidence is submitted and validated.

**Evidence trail:**

- corporate registration: found and readable;
- insurance certificate: valid at the review date;
- tax clearance certificate: found, but expired;
- beneficial ownership declaration: not found in the submitted batch;
- OCR limitation: one scanned page has low confidence and requires visual confirmation.

This example is illustrative and does not represent a legal or institutional decision.

## Client pilot

The recommended next step is a controlled pilot using fictional, sanitized or contractually authorized documents.

See:

- [Client Pilot Guide](docs/client-pilot.md)
- [Example Decision Recommendation](examples/client-decision-example.md)
- [Example PDF Report](output/pdf/tcria-compliance-report-example.pdf)

## Report Preview

Example client-facing output:

![Compliance report preview - page 1](docs/images/tcria-compliance-report-example-1.png)

![Compliance report preview - page 2](docs/images/tcria-compliance-report-example-2.png)

## Primary Task

TCRIA exists to do one main job:

- receive a bounded document batch;
- extract relevant content and signals;
- correlate documents that belong to the same subject, process or event;
- compare dates, values, deadlines, statuses, responsible parties and approvals;
- identify pattern breaks and impossible temporal sequences;
- identify compliance and conformity issues;
- organize findings and evidence;
- generate a structured compliance review report with a decision recommendation.

## Primary Input

The primary input is:

- one bounded document batch submitted for review;
- one defined review or decision question.

The batch may come from a folder, upload or workspace, but that packaging detail does not define a different product.

## Primary Output

The primary output is one structured compliance review report containing:

- formatted client-facing presentation;
- scope summary;
- compliance findings;
- evidence references;
- conformity gaps or unresolved points;
- recommended decision and rationale;
- conditions and escalation points;
- unresolved items or limits;
- next review priorities.

## MVP Boundaries

The current repository foundation assumes:

1. the user submits a bounded document batch for review;
2. the system analyzes documents, not an entire company or environment;
3. the system recommends a decision, but does not issue the final institutional, legal or management decision;
4. document reading and risk judgment are separate steps;
5. imperfect documents are flagged, not automatically discarded;
6. every material recommendation should be linked to evidence or explicitly marked as unresolved;
7. the MVP is centered on one compliance review workflow, not multiple products.

## Documentation Map

- [Client Pilot Guide](docs/client-pilot.md)
- [Repository Scope](docs/repository-constitution.md)
- [Naming Boundaries](docs/naming-boundaries.md)
- [Product Definition](docs/product-vision.md)
- [Analysis Model](docs/analysis-model.md)
- [Reading Pipeline](docs/reading-pipeline.md)
- [Governance Profiles](docs/governance-profiles.md)
- [Integration Readiness](docs/integration-readiness.md)
- [Legacy Output Lessons](docs/legacy-output-lessons.md)
- [Legacy Adapter Contract](docs/legacy-adapter-contract.md)
- [Output Specification](docs/output-philosophy.md)
- [Output Taxonomy](docs/output-taxonomy.md)
- [Report Contract](docs/report-contract.md)
- [Report Template](docs/report-template.md)
- [Architecture Layers](docs/architecture/layers.md)
- [Non-Goals](docs/non-goals.md)
- [Contributing](CONTRIBUTING.md)

## Local secret placeholder

This repository now reserves a local placeholder for future OpenAI integration.

1. Copy `.env.example` to `.env`.
2. Fill `OPENAI_API_KEY` only in your local file or environment.
3. Never commit real keys or other secrets to the repository.

The current repository does not use this key automatically yet; the placeholder exists only to prepare a safe configuration path.

## Current Repository Focus

The current work in this repository is to define TCRIA objectively as a product:

- what document batch enters the system;
- which decision question is being reviewed;
- how the batch is processed;
- how direct extraction and OCR fallback are exposed to the user;
- how facts, gaps and risks are separated;
- how a recommended decision is justified by evidence;
- what the compliance review report must contain;
- how imperfect material is handled;
- what requires human validation;
- what remains outside the MVP.
