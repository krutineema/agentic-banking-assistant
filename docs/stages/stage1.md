# Stage 1A — Customer-Scoped Deterministic Workflow Baseline

> **Milestone status:** Complete  
> **Recommended Git tag:** `stage-1a`  
> **Next milestone:** Stage 1B — SQLite + repository/data-access boundary

## Purpose of this stage

Stage 1A establishes the non-agentic baseline for the Personal Banking Assistant.

The primary learning question was:

> **Which banking-assistant behaviours can be implemented cleanly with ordinary deterministic application logic before an LLM agent is introduced?**

The stage also establishes customer identity and data isolation from the beginning so later AI capabilities inherit the correct security boundary rather than adding it retrospectively.

---

## What was built

Stage 1A contains:

- FastAPI backend;
- banking-style browser UX;
- login with known synthetic users;
- salted PBKDF2 password hashes;
- opaque server-side sessions referenced through an HttpOnly cookie;
- customer-specific accounts and transactions;
- backend-enforced customer isolation;
- deterministic keyword intent routing;
- account-balance workflow;
- recent-transactions workflow;
- spending-summary workflow;
- safe execution trace shown in the UI;
- automated tests including cross-customer access checks.

No LLM, agent framework, tool-calling model, RAG pipeline or database is used yet.

---

## Stage 1A runtime architecture

```text
                         Browser / app.js
                                │
                             HTTP API
                                │
                           ┌────▼─────┐
                           │ routes.py│
                           └────┬─────┘
                                │
                      protected request?
                                │
                                ▼
                         require_customer
                                │
                         SessionService
                                │
                      AuthenticatedCustomer
                         /              \
                        /                \
               dashboard APIs        assistant API
                    │                     │
                    ▼                     ▼
            BankingService        AssistantWorkflow
                                        │
                                  IntentRouter
                                        │
                                 selected workflow
                                        │
                                        ▼
                                 BankingService
                                        │
                                        ▼
                              customer-scoped JSON data
```

Login is a separate path:

```text
login request
     │
     ▼
 AuthService ───────→ customers.json
     │
     ▼
SessionService
     │
     ▼
HttpOnly session cookie
```

### Important detail: `main.py` is not a business workflow step

`main.py` is the application bootstrap/composition root. It creates the FastAPI app, attaches the API routes and mounts static assets. Browser requests are handled by the routes exposed by the application rather than `main.py` acting as a controller itself.

---

## Main code responsibilities

### `app/main.py`

Application bootstrap / composition root.

Responsibilities include:

- create the FastAPI application;
- attach API routes;
- mount static assets;
- expose application-level endpoints such as health checks.

### `app/api/routes.py`

FastAPI controller/router layer.

It exposes the HTTP interface for:

- login;
- logout;
- current session;
- accounts;
- transactions;
- assistant messages.

Protected endpoints resolve the authenticated customer before accessing banking data.

### `app/services/auth_service.py`

Validates username/password credentials for the synthetic customers.

Passwords are not stored in plaintext; the demo uses salted PBKDF2 hashes.

### `app/services/session_service.py`

Maintains a small server-side in-memory session map.

The browser receives an opaque random session token in an HttpOnly cookie. The customer identity remains server-side.

### `app/services/banking_service.py`

Provides the banking-data capability used by both ordinary dashboard APIs and assistant workflows.

Every public data operation is customer scoped.

Conceptually:

```text
get_accounts(customer_id)
get_account(customer_id, account_id)
get_transactions(customer_id, ...)
debit_total(customer_id, ...)
```

The caller cannot retrieve another customer's account simply by knowing its ID.

### `app/core/router.py`

Performs deterministic natural-language-to-intent mapping.

For example:

```text
"How much did I spend eating out in August?"
                    ↓
             spending_summary
```

The router deliberately uses simple keyword rules. Its limitations become useful evidence when Stage 2 introduces LLM-based tool selection.

### `app/workflows/assistant_workflow.py`

Maps the intent to the deterministic workflow implementation.

```text
intent
  ↓
account_balance       → AccountBalanceWorkflow
recent_transactions   → RecentTransactionsWorkflow
spending_summary      → SpendingSummaryWorkflow
```

This separation is important:

```text
router.py
text → intent

assistant_workflow.py
intent → workflow
```

### Individual workflows

The workflow modules contain the fixed application steps for known request types.

For example, spending analysis resolves:

```text
"eating out" → restaurants
"August"     → 2026-08-01 .. 2026-08-31
```

then asks `BankingService` for the customer's matching transactions and performs a deterministic aggregation.

### `app/static/`

Contains the small banking-style UX:

- login screen;
- account overview;
- recent transactions;
- assistant conversation panel;
- execution trace.

The browser does not contain the banking business rules and does not decide which customer data it is entitled to access.

---

## Customer-session and isolation design

Customer identity is established before assistant reasoning or banking-data access.

```text
credentials
    ↓
authentication
    ↓
server-side session
    ↓
authenticated customer_id
    ↓
workflow / banking service
```

The browser never supplies `customer_id` as an authority signal.

This is intentionally established in Stage 1 because the same trusted identity context must later flow into:

- LLM tool execution;
- RAG access decisions;
- Text-to-SQL query policy;
- transfer preparation and execution;
- traces and audit events;
- any future multi-agent hand-off.

The model must never be responsible for selecting the customer identity.

---

## Synthetic persistence

Current persistence is intentionally simple:

```text
customers.json
accounts.json
transactions.json
```

JSON was sufficient for the Stage 1 learning question because the workflows interact through service boundaries rather than depending directly on a particular storage technology.

The architecture therefore currently looks like:

```text
Workflow
   ↓
BankingService
   ↓
JSON
```

This is temporary. Stage 1B will test whether persistence can be changed without materially changing the workflow layer.

---

## Supported assistant requests

Examples include:

```text
What are my balances?
Show my recent transactions
How much did I spend in August?
How much did I spend eating out in August?
How much did I spend on groceries last month?
```

These requests have known paths and do not require agent autonomy.

---

## Deliberately unsupported in Stage 1A

The following are intentionally absent:

- LLM calls;
- tool/function calling by a model;
- free-form agent planning;
- conversational task memory;
- transfer execution;
- human-in-the-loop approvals;
- RAG;
- Text-to-SQL;
- MCP;
- LangGraph;
- multi-agent orchestration;
- relational database persistence.

A request such as:

```text
Transfer £100 to savings
```

is rejected rather than pretending that a high-risk write operation belongs in the Stage 1 design.

---

## What Stage 1A demonstrates

### 1. Not every assistant request needs an agent

Balance lookup, recent transactions and constrained spending summaries can be expressed as explicit, testable application workflows.

The existence of a natural-language UI does not itself imply that the backend must be agentic.

### 2. Authentication and AI orchestration are separate concerns

Customer identity is established by the application/session layer, not inferred by the assistant.

This boundary should remain true when an LLM is introduced.

### 3. The assistant is a consumer of banking capabilities

Both the ordinary banking UX and the assistant use the same banking service boundary.

```text
Traditional UX ───────┐
                      ├── BankingService → data
Assistant workflow ───┘
```

The AI layer does not become the banking system itself.

### 4. Persistence can be hidden behind an application boundary

The workflow does not need to know whether banking data comes from JSON, SQLite or a remote API.

This is the architectural hypothesis that Stage 1B will test.

### 5. Simple routing is transparent but brittle

Keyword routing is easy to understand and test, but it only supports the language patterns explicitly anticipated in code.

Stage 2 will give an LLM controlled banking tools and compare model-based tool selection against this deterministic baseline.

---

## Testing focus

Stage 1A tests cover:

- correct deterministic intent routing;
- supported workflow results;
- unsupported transfer requests;
- authentication requirement for protected endpoints;
- invalid credential rejection;
- session creation;
- logout/session invalidation;
- user-specific account and transaction results;
- different answers for different authenticated customers;
- blocked cross-customer account access.

The important security assertion is not simply that the UI displays the right customer. The backend must refuse to return another customer's data.

---

## Known limitations

The Stage 1 authentication/session implementation is deliberately educational rather than production-ready:

- sessions are stored only in memory;
- sessions disappear when the local application restarts;
- no MFA;
- no lockout/rate-limiting policy;
- no password-reset workflow;
- no external identity provider;
- local HTTP means the demo cookie is not marked `Secure`;
- banking persistence is JSON rather than a relational database.

These limitations do not undermine the Stage 1 learning objective because the architectural identity and customer-isolation boundaries are already explicit.

---

## Experiments at this milestone

There is **no `experiments/` folder yet**, intentionally.

Stage 1A gives us one baseline implementation. A comparison experiment is meaningful only after another approach exists.

The first formal experiment is planned for Stage 2:

```text
Stage 1 deterministic workflows
            vs
Stage 2 LLM tool selection
```

At that point `experiments/workflow-vs-agent/` can hold scenarios, measurements and findings while the original full Stage 1 application remains available through Git tag `stage-1a`.

Later comparison experiments are expected around:

- controlled APIs vs Text-to-SQL;
- direct tools vs MCP;
- hand-written orchestration vs LangGraph;
- single-agent vs multi-agent architecture.

---

## Milestone preservation

This project uses Git tags rather than copied stage source trees.

Before beginning Stage 1B:

```bash
git add .
git commit -m "Complete Stage 1A deterministic banking baseline"
git tag -a stage-1a -m "Stage 1A - customer-scoped deterministic workflow baseline"
git push origin main
git push origin stage-1a
```

The responsibilities are intentionally separate:

```text
Git tag stage-1a
    → exact runnable Stage 1A code snapshot

docs/stages/stage1.md
    → what Stage 1A built and taught us

DEVELOPMENT_PHASES.md
    → forward-looking project architecture and roadmap
```

---

## What changes in Stage 1B

Stage 1B replaces temporary JSON persistence with a local relational database.

Target change:

```text
Before
BankingService → JSON

After
BankingService → Repository → SQLite
```

The important test is that the layers above this boundary should change very little:

```text
UX
API
Authentication/session boundary
AssistantWorkflow
IntentRouter
Deterministic workflows
```

should continue to behave as they did in Stage 1A.

Stage 1B will therefore teach a different lesson from Stage 1A: **persistence and data-access architecture**, not agent behaviour.
