# Legacy Audit Summary

## Executive Summary

This report translates a legacy TCRIA audit payload into a reader-oriented summary. The most visible issue in the reviewed batch is: High-value amendment found without strong approval support in the reviewed batch.

## Batch Snapshot

- Generated at: `2026-04-23T11:25:36`
- Legacy mode: `strict-explicit-decision-record`
- Total files scanned: `4`
- Files read: `3`
- Files not read: `1`
- Files blocked: `1`
- Files partially read: `2`

## Main Findings

### Finding 1: contract-amendment-17.pdf

- Legacy status: `BLOCKED (complianceGate)`

High-value amendment found without strong approval support in the reviewed batch.

Reasons carried from the legacy payload:

- Missing approval support
- High-value contract change
- Traceability expectation not fully satisfied

### Finding 2: vendor-boarding-form.pdf

- Legacy status: `PARTIAL_PASS (traceability warning; static audit)`

Vendor file contains a declared review record but only partial due diligence support.

Reasons carried from the legacy payload:

- Supporting approval record present
- Due diligence evidence incomplete
- Traceability signals limited

### Finding 3: scanned-exception-request.pdf

- Legacy status: `UNREADABLE`

The file could not be read reliably from the submitted batch.

Reasons carried from the legacy payload:

- Unreadable scan
- Insufficient extraction quality

### Finding 4: vendor-checklist-register.csv

- Legacy status: `PASS`

Register contains evidence of required checklist controls for multiple suppliers.

Reasons carried from the legacy payload:

- Supporting evidence markers identified
- Document role suggests supporting proof

## Evidence Highlights

### Evidence 1: vendor-boarding-form.pdf

- Classification: `ACCUSATORY_CANDIDATE`
- Signal summary: `checklist=1`

Vendor file contains a declared review record but only partial due diligence support.

### Evidence 2: vendor-checklist-register.csv

- Classification: `SUPPORTING_EVIDENCE_RELEVANT`
- Signal summary: `checklist=5, supplier id=8`

Register contains evidence of required checklist controls for multiple suppliers.

## Limits And Translation Notes

- 1 file(s) could not be read reliably from the legacy batch.
- 2 file(s) were read with only low or medium extraction quality.
- Some legacy items do not expose gate details in a consistent way.
- This adapted report summarizes a legacy payload and does not re-run the original engine.

## Legacy Counters

- Classification counts: `{'ACCUSATORY_CANDIDATE': 2, 'SUPPORTING_EVIDENCE_RELEVANT': 1, 'UNREADABLE': 1}`
- Route counts: `{'CIVIL_CRIMINAL_INVESTIGATIVE': 2, 'EVIDENTIARY_SUPPORT_GENERAL': 1, 'UNDETERMINED': 1}`
