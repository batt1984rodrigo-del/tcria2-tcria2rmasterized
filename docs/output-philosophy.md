# Output Specification

This document defines the required compliance report output for TCRIA.

For the MVP, the product has one main deliverable: a structured compliance review report for a bounded document batch.

The report must be formatted for client understanding, not only for technical completeness.

See also: [Report Contract](report-contract.md)

## Required Sections

The structured compliance review report should contain, at minimum:

- formatted client-facing presentation;
- analysis scope;
- applied review rules or policy;
- compliance findings summary;
- evidence references;
- graded compliance risk or severity result;
- unresolved items or limits;
- recommended next actions.

## Required Questions

Every substantial output should answer:

1. What was analyzed?
2. What was found?
3. Which rule or policy was used?
4. Which evidence supports the result?
5. What could not be determined?
6. What should be reviewed next?
7. Where are the main conformity gaps?

If these questions are not answered, the output is incomplete.

## Output Format Standard

The report should be readable, structured, and consistent across runs of the same workflow.

It should not resemble a raw log unless the output is explicitly a debug or trace artifact.

It should be formatted so that the main compliance situation is understandable from the opening section.

## Suggested Report Structure

- executive summary;
- analysis scope;
- applied rules or policy;
- key findings and classifications;
- supporting evidence;
- limitations;
- recommended next steps;
- annexes or supporting details.

## Output Composition Layer

The system should include a dedicated layer responsible for composing the compliance review report from analysis results.

That layer should:

- arrange findings consistently;
- attach evidence references;
- state the applied rules;
- apply report structure and visual hierarchy;
- expose uncertainty or missing data;
- generate report-ready artifacts.

## Failure Condition

The output layer fails when the system produces information that is technically present but operationally unusable.
