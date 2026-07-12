# Output Taxonomy

This document defines the official output taxonomy for TCRIA.

Its purpose is to answer four questions clearly:

1. which outputs exist;
2. what each output is for;
3. which output is the main product deliverable;
4. which outputs are technical support, annexes, or legacy artifacts.

## Core Rule

TCRIA has one primary product output.

That output is the client-facing compliance review report.

Everything else exists to support, explain, validate, archive, or operationalize that report.

## Output Classes

### 1. Primary Output

This is the main product deliverable.

`Client-facing compliance review report`

Purpose:

- explain the compliance result clearly;
- show the main findings early;
- connect findings to evidence;
- expose limits and next review priorities.

Typical formats:

- PDF;
- HTML;
- formatted Markdown when used as report source or lightweight delivery.

Audience:

- client;
- business operator;
- compliance reviewer;
- decision-maker consuming the result.

Rule:

This is the output that defines whether the product feels complete or incomplete.

### 2. Supporting Production Outputs

These outputs are part of the delivery pipeline but are not the main client-facing artifact by themselves.

#### Structured report source

Examples:

- report Markdown;
- structured report JSON;
- normalized report payload used for rendering.

Purpose:

- preserve structured content before final render;
- support reproducible PDF or HTML generation;
- make report generation testable and versionable.

Audience:

- system;
- developer;
- internal operator.

Rule:

These outputs support the main report. They should not replace the formatted report in the normal client experience.

### 3. Technical Annexes

These outputs add traceability and depth without replacing the main report.

Examples:

- evidence register;
- detailed finding appendix;
- document inventory;
- rule reference appendix;
- extraction or traceability notes when attached intentionally.

Purpose:

- support deeper review;
- preserve auditability;
- give technical backup to the conclusions.

Audience:

- compliance analyst;
- auditor;
- internal reviewer;
- advanced client reader when needed.

Rule:

Technical annexes may accompany the main report, but they must not push the client into technical material before the main result is understood.

### 4. Operational And Validation Outputs

These outputs are for system operation, debugging, validation, and internal quality control.

Examples:

- runtime telemetry;
- render validation output;
- debug traces;
- intermediate generation files;
- preview images used to inspect PDFs.

Purpose:

- verify quality;
- diagnose failures;
- support development and maintenance.

Audience:

- developer;
- maintainer;
- internal operations.

Rule:

These are not client-facing deliverables and should not be presented as product output.

### 5. Legacy Outputs

These are outputs inherited from earlier versions of the project.

Examples may include:

- older audit dumps;
- gate-ledger style reports;
- historical governance outputs;
- earlier report formats from TCR or legacy TCRIA runs.

Purpose:

- preserve historical work;
- support migration and comparison;
- help identify what should be reused or retired.

Audience:

- internal project team;
- migration work.

Rule:

Legacy outputs should not define the current product promise. They are reference material, not the current standard.

## Official Output Hierarchy

The intended hierarchy is:

1. main report;
2. optional annexes;
3. supporting structured source;
4. operational validation artifacts;
5. legacy artifacts.

If this order gets inverted, the product starts feeling like a tool dump again.

## Output Workflow

The output workflow for the current MVP should be:

1. analyze the bounded document batch;
2. produce structured findings and evidence links;
3. assemble the normalized report source;
4. render the client-facing compliance review report;
5. attach technical annexes when needed;
6. keep operational and validation artifacts separate from client delivery;
7. preserve legacy outputs outside the primary delivery path.

## Delivery Rule

Normal delivery should begin with the main report.

Annexes may be attached.

Technical support outputs may be stored.

Operational artifacts may be retained internally.

Legacy outputs may be archived.

But only the main report should represent the product by default.

## Repository Guidance

When creating or naming an output artifact, classify it explicitly as one of:

- primary;
- supporting production;
- technical annex;
- operational or validation;
- legacy.

If the artifact cannot be classified, its purpose is still unclear and should be defined before it spreads through the repository.
