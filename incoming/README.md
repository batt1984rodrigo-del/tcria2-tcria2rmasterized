# Incoming Area

This folder is the controlled landing area for files from the remodeled TCRIA.

Purpose:

- receive incoming material without mixing it immediately into the product structure;
- allow inventory and review before integration;
- protect the repository from accidental direct merges of legacy or mixed material.

## Rule

Files may arrive here first.

They should not be treated as already integrated product code or product documentation.

## Expected Workflow

1. place incoming files here;
2. inventory what arrived;
3. classify each item as:
   - reusable core logic;
   - report or output logic;
   - product-facing material;
   - legacy artifact;
   - discard or archive candidate;
4. decide destination only after review.

## Important

This folder is ignored by git except for this guide file.

That means incoming material can be inspected safely before we decide what belongs in the public repository history.
