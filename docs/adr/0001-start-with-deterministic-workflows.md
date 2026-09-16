# ADR 0001 — Start with deterministic workflows before introducing an agent

- **Status:** Accepted
- **Stage:** 1

## Context

The target product will eventually demonstrate agentic patterns, but several initial banking use cases have known inputs, known data sources and predictable steps. Introducing model autonomy immediately would make it harder to distinguish where agent behaviour creates value from where it only creates variability.

## Decision

Stage 1 uses:

- explicit intent routing;
- fixed workflow classes;
- a banking service abstraction;
- read-only synthetic data;
- no LLM or agent framework.

## Consequences

### Positive

- easy to understand and test;
- creates a behavioural baseline;
- exposes which tasks are naturally deterministic;
- keeps risky banking actions out of scope while foundations are built.

### Negative

- brittle natural-language routing;
- limited supported phrasing;
- no dynamic tool selection;
- no multi-step autonomy.

These limitations are intentional and will become comparison points in Stage 2.
