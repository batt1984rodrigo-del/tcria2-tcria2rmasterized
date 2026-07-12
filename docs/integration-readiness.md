# Integration Readiness

This document defines how the remodeled TCRIA should enter this repository.

The current instruction is:

`prepare the terrain first, wait for the files, integrate only after review`

## Current Position

The repository is prepared to receive remodeled TCRIA material, but it should not absorb that material blindly.

Incoming files must be reviewed before they are moved into the product structure.

## Integration Boundary

Before the files arrive:

- define product scope;
- define output rules;
- define governance profiles;
- define contribution and CI basics;
- define a controlled intake area.

After the files arrive:

- inventory the material;
- identify what is core;
- identify what is report rendering;
- identify what is legacy;
- identify what should stay outside the new repository history.

## Intake Workflow

1. place incoming files in `incoming/`;
2. inspect structure and file types;
3. map each file to one of these destinations:
   - `docs/`
   - `scripts/`
   - future product code path
   - `output/` example material
   - archive or legacy reference
4. integrate only what matches the current product direction.

## Non-Goals During Intake

- do not rename everything immediately;
- do not rewrite history before classification;
- do not merge mixed legacy output directly into current product paths;
- do not commit sensitive or private material into the public repository.

## Decision Rule

A file should enter the active repository structure only if at least one of these is true:

- it directly supports the current compliance review product;
- it helps render or validate the new client-facing report;
- it documents a rule, profile, or workflow still active in the remodeled system;
- it is a reusable part of the future core.

If none of those are true, the file is likely:

- legacy;
- temporary;
- private;
- or outside current scope.

## Prepared Ground

At this point, the repository already has:

- product definition;
- output taxonomy;
- report contract;
- report template;
- governance profiles;
- basic CI check;
- controlled intake area.

That is enough preparation to receive the remodeled TCRIA files without rushing integration.
