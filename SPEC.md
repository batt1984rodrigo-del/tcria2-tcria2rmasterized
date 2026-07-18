# TCRIA Deployment Application

## Value Proposition

TCRIA helps compliance, audit and document-decision professionals review a bounded document batch without losing the connection between evidence, findings and the recommended decision.

The deployed application must make file intake and processing a primary product capability. The user must not need to prepare a server-side folder or invoke scripts manually.

### Core actions

1. Upload multiple documents as one bounded review batch.
2. State the review or decision question in natural language.
3. Run the existing TCRIA pipeline and download the resulting report.

## Why an LLM?

### Conversational advantage

The user can state the decision they need to make in natural language, for example:

> Based on the submitted documents, should this supplier be approved, approved with conditions, or held for further review?

This is more direct than requiring the user to translate the decision into technical filters or pipeline parameters.

### What the LLM contributes

- interprets the review question;
- relates evidence across documents;
- identifies gaps and inconsistencies;
- organizes compliance findings;
- drafts an evidence-linked, structured recommendation;
- distinguishes confirmed facts, verification signals and limitations.

### What the LLM does not provide

- documents or evidence that are absent from the submitted batch;
- direct text extraction or OCR by itself;
- authority to issue the final legal, compliance, audit, management or institutional decision;
- permission to turn isolated keywords into claims of fraud, guilt or wrongdoing.

The document pipeline remains responsible for controlled intake, extraction, OCR provenance and evidence organization. The model reasons over that auditable base.

## User Experience

### First view

The first screen presents a concise description of TCRIA, a field for the review question and a drag-and-drop or file-picker area that accepts multiple files.

### Intake validation

Before processing starts, the application shows:

- the received documents;
- detected formats and sizes;
- rejected files and the reason for rejection;
- the configured batch limits.

The user can correct the batch before starting the analysis.

### Processing

The application exposes progress through these stages:

1. receiving and validating the batch;
2. direct document reading and OCR fallback;
3. evidence organization and cross-document correlation;
4. compliance analysis;
5. report generation.

The browser must not need to remain responsible for the processing lifecycle. Each analysis runs as an isolated job with a queryable status.

### Result

The result view presents:

- the recommended decision and rationale;
- confirmed facts;
- gaps, inconsistencies and unresolved points;
- compliance risks and verification signals;
- evidence references;
- reading and OCR limitations;
- required human validation.

The user can download the complete HTML/PDF report and the technical JSON result, then start a new analysis.

## Product and Technical Context

### Source of truth

This repository and its existing Python document pipeline are the product source of truth. The application layer must invoke that pipeline rather than duplicate its analysis rules.

### Application boundary

- A web frontend collects the review question and document batch.
- A backend validates uploads, creates the isolated analysis job and invokes the Python pipeline.
- Sensitive processing and secrets remain on the backend.
- Heavy or long-running processing may be moved to a worker without changing the user-facing contract.

### Authentication

The initial private pilot uses simple credential protection. Individual user accounts and organization-level authorization are deferred beyond the MVP.

### Accepted inputs

The initial application accepts:

- PDF;
- DOCX;
- TXT;
- Markdown;
- ZIP containing supported documents.

The MVP supports at most 20 files and 100 MB per batch.

### Upload safety

The backend must:

- validate size and permitted type rather than trusting only the browser or filename;
- normalize unsafe filenames;
- reject executables and unsupported archive members;
- reject symbolic links and absolute or parent-traversal archive paths;
- extract ZIP contents into an analysis-specific temporary directory;
- prevent one analysis from reading another analysis's files;
- avoid committing uploaded material or generated private reports to the repository.

### Retention

Uploaded files and generated private results are temporary and are automatically deleted after 24 hours. A future deployment may make this period configurable, but the pilot must communicate the active retention policy to the user.

### Outputs

Each successful analysis produces:

- a client-facing HTML/PDF compliance review report;
- a structured JSON result for traceability and technical inspection.

Material conclusions must remain evidence-linked or explicitly unresolved. Reading method, OCR status and reading confidence must remain visible when available.

### Secrets

Model credentials and deployment secrets must be provided through backend environment configuration or the deployment platform's secret store. They must never be embedded in frontend code, committed files or browser-visible responses.

## MVP Success Criteria

The MVP is successful when a permitted pilot user can:

1. open the deployed application;
2. authenticate with the pilot credential;
3. submit a review question and a valid multi-file batch;
4. see clear validation feedback for invalid input;
5. start one isolated analysis job;
6. follow its processing status;
7. receive an evidence-linked recommendation with limitations;
8. download the generated report and JSON result;
9. rely on automatic deletion of temporary material after 24 hours.

## UX Flow

Analyze one bounded document batch:

1. State the review question.
2. Select or drag multiple files.
3. Validate the batch and correct rejected files.
4. Start processing.
5. Follow direct reading, OCR, correlation, analysis and report generation.
6. Review the recommendation, evidence, gaps and limitations.
7. Download the PDF/HTML report and JSON result.

This is one product flow. Upload, processing and reporting must not be split into unrelated applications.

## Application Architecture

### Primary view: `analyze_document_batch`

The primary full-screen view owns file selection, intake feedback, processing progress and result presentation. It may receive a suggested review question from the conversation, but document analysis never runs only in the browser.

### Backend operations

**`create_analysis`**

- Input: review question and multipart document files.
- Output: analysis identifier, accepted/rejected file information and initial status.
- Behavior: validates the batch, safely expands supported ZIPs, creates an isolated job and starts the existing pipeline.

**`get_analysis_status`**

- Input: analysis identifier.
- Output: current stage, progress, safe warnings and safe error information.

**`get_analysis_result`**

- Input: analysis identifier.
- Output: structured recommendation, facts, gaps, risks, evidence, reading/OCR provenance and limitations.

**`download_analysis_artifact`**

- Input: analysis identifier and `pdf`, `html` or `json` artifact format.
- Output: the requested generated artifact when it belongs to the valid analysis.

### Job lifecycle

- Each analysis uses a private temporary directory and manifest.
- Processing runs independently of the browser connection.
- The first MVP may use local temporary storage and an in-process executor behind stable operation boundaries.
- Long-running or horizontally scaled deployment can replace that executor with a queue and worker without changing the user-facing contract.
- Expired jobs and artifacts are removed after 24 hours.

### Deployment requirements

- Deploy frontend and backend together for the first pilot.
- Provide temporary writable storage for analysis jobs.
- Install Poppler and Tesseract with Portuguese language support.
- Store credentials only in the backend environment or deployment secret store.
- Expose a lightweight health check that verifies application availability without running a document analysis.

## Non-Goals for the Initial Deployment

- scanning an entire company, device, drive or network;
- silently ingesting files outside the user-submitted batch;
- issuing the final institutional or legal decision;
- making accusations from isolated keywords;
- permanent document management;
- organization administration, billing or multi-tenant account management;
- replacing the existing TCRIA pipeline with unrelated application logic.
