# Legacy Output Lessons

This document records the main lessons learned from legacy TCRIA outputs.

It exists to preserve what the old system did well while making explicit what needs to change in the remodeled repository.

## What The Legacy Output Already Did Well

- processed large document batches;
- preserved structured classifications;
- exposed gate results and outcome states;
- retained traceability-rich technical detail;
- separated accusation-oriented and non-accusation-oriented material.
- captured useful compliance-facing signals even when the final reading experience was weak.

The legacy system was not empty or weak.

Its main problem was not lack of processing.

Its main problem was how the result arrived to the reader.

## Main Legacy Problems

### 1. Too much machine sequence, not enough reader sequence

The legacy output often presented technical fields in the order the system produced them.

That made the result feel like a system dump instead of a review document.

### 2. Important findings were buried

Blocked items, weak support, unreadable files, and traceability warnings often appeared as repeated per-file structures without strong prioritization.

The reader had to work too hard to understand what mattered most.

### 3. Technical richness was not translated

The old output captured many useful signals:

- overall outcome;
- gate statuses;
- extraction quality;
- classification reasons;
- evidence markers;
- interpretation layers.

But those signals were not consistently translated into a client-facing explanation.

### 4. Compliance coverage was present, but not clearly framed

The product direction is compliance-oriented.

That means the first reader question is usually not "what did the engine run?"

It is:

"How much of the batch was actually usable, what was blocked, and where are the gaps?"

The legacy output often had the raw ingredients for that answer, but not the formatted response itself.

### 5. The system organized, but did not sufficiently show that it organized

This is the central lesson.

The engine often knew more than the reader could quickly perceive from the report.

## What Must Be Preserved

- structured result fields from the legacy engine;
- gate status information;
- evidence relationships;
- traceability cues;
- operational counts;
- route and classification information when still useful.

## What Must Change

- the primary output must become reader-first;
- the primary output must become compliance-coverage-first;
- the first page must explain the batch condition quickly;
- technical details must move into annexes or supporting sections;
- the legacy result must be normalized before presentation;
- the remodeled system must translate old output instead of exposing it raw.

## Practical Translation Rule

The remodeled repository should treat legacy output as:

`legacy JSON -> normalizer -> human coverage report`

It should not treat legacy output as:

`legacy JSON -> direct client delivery`

## Why The Adapter Is The Right First Step

The legacy adapter is the safest entry path because it:

- preserves the old engine;
- avoids dumping legacy code into the new repository structure;
- solves the most visible product defect first;
- creates immediate value through improved presentation.
- gives the compliance product a clear migration bridge without pretending to replace the final executive report.

## Repository Guidance

Whenever a legacy output field is carried forward, ask:

1. is it useful to the client-facing report;
2. is it useful only as technical support;
3. should it remain internal or legacy-only.

If a field cannot answer one of those questions, it should not control the new report structure.
