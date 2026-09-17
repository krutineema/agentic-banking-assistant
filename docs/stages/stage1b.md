# Stage 1B — SQLite and Repository Boundary

> **Milestone status:** Complete  
> **Recommended Git tag:** `stage-1b`  
> **Previous snapshot:** `stage-1a`  
> **Next milestone:** Stage 2 — LLM tool calling / first agent

## Purpose

Stage 1B changes persistence without changing the assistant's behavioural model.

Primary question:

> **Can relational persistence be introduced without forcing the deterministic workflows and UX to know about SQL?**

## Architectural change

Stage 1A:

```text
Workflow
  ↓
BankingService
  ↓
JSON
```

Stage 1B:

```text
Workflow
  ↓
BankingService
  ↓
BankingRepository
  ↓
SQLite
```

Authentication follows the same pattern:

```text
AuthService
  ↓
CustomerRepository
  ↓
SQLite
```

## What was added

- SQLite schema for customers, accounts and transactions;
- idempotent seed SQL for the two existing demo customers;
- `Database` connection/bootstrap boundary;
- `CustomerRepository`;
- `BankingRepository`;
- repository-level SQL aggregation for debit totals;
- foreign keys and useful indexes;
- integer-pence storage for monetary values;
- tests for schema creation, seeding, repositories and customer isolation;
- ADR documenting the persistence decision.

## What deliberately did not change

- login UX and session semantics;
- `customer_id` still comes from trusted session context;
- API request shapes;
- deterministic intent router;
- assistant workflow selection;
- supported Stage 1 banking questions;
- transfers remain unsupported;
- there is still no LLM.

That lack of change above the service boundary is the main success criterion of this milestone.

## Customer isolation in SQL

A transaction query does not first load all transactions and filter them in Python. It joins through the owned account:

```text
transactions
    JOIN accounts
        ON accounts.account_id = transactions.account_id
    WHERE accounts.customer_id = authenticated_customer
```

This means knowing another customer's account ID is insufficient to retrieve that account's transactions through the repository.

## Database lifecycle

The repository versions:

```text
app/database/schema.sql
app/database/seed.sql
```

The local SQLite file is generated at runtime under `app/data/banking.db` and is ignored by Git. Initialization is idempotent, so restarting the local app does not duplicate seed records.

## Why SQLite

SQLite provides the relational concepts required for the learning path — tables, keys, joins, indexes, aggregation and SQL — without introducing Docker/database-server operations into a phase whose learning goal is the persistence boundary.

It is not presented as a production banking database choice.

## Money representation

Stage 1B stores balances and transaction amounts as integer pence (`balance_pence`, `amount_pence`) rather than SQLite floating-point values. Repositories convert these values to Python `Decimal` objects before returning domain models.

This avoids making floating-point rounding part of the banking-data model and creates a cleaner basis for later SQL analytics.

## Tests that matter most

- both customers are seeded;
- schema initialization is idempotent;
- authentication reads customer records from SQLite;
- `cust-001` cannot query an account owned by `cust-002`;
- transaction queries preserve ownership boundaries;
- August restaurant spending still produces different results for Alex and Sam;
- existing assistant/API behavior remains intact.

## Learning takeaway

The repository layer is not merely another folder. It creates a replaceable persistence adapter beneath application services:

```text
Assistant/business behavior
         │
         ▼
application service contract
         │
         ▼
repository implementation
         │
         ▼
persistence technology
```

That same boundary becomes important later when controlled Text-to-SQL is introduced: normal application operations continue through known services/repositories, while analytical SQL uses a separate read-only policy-controlled path.

## No experiment folder yet

Stage 1B is a refactor of persistence rather than a competition between two application architectures. The `stage-1a` Git tag already preserves the JSON version if it needs to be inspected.

The first focused comparison experiment is created in Stage 2, when deterministic routing and LLM tool selection both exist.
