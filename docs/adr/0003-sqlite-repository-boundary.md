# ADR 0003 — Introduce SQLite behind a repository boundary

- **Status:** Accepted
- **Stage:** 1B

## Context

Stage 1A used JSON as temporary persistence. Future phases need realistic relational relationships, controlled SQL access, joins and a database suitable for later Text-to-SQL experiments. At the same time, persistence concerns should not leak into assistant workflows or API routes.

## Decision

Replace runtime JSON persistence with SQLite and introduce explicit repositories:

```text
Workflow / API
     ↓
BankingService / AuthService
     ↓
Repository
     ↓
SQLite
```

- `CustomerRepository` owns customer-record reads used by authentication.
- `BankingRepository` owns account, transaction and aggregate SQL.
- Customer ownership is enforced inside SQL queries.
- Services expose the same application-oriented interface to their callers.
- Money is stored as integer pence rather than floating-point values.
- The generated local `.db` file is ignored by Git; schema and seed SQL are version controlled.

## Consequences

### Positive

- workflows remain persistence-agnostic;
- relational constraints and foreign keys model banking relationships explicitly;
- customer isolation moves closer to the data-access boundary;
- the database is ready for later read-only Text-to-SQL experiments;
- repository classes can be replaced or tested independently.

### Negative / intentionally deferred

- SQLite is a local learning database, not representative of production bank infrastructure;
- no migration framework is introduced yet;
- sessions are still in memory;
- there are still no write banking operations.
