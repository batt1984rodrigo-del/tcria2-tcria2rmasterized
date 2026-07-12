# Contributing

This repository should be changed in a controlled way.

The goal is not to stop progress.

The goal is to keep changes understandable, reviewable, and reversible.

## Repository Workflow

### `main` is the landing strip

Treat `main` as the stable line.

Do not use it as a place for unreviewed experiments, mixed-topic changes, or unclear repository state.

### Branches are the workbench

For focused work, prefer a dedicated branch.

Examples:

- `docs/output-taxonomy`
- `docs/governance-profiles`
- `ci/basic-check`
- `reports/template-renderer`

### Commits are clean snapshots

Each commit should answer two questions clearly:

1. what changed;
2. why it changed.

Good:

- `Add output taxonomy and delivery workflow`
- `Add governance profiles documentation`
- `Add basic CI check for report rendering`

Bad:

- `update stuff`
- `misc changes`
- `fix repo`

### Pull requests are review gates

When possible, prefer:

1. create branch;
2. make focused change;
3. commit with one theme;
4. push branch;
5. open pull request;
6. review before merge.

## Sensitive Data Rule

This repository is public.

Never commit:

- `.env` files;
- API keys;
- client secrets;
- private company records;
- legal or banking documents with real sensitive data;
- any real confidential evidence package.

Use synthetic or sanitized examples for public artifacts.

## CI Rule

GitHub Actions is used as a basic control layer.

Its first job is not deployment.

Its first job is to verify that the repository still performs the minimum expected behavior without breaking.

For this repository, the first useful check is:

- install dependencies;
- render the example report;
- fail if report rendering breaks.

## Current Practical Rule

Until the repository grows further, prefer small, themed changes over large mixed updates.

One change set should normally cover one of these areas only:

- product docs;
- output docs;
- report template;
- CI;
- rendering code.
